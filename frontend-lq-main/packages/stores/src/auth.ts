import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { useQuery, provideApolloClient } from "@vue/apollo-composable";
import { GET_USER_PROFILE_BY_ID, type UserProfileFragment } from "@lq/graphql";
import type { DocumentNode } from "graphql";
import { normalizeAllauthError, type AllauthClient, type AuthResponse, type NormalizedAuthError } from "@lq/clients";
import type {
  AuthUser,
  LoginResponse,
  RegisterResponse,
  RegisterFormData,
  Institution,
  UserProfileComplete,
} from "@lq/types";

export interface AuthState {
  userProfile: UserProfileFragment | null;
  userAuth: AuthUser | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
}

export function clearAuthStorage() {
  if (typeof window === "undefined") return;

  localStorage.removeItem("auth_token");
  // Note: refresh_token is no longer persisted, only kept in memory
  localStorage.removeItem("auth_user");
  localStorage.removeItem("auth_user_profile_complete");
  localStorage.removeItem("auth_institution");
}

/**
 * Authentication store
 * Manages user authentication state, tokens, and session
 */
// Instance holders for Vue standalone apps
let standaloneAllauth: unknown = null;
let standaloneApollo: unknown = null;

export function setAllauthInstance(allauthInstance: unknown) {
  standaloneAllauth = allauthInstance;
}

export function setApolloInstance(apolloInstance: unknown) {
  standaloneApollo = apolloInstance;
}

export const useAuthStore = defineStore("auth", () => {
  const userProfile = ref<UserProfileFragment | null>(null);
  const userAuth = ref<AuthUser | null>(null);
  const token = ref<string | null>(null);
  const refreshToken = ref<string | null>(null);
  const loading = ref(false);
  const error = ref<Error | null>(null);

  // Complete user profile and institution data (persisted)
  const userProfileComplete = ref<UserProfileComplete | null>(null);
  const institution = ref<Institution | null>(null);

  const userRole = computed(() => userProfile.value?.primaryRole || null);
  const isAuthenticated = computed(() => !!token.value && !!userAuth.value);
  const userId = computed(() => userAuth.value?.id || null);

  const getAllauth = (): AllauthClient | null => {
    return standaloneAllauth as AllauthClient | null;
  };

  const getApollo = () => {
    return standaloneApollo;
  };

  async function login(
    email: string,
    password: string,
  ): Promise<{ success: boolean; requiresEmailVerification?: boolean }> {
    loading.value = true;
    error.value = null;

    try {
      const $allauth = getAllauth();
      if (!$allauth) {
        throw new Error("Allauth not initialized");
      }

      let authResponse: LoginResponse;

      try {
        authResponse = await $allauth.login({ email, password });
      } catch (allauthError: any) {
        // Allauth throws on non-OK responses, check if it's email not verified
        console.error("Allauth login error/response:", allauthError);

        // The error object has the full response assigned to it via Object.assign
        // So we can access errors, data, status directly from the error
        const status = allauthError?.status;
        const errors = allauthError?.errors || [];
        const userData = allauthError?.data?.user;

        // Check if it's a 403 email not verified error
        if (status === 403) {
          const emailNotVerified = errors.some((err: any) => err?.code === "email_not_verified");

          if (emailNotVerified) {
            // Store user data even though not authenticated
            if (userData) {
              userAuth.value = userData;
            }

            return {
              success: false,
              requiresEmailVerification: true,
            };
          }
        }

        // If it's not a 403 email verification error, re-throw
        throw allauthError;
      }

      console.error("Login response:", { status: authResponse.status, authResponse });

      // Check for email not verified error (403) - in case it doesn't throw
      if (authResponse.status === 403) {
        // Errors are at the root level, not in data
        const errors = authResponse.errors || [];
        console.error("403 Response details:", {
          errors,
          rootErrors: authResponse.errors,
          dataErrors: authResponse.data?.errors,
          hasErrors: errors.length > 0,
          errorCodes: errors.map((e) => e?.code),
        });

        const emailNotVerified = errors.some((err) => err?.code === "email_not_verified");

        if (emailNotVerified) {
          // Store user data even though not authenticated
          const allauthUser = authResponse.data?.user;
          if (allauthUser) {
            userAuth.value = allauthUser;
          }

          return {
            success: false,
            requiresEmailVerification: true,
          };
        }
      }

      if (authResponse.meta?.is_authenticated) {
        if (authResponse.meta.access_token) {
          token.value = authResponse.meta.access_token;
          refreshToken.value = authResponse.meta.refresh_token || null;

          // Only persist access_token, keep refresh_token in memory only
          if (typeof window !== "undefined") {
            localStorage.setItem("auth_token", token.value);
          }
        }

        const allauthUser = authResponse.data?.user;
        userAuth.value = allauthUser || null;
        if (allauthUser?.onboarding_completed) {
          await fetchCurrentUserById(allauthUser);
        }

        return { success: true };
      } else {
        let errorMessage = "Login failed";

        // Check for errors in the response
        if (authResponse.data.errors && authResponse.data.errors.length > 0) {
          errorMessage = authResponse.data.errors[0].message;
        } else if (authResponse.status === 409) {
          errorMessage = "Tu cuenta requiere verificación de email. Por favor verifica tu correo.";
        } else if (authResponse.status === 401) {
          errorMessage = "Credenciales inválidas. Por favor verifica tu correo y contraseña.";
        } else if (authResponse.data.flows && authResponse.data.flows.length > 0) {
          const flow = authResponse.data.flows[0];
          if (flow.id === "verify_email") {
            errorMessage = "Debes verificar tu correo electrónico antes de continuar.";
          } else {
            errorMessage = `Se requiere completar: ${flow.id}`;
          }
        }

        throw new Error(errorMessage);
      }
    } catch (err) {
      console.error("Login failed:", err);
      const normalizedError: NormalizedAuthError = normalizeAllauthError(err);
      error.value = normalizedError;
      throw normalizedError;
    } finally {
      loading.value = false;
    }
  }

  async function register(form: RegisterFormData) {
    loading.value = true;
    error.value = null;

    try {
      const $allauth = getAllauth();
      if (!$allauth) {
        throw new Error("Allauth not initialized");
      }

      const payload = {
        email: form.email.trim(),
        username: form.email.trim(),
        password: form.password,
        password2: form.password2,
        first_name: form.firstName?.trim() || "",
        last_name: form.lastName?.trim() || "",
      };

      let registerResponse: RegisterResponse;

      try {
        registerResponse = await $allauth.signUp(payload);
      } catch (allauthError: any) {
        // Allauth might throw on 201, but it's actually a success
        console.error("Allauth signUp error/response:", {
          error: allauthError,
          status: allauthError?.status,
          responseStatus: allauthError?.response?.status,
          data: allauthError?.data,
          responseData: allauthError?.response?.data,
        });

        // Check if it's actually a 201 success response in various possible structures
        const status = allauthError?.status || allauthError?.response?.status || allauthError?.data?.status;

        if (status === 201) {
          // Extract the actual response data
          registerResponse = allauthError.response || allauthError.data || allauthError;
        } else {
          throw allauthError;
        }
      }

      const status = registerResponse.status ?? 0;

      console.error("Register response:", { status, registerResponse });

      // 201 Created is a success status for registration with email verification
      if (status >= 400) {
        const errorMessage = getRegisterErrorMessage(registerResponse);
        throw new Error(errorMessage);
      }

      const userData = registerResponse.data?.user;
      if (userData) {
        userAuth.value = userData;
      }

      // 201 means user created but needs email verification
      // 200 means user created and authenticated
      const requiresVerification = status === 201 || !registerResponse.meta?.is_authenticated;
      const emailVerified = registerResponse.data?.user?.email_verified ?? false;

      if (registerResponse.meta?.is_authenticated) {
        // Only persist tokens if email is verified
        if (emailVerified && registerResponse.meta.access_token) {
          token.value = registerResponse.meta.access_token;
          refreshToken.value = registerResponse.meta.refresh_token || null;

          // Only persist access_token, keep refresh_token in memory only
          if (typeof window !== "undefined") {
            localStorage.setItem("auth_token", token.value);
          }
        }

        const registeredUser = registerResponse.data?.user;
        if (registeredUser?.email_verified) {
          restoreSession();
        } else if (registeredUser?.onboarding_completed) {
          await fetchCurrentUserById(registeredUser);
        }
      }

      return {
        success: true,
        requiresEmailVerification: requiresVerification,
        emailVerified,
      };
    } catch (err) {
      console.error("Register failed:", err);
      const normalizedError: NormalizedAuthError = normalizeAllauthError(err);
      error.value = normalizedError;
      throw normalizedError;
    } finally {
      loading.value = false;
    }
  }

  async function logout() {
    loading.value = true;
    try {
      // Use django-allauth REST API for logout
      const $allauth = getAllauth();
      if ($allauth) {
        await $allauth.logout();
      }

      // Clear state
      userProfile.value = null;
      token.value = null;
      refreshToken.value = null;

      // Clear localStorage
      clearAuthStorage();
    } catch (err) {
      console.error("Logout failed:", err);
      // Clear state anyway
      userProfile.value = null;
      token.value = null;
      refreshToken.value = null;

      clearAuthStorage();
    } finally {
      loading.value = false;
    }
  }

  async function verifyEmail(key: string): Promise<{ success: boolean }> {
    loading.value = true;
    error.value = null;

    try {
      const $allauth = getAllauth();
      if (!$allauth) {
        throw new Error("Allauth not initialized");
      }

      const response: RegisterResponse = await $allauth.verifyEmail(key);

      if (response.status === 200) {
        // if (response.data?.user) {
        //   syncUserFromAllauth(response);
        // }

        return { success: true };
      } else {
        // Verification failed
        let errorMessage = "Error al verificar el email. Por favor intenta de nuevo.";

        if (response.data?.errors && Array.isArray(response.data.errors) && response.data.errors.length > 0) {
          errorMessage = response.data.errors[0].message || errorMessage;
        }

        throw new Error(errorMessage);
      }
    } catch (err: unknown) {
      console.error("Email verification failed:", err);
      error.value = err as Error;

      // Re-throw the error
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function resendEmailVerification(): Promise<{ success: boolean; isConflict?: boolean }> {
    loading.value = true;
    error.value = null;

    try {
      const $allauth = getAllauth();
      if (!$allauth) {
        throw new Error("Allauth not initialized");
      }

      const response = await $allauth.resendEmailVerification();

      console.error("Resend email verification response:", {
        status: response.status,
        response,
      });

      if (response.status === 200) {
        return { success: true };
      } else if (response.status === 409) {
        // Email already verified or rate limited
        const errorMessage =
          "Tu email ya está verificado o ya se envió un correo recientemente. Por favor espera unos minutos antes de intentar de nuevo.";
        const conflictError = new Error(errorMessage) as Error & { isConflict: boolean };
        conflictError.isConflict = true;
        throw conflictError;
      } else {
        throw new Error("Error al reenviar el email de verificación. Por favor intenta de nuevo.");
      }
    } catch (err: unknown) {
      console.error("Resend email verification failed:", err);
      error.value = err as Error;
      throw err;
    } finally {
      loading.value = false;
    }
  }

  function syncUserFromAllauth(allauthResponse: any) {
    // Extract user data from Allauth response
    const userData = allauthResponse.data?.user || allauthResponse.user;

    if (userData) {
      userProfile.value = {
        id: String(userData.id || userData.pk || ""),
        // username property removed as it does not exist in UserProfileFragment
        email: userData.email || "",
        firstName: userData.first_name || userData.firstName || "",
        lastName: userData.last_name || userData.lastName || "",
        userType: userData.user_type || userData.userType || "student",
        isStaff: userData.is_staff || userData.isStaff || false,
        avatar: userData.avatar || undefined,
        needsOnboarding: userData.needs_onboarding ?? userData.needsOnboarding ?? true,
      } as unknown as UserProfileFragment;

      // Store in localStorage
      if (typeof window !== "undefined") {
        localStorage.setItem("auth_user", JSON.stringify(userProfile.value));
      }
    }

    // Store session token if available
    if (allauthResponse.meta?.session_token) {
      token.value = allauthResponse.meta.session_token;
      if (typeof window !== "undefined" && token.value) {
        localStorage.setItem("auth_token", token.value);
      }
    }
  }

  function flattenErrorValue(value: unknown): string[] {
    if (!value) return [];

    if (Array.isArray(value)) {
      return value.flatMap((entry) => flattenErrorValue(entry));
    }

    if (typeof value === "string") {
      return [value];
    }

    if (typeof value === "object") {
      return Object.values(value).flatMap((entry) => flattenErrorValue(entry));
    }

    return [];
  }

  function getRegisterErrorMessage(response: RegisterResponse): string {
    const fallback = "No pudimos crear tu cuenta. Intenta nuevamente.";
    const data = response.data;

    if (!data) return fallback;

    const candidateErrors: string[] = [];

    if (Array.isArray(data.errors)) {
      const mapped = data.errors
        .map(
          (item: unknown) =>
            (item as { message?: string; detail?: string })?.message || (item as { detail?: string })?.detail || item,
        )
        .filter(Boolean)
        .map(String);
      candidateErrors.push(...mapped);
    }

    candidateErrors.push(...flattenErrorValue(data.form_errors));
    candidateErrors.push(...flattenErrorValue(data.non_field_errors));

    if (typeof data.detail === "string") {
      candidateErrors.push(data.detail);
    }

    if (typeof data.message === "string") {
      candidateErrors.push(data.message);
    }

    if (candidateErrors.length > 0) {
      return candidateErrors.join(" ");
    }

    return fallback;
  }

  function fetchUser(query: DocumentNode, variables: Record<string, string>): Promise<UserProfileFragment> {
    loading.value = true;
    try {
      const $apollo = getApollo();
      if (!$apollo) {
        throw new Error("Apollo client not initialized");
      }
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      provideApolloClient($apollo as any);

      const { onResult, onError } = useQuery(query, variables, { fetchPolicy: "network-only" });

      return new Promise((resolve, reject) => {
        onResult((result) => {
          if (result.data?.readUserProfile) {
            const userData = result.data.readUserProfile;

            // Unified user mapping
            userProfile.value = userData || null;

            // Store user in localStorage for persistence
            if (typeof window !== "undefined") {
              localStorage.setItem("auth_user", JSON.stringify(userProfile.value));
            }

            resolve(userProfile.value as UserProfileFragment);
          } else {
            reject(new Error("No user data received"));
          }
        });

        onError((err) => {
          console.error("Failed to fetch user:", err);
          error.value = err;
          reject(err);
        });
      });
    } catch (err) {
      console.error("Failed to fetch user:", err);
      error.value = err as Error;
      throw err;
    } finally {
      loading.value = false;
    }
  }

  function fetchCurrentUserById(authUser: AuthUser): Promise<UserProfileFragment> {
    return fetchUser(GET_USER_PROFILE_BY_ID, { id: authUser.id });
  }

  async function refreshAuthToken() {
    try {
      if (!refreshToken.value) {
        throw new Error("No refresh token available");
      }

      const $allauth = getAllauth();
      if (!$allauth) {
        throw new Error("Allauth not initialized");
      }

      // Call refresh token endpoint
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/_allauth/browser/v1/auth/token/refresh`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          refresh: refreshToken.value,
        }),
      });

      if (!response.ok) {
        throw new Error("Token refresh failed");
      }

      const data = await response.json();

      if (data.meta?.access_token) {
        token.value = data.meta.access_token;
        if (data.meta.refresh_token) {
          refreshToken.value = data.meta.refresh_token;
        }

        if (typeof window !== "undefined" && token.value) {
          localStorage.setItem("auth_token", token.value);
          if (refreshToken.value) {
            localStorage.setItem("auth_refresh_token", refreshToken.value);
          }
        }
      } else {
        throw new Error("No access token in refresh response");
      }
    } catch (error) {
      console.error("Token refresh failed:", error);
      await logout();
      throw error;
    }
  }

  async function restoreSession() {
    if (typeof window === "undefined") return;

    const storedToken = localStorage.getItem("auth_token");
    const storedUser = localStorage.getItem("auth_user");
    const storedUserProfileComplete = localStorage.getItem("auth_user_profile_complete");
    const storedInstitution = localStorage.getItem("auth_institution");

    if (storedToken && storedUser) {
      try {
        token.value = storedToken;
        userAuth.value = JSON.parse(storedUser);

        // Call session endpoint to rotate tokens
        await refreshSessionTokens();
      } catch (error) {
        console.error("Failed to restore session:", error);
        // If session refresh fails, clear auth state but don't redirect
        // Let the auth middleware handle the redirect
        token.value = null;
        userAuth.value = null;
        userProfile.value = null;
        userProfileComplete.value = null;
        institution.value = null;

        if (typeof window !== "undefined") {
          localStorage.removeItem("auth_token");
          localStorage.removeItem("auth_user");
          localStorage.removeItem("auth_user_profile");
          localStorage.removeItem("auth_user_profile_complete");
          localStorage.removeItem("auth_institution");
        }
        return;
      }
    }

    if (storedUserProfileComplete) {
      try {
        userProfileComplete.value = JSON.parse(storedUserProfileComplete);
      } catch (error) {
        console.error("Failed to parse stored user profile complete:", error);
      }
    }

    if (storedInstitution) {
      try {
        institution.value = JSON.parse(storedInstitution);
      } catch (error) {
        console.error("Failed to parse stored institution:", error);
      }
    }
  }

  async function refreshSessionTokens() {
    try {
      const $allauth = getAllauth();
      if (!$allauth) {
        throw new Error("Allauth not initialized");
      }

      // Call session endpoint with current access token for rotation
      const response: AuthResponse = await $allauth.getSession(token.value || undefined);

      // Update tokens from session response (token rotation)
      if (response.meta?.access_token) {
        token.value = response.meta.access_token;
        refreshToken.value = response.meta.refresh_token || null;

        // Only persist access_token
        if (typeof window !== "undefined" && token.value) {
          localStorage.setItem("auth_token", token.value);
        }
      }

      // Update user data if provided
      const responseData = response.data as { user?: AuthUser };
      if (responseData?.user) {
        userAuth.value = responseData.user;
        if (typeof window !== "undefined") {
          localStorage.setItem("auth_user", JSON.stringify(userAuth.value));
        }
      }
    } catch (error) {
      console.error("Failed to refresh session tokens:", error);
      throw error;
    }
  }

  function hasRole(role: string) {
    return userProfile.value?.primaryRole === role;
  }

  function hasAnyRole(roles: string[]) {
    return userProfile.value?.primaryRole ? roles.includes(userProfile.value.primaryRole) : false;
  }

  async function requestPasswordReset(_email: string) {
    // Mock implementation - always succeeds
    loading.value = true;
    error.value = null;

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // Mock success response
      return {
        success: true,
        message: "Password reset instructions sent to your email",
      };
    } catch (err) {
      console.error("Password reset request failed:", err);
      error.value = err as Error;
      throw err;
    } finally {
      loading.value = false;
    }
  }

  function markOnboardingCompleted() {
    if (userAuth.value) {
      userAuth.value.onboarding_completed = true;
    }
  }

  /**
   * Save complete user profile data to localStorage and state
   */
  function setUserProfileComplete(profile: UserProfileComplete) {
    userProfileComplete.value = profile;

    if (typeof window !== "undefined") {
      localStorage.setItem("auth_user_profile_complete", JSON.stringify(profile));
    }
  }

  /**
   * Save institution data to localStorage and state
   */
  function setInstitution(institutionData: Institution) {
    institution.value = institutionData;

    if (typeof window !== "undefined") {
      localStorage.setItem("auth_institution", JSON.stringify(institutionData));
    }
  }

  /**
   * Clear institution data from localStorage and state
   */
  function clearInstitution() {
    institution.value = null;

    if (typeof window !== "undefined") {
      localStorage.removeItem("auth_institution");
    }
  }

  return {
    userProfile,
    userAuth,
    userProfileComplete,
    institution,
    token,
    refreshToken,
    loading,
    error,

    isAuthenticated,
    userRole,
    userId,

    login,
    logout,
    fetchCurrentUserById,
    register,
    refreshAuthToken,
    restoreSession,
    hasRole,
    hasAnyRole,
    requestPasswordReset,

    verifyEmail,
    resendEmailVerification,
    syncUserFromAllauth,
    markOnboardingCompleted,
    setUserProfileComplete,
    setInstitution,
    clearInstitution,
  };
});
