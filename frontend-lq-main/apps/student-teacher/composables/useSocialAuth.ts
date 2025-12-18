import { ref } from "vue";
import { useAuthStore } from "@lq/stores";
import { useToast } from "primevue/usetoast";
import { useAuthNavigation } from "./useAuthNavigation";

type SocialProvider = "google" | "microsoft";

interface SocialAuthConfig {
  id: string;
  name: string;
  client_id?: string;
  flows: string[];
}

/**
 * Composable for handling social authentication (Google & Microsoft)
 * Manages OAuth flows, token exchange, and user session setup
 */
export function useSocialAuth() {
  const { $allauth } = useNuxtApp();
  const authStore = useAuthStore();
  const toast = useToast();
  const { handlePostLogin } = useAuthNavigation();
  const loading = ref(false);

  /**
   * Get provider configuration from allauth
   */
  const getProviderConfig = async (providerId: string): Promise<SocialAuthConfig> => {
    const providers = await $allauth.getSocialProviders();
    const provider = providers.find((p) => p.id === providerId);

    if (!provider?.client_id) {
      throw new Error(`${providerId} client ID not configured in allauth`);
    }

    return provider;
  };

  /**
   * Handle successful authentication response
   * Uses the same post-login flow as email login
   */
  const handleAuthSuccess = async (
    providerName: string,
    authResponse: { meta?: { is_authenticated?: boolean; access_token?: string }; data?: unknown },
  ) => {
    if (!authResponse.meta?.is_authenticated) {
      throw new Error("Authentication failed");
    }

    // Store tokens
    if (authResponse.meta?.access_token) {
      localStorage.setItem("auth_token", authResponse.meta.access_token);
    }

    // Update auth store
    const userData = authResponse.data as { user?: unknown };
    if (userData?.user) {
      authStore.userAuth = userData.user as typeof authStore.userAuth;
    }

    // Use the same post-login navigation flow as email login
    // This handles onboarding checks, email verification, and role-based redirects
    await handlePostLogin({ success: true });
  };

  /**
   * Handle Google OAuth authentication
   * Uses implicit flow with popup to get both access_token and id_token
   */
  const loginWithGoogle = async (): Promise<void> => {
    const provider = await getProviderConfig("google");
    const redirectUri = encodeURIComponent(window.location.origin + "/auth/google/callback");
    const scope = encodeURIComponent("openid email profile");
    const state = crypto.randomUUID();
    const nonce = crypto.randomUUID();

    sessionStorage.setItem("google_oauth_state", state);
    sessionStorage.setItem("google_oauth_nonce", nonce);

    // Use implicit flow to get both access_token and id_token
    const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${provider.client_id}&response_type=token id_token&scope=${scope}&redirect_uri=${redirectUri}&state=${state}&nonce=${nonce}`;

    const popup = window.open(authUrl, "google-login", "width=500,height=600,scrollbars=yes");

    if (!popup) {
      throw new Error("Popup blocked. Please allow popups for this site.");
    }

    return new Promise<void>((resolve, reject) => {
      let isResolved = false;

      // Set a timeout to cleanup if no response is received
      const timeout = setTimeout(
        () => {
          if (!isResolved) {
            window.removeEventListener("message", messageHandler);
            clearInterval(popupChecker);
            reject(new Error("Login timeout - no response received"));
          }
        },
        5 * 60 * 1000,
      ); // 5 minutes timeout

      // Check if popup was closed by user
      const popupChecker = setInterval(() => {
        try {
          if (popup.closed) {
            clearInterval(popupChecker);
            if (!isResolved) {
              clearTimeout(timeout);
              window.removeEventListener("message", messageHandler);
              reject(new Error("Login cancelled - popup was closed"));
            }
          }
        } catch {
          // Ignore COOP errors - popup might be on different origin
        }
      }, 500);

      const messageHandler = async (
        event: MessageEvent<{
          type: string;
          access_token?: string;
          id_token?: string;
          state?: string;
          error?: string;
        }>,
      ) => {
        if (event.origin !== window.location.origin) return;

        if (event.data.type === "GOOGLE_TOKEN") {
          isResolved = true;
          clearTimeout(timeout);
          clearInterval(popupChecker);
          window.removeEventListener("message", messageHandler);

          try {
            popup.close();
          } catch {
            // Popup might already be closed, ignore error
          }

          // Handle error from callback
          if (event.data.error) {
            reject(new Error(event.data.error));
            return;
          }

          try {
            // Verify CSRF state
            const storedState = sessionStorage.getItem("google_oauth_state");
            sessionStorage.removeItem("google_oauth_state");
            sessionStorage.removeItem("google_oauth_nonce");

            if (!storedState || storedState !== event.data.state) {
              throw new Error("Invalid state parameter. Possible CSRF attack.");
            }

            const authResponse = await $allauth.socialLogin("google", event.data.access_token, event.data.id_token);

            await handleAuthSuccess("Google", authResponse);
            resolve();
          } catch (error: unknown) {
            console.error("Google login error:", error);
            reject(error instanceof Error ? error : new Error(String(error)));
          }
        }
      };

      window.addEventListener("message", messageHandler);
    });
  };

  /**
   * Handle Microsoft OAuth authentication via popup
   */
  const loginWithMicrosoft = async (): Promise<void> => {
    const provider = await getProviderConfig("microsoft");
    const redirectUri = encodeURIComponent(window.location.origin + "/auth/microsoft/callback");
    const scope = encodeURIComponent("openid email profile");
    const state = crypto.randomUUID();

    sessionStorage.setItem("ms_oauth_state", state);

    const authUrl = `https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id=${provider.client_id}&response_type=token&scope=${scope}&redirect_uri=${redirectUri}&response_mode=fragment&state=${state}`;

    const popup = window.open(authUrl, "microsoft-login", "width=500,height=600,scrollbars=yes");

    if (!popup) {
      throw new Error("Popup blocked. Please allow popups for this site.");
    }

    return new Promise<void>((resolve, reject) => {
      let isResolved = false;

      // Set a timeout to cleanup if no response is received
      const timeout = setTimeout(
        () => {
          if (!isResolved) {
            window.removeEventListener("message", messageHandler);
            clearInterval(popupChecker);
            reject(new Error("Login timeout - no response received"));
          }
        },
        5 * 60 * 1000,
      ); // 5 minutes timeout

      // Check if popup was closed by user
      const popupChecker = setInterval(() => {
        try {
          if (popup.closed) {
            clearInterval(popupChecker);
            if (!isResolved) {
              clearTimeout(timeout);
              window.removeEventListener("message", messageHandler);
              reject(new Error("Login cancelled - popup was closed"));
            }
          }
        } catch {
          // Ignore COOP errors - popup might be on different origin
        }
      }, 500);

      const messageHandler = async (
        event: MessageEvent<{ type: string; access_token?: string; state?: string; error?: string }>,
      ) => {
        if (event.origin !== window.location.origin) return;

        if (event.data.type === "MSAL_TOKEN") {
          isResolved = true;
          clearTimeout(timeout);
          clearInterval(popupChecker);
          window.removeEventListener("message", messageHandler);

          try {
            popup.close();
          } catch {
            // Popup might already be closed, ignore error
          }

          // Handle error from callback
          if (event.data.error) {
            reject(new Error(event.data.error));
            return;
          }

          try {
            // Verify CSRF state
            const storedState = sessionStorage.getItem("ms_oauth_state");
            sessionStorage.removeItem("ms_oauth_state");

            if (!storedState || storedState !== event.data.state) {
              throw new Error("Invalid state parameter. Possible CSRF attack.");
            }

            const authResponse = await $allauth.socialLogin("microsoft", event.data.access_token);

            await handleAuthSuccess("Microsoft", authResponse);
            resolve();
          } catch (error: unknown) {
            console.error("Microsoft login error:", error);
            reject(error instanceof Error ? error : new Error(String(error)));
          }
        }
      };

      window.addEventListener("message", messageHandler);
    });
  };

  /**
   * Login with specified social provider
   */
  const login = async (provider: SocialProvider): Promise<void> => {
    if (loading.value) return;

    loading.value = true;

    try {
      if (provider === "google") {
        await loginWithGoogle();
      } else if (provider === "microsoft") {
        await loginWithMicrosoft();
      }
    } catch (error: unknown) {
      console.error(`${provider} login error:`, error);
      const errorMessage = error instanceof Error ? error.message : `${provider} login failed`;
      toast.add({
        severity: "error",
        summary: "Error",
        detail: errorMessage,
        life: 5000,
      });
      throw error;
    } finally {
      loading.value = false;
    }
  };

  return {
    login,
    loading: readonly(loading),
    loginWithGoogle,
    loginWithMicrosoft,
  };
}
