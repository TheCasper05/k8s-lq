import { useAuthStore, useOnboardingStore } from "@lq/stores";
import { FlowType } from "@lq/types";
import { AUTH_ROUTES } from "@lq/utils";
import { useAppToast } from "./useAppToast";
import { useRoleRedirect } from "./useRoleRedirect";

export interface LoginResult {
  success: boolean;
  requiresEmailVerification?: boolean;
}

export interface RegisterResult {
  success: boolean;
  requiresEmailVerification?: boolean;
}

/**
 * Composable for handling authentication navigation flows
 * Manages post-login/register redirects, onboarding checks, and email verification
 */
export const useAuthNavigation = () => {
  const router = useRouter();
  const authStore = useAuthStore();
  const onboardingStore = useOnboardingStore();
  const toast = useAppToast();
  const { t } = useI18n();
  const { redirectToDashboard: redirectToRoleDashboard } = useRoleRedirect();
  const config = useRuntimeConfig();
  const BYPASS_ONBOARDING = config.public.bypassOnboarding;

  /**
   * Handle navigation after successful login
   * Checks for email verification, onboarding completion and redirects accordingly
   */
  const handlePostLogin = async (result: LoginResult) => {
    // If email verification is required (even if login failed), redirect to verify-email page
    if (result.requiresEmailVerification) {
      const userEmail = authStore.userAuth?.email || "";
      await router.push({
        path: AUTH_ROUTES.REGISTER_VERIFY_EMAIL,
        query: { email: userEmail },
      });
      return;
    }

    // If login was not successful and doesn't require email verification, exit
    if (!result.success) {
      if (result.requiresEmailVerification) {
        toast.auth.loginError(t("auth.emailVerificationRequired"));
      }
      return;
    }

    const currentUser = authStore.userAuth;

    // Optional bypass for onboarding (e.g. for dev/staging)
    if (BYPASS_ONBOARDING) {
      toast.auth.loginSuccess();
      await redirectToRoleDashboard();
      return;
    }

    // Check if onboarding is completed
    if (!currentUser?.onboarding_completed) {
      onboardingStore.setFlowType(FlowType.LOGIN);
      await router.push(AUTH_ROUTES.REGISTER_ACCOUNT_TYPE);
      return;
    }

    // Show success message
    toast.auth.loginSuccess();

    // Redirect to role-specific dashboard
    await redirectToRoleDashboard();
  };

  /**
   * Handle navigation after successful registration
   * Redirects to email verification or onboarding flow
   */
  const handlePostRegister = async (result: RegisterResult) => {
    if (!result.success) return;

    // If email verification is required, redirect to verify-email page
    if (result.requiresEmailVerification) {
      const userEmail = authStore.userAuth?.email || "";
      await router.push({
        path: AUTH_ROUTES.REGISTER_VERIFY_EMAIL,
        query: { email: userEmail },
      });
      return;
    }

    // Show success message
    toast.auth.registerSuccess();

    // Redirect to onboarding
    onboardingStore.setFlowType(FlowType.REGISTER);
    await router.push(AUTH_ROUTES.REGISTER_ACCOUNT_TYPE);
  };

  /**
   * Handle logout and redirect to login
   */
  const handleLogout = async () => {
    await authStore.logout();
    await router.push(AUTH_ROUTES.LOGIN);
  };

  /**
   * Handle forgot password request
   * Sends password reset email and redirects to check-email page
   */
  const handleForgotPassword = async (email: string) => {
    try {
      const $allauth = useNuxtApp().$allauth;
      if (!$allauth) {
        throw new Error("Allauth not initialized");
      }

      await $allauth.requestPasswordReset(email);

      toast.success({
        summaryKey: "common.success",
        detailKey: "auth.passwordResetSent",
        life: 5000,
      });

      // Redirect to check-email page with email in query
      await router.push({
        path: AUTH_ROUTES.FORGOT_PASSWORD_CHECK_EMAIL,
        query: { email },
      });

      return { success: true };
    } catch (error) {
      console.error("Password reset request failed:", error);
      toast.error({
        summaryKey: "common.error",
        detailKey: "auth.somethingWentWrong",
        life: 5000,
      });
      return { success: false, error };
    }
  };

  /**
   * Handle password reset with key
   * Confirms password reset and redirects to login on success
   */
  const handleResetPassword = async (key: string, password: string, password2: string) => {
    try {
      const $allauth = useNuxtApp().$allauth;
      if (!$allauth) {
        throw new Error("Allauth not initialized");
      }

      await $allauth.resetPasswordWithKey(key, password, password2);

      toast.success({
        summaryKey: "common.success",
        detailKey: "auth.passwordResetSuccess",
        life: 5000,
      });

      // Redirect to login after short delay
      setTimeout(async () => {
        await router.push(AUTH_ROUTES.LOGIN_EMAIL);
      }, 2000);

      return { success: true };
    } catch (error: unknown) {
      console.error("Password reset confirmation failed:", error);

      // Check for invalid/expired key error
      if (error && typeof error === "object" && "errors" in error && Array.isArray(error.errors)) {
        const errors = error.errors as Array<{ code?: string; message?: string }>;
        const invalidKeyError = errors.find((err) => err.code === "invalid_key");

        if (invalidKeyError) {
          toast.error({
            summaryKey: "common.error",
            detailKey: "auth.invalidOrExpiredResetKey",
            life: 5000,
          });

          // Redirect to forgot password page to request new link
          setTimeout(async () => {
            await router.push(AUTH_ROUTES.FORGOT_PASSWORD);
          }, 2000);

          return { success: false, error, invalidKey: true };
        }
      }

      // Generic error
      toast.error({
        summaryKey: "common.error",
        detailKey: "auth.somethingWentWrong",
        life: 5000,
      });

      return { success: false, error };
    }
  };

  /**
   * Resend password reset email
   */
  const handleResendPasswordReset = async (email: string) => {
    try {
      const $allauth = useNuxtApp().$allauth;
      if (!$allauth) {
        throw new Error("Allauth not initialized");
      }

      await $allauth.requestPasswordReset(email);

      toast.success({
        summaryKey: "common.success",
        detailKey: "auth.verificationEmailResent",
        life: 3000,
      });

      return { success: true };
    } catch (error) {
      console.error("Resend password reset failed:", error);
      toast.error({
        summaryKey: "common.error",
        detailKey: "auth.somethingWentWrong",
        life: 5000,
      });
      return { success: false, error };
    }
  };

  return {
    // Post-auth handlers
    handlePostLogin,
    handlePostRegister,

    // Password reset flow
    handleForgotPassword,
    handleResetPassword,
    handleResendPasswordReset,

    // Direct access to role redirect (for other composables)
    redirectToRoleDashboard,

    // Logout
    handleLogout,
  };
};
