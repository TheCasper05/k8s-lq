/**
 * Onboarding Middleware
 *
 * Ensures users complete onboarding before accessing the app.
 * Redirects based on authentication and onboarding status.
 */

import { useAuthStore } from "@lq/stores";
import { getRoleDashboardRoute } from "@lq/utils";

import { PUBLIC_AUTH_PAGES, ONBOARDING_PAGES, PROTECTED_AUTH_PAGES, AUTH_ROUTES, AccountType } from "@lq/types";

export default defineNuxtRouteMiddleware((to, from) => {
  const authStore = useAuthStore();
  const isAuthenticated = authStore.isAuthenticated;
  const user = authStore.userAuth;
  const needsOnboarding = !user?.onboarding_completed;
  const config = useRuntimeConfig();
  const BYPASS_ONBOARDING = config.public.bypassOnboarding;

  // Auth pages that don't require authentication
  // /accounts/verify-email is for email verification links from inbox
  const allowedUnauthPages = [...PUBLIC_AUTH_PAGES, "/accounts/verify-email"];

  // Onboarding pages - also allowed without authentication (user just registered)
  const onboardingPages = ONBOARDING_PAGES;

  // Protected auth pages that require active flow (no refresh/direct access)
  const protectedAuthPages = PROTECTED_AUTH_PAGES;

  const isAllowedUnauthPage = allowedUnauthPages.some((page) => to.path === page || to.path.startsWith(`${page}/`));
  const isOnboardingPage = onboardingPages.some((page) => to.path.startsWith(page));
  const isProtectedAuthPage = protectedAuthPages.some((page) => to.path.startsWith(page));

  // Case 1: User is NOT authenticated
  if (!isAuthenticated) {
    // Bypass mode: skip login/onboarding and go straight to a dashboard
    if (BYPASS_ONBOARDING) {
      // Only force dashboard when coming from root or auth/onboarding routes
      const targetDashboard = getRoleDashboardRoute(AccountType.TEACHER);

      const isAuthOrOnboarding = isAllowedUnauthPage || isOnboardingPage;

      if ((to.path === "/" || isAuthOrOnboarding) && to.path !== targetDashboard) {
        return navigateTo(targetDashboard);
      }

      // For any other route, allow navigation normally even without auth
      return;
    }

    // Protected auth pages require active flow (no refresh/direct access)
    // This includes /auth/login/email and all onboarding pages
    if (isProtectedAuthPage) {
      // Check if it's a direct access/refresh (no 'from' route or same path)
      // Direct access or refresh should redirect to login
      if (!from || from.path === to.path) {
        return navigateTo(AUTH_ROUTES.LOGIN);
      }
      // Allow if coming from another page (programmatic navigation)
      return;
    }

    // Allow access to other auth pages (login, register, verify-email)
    if (isAllowedUnauthPage) {
      return;
    }

    // Redirect all other pages to main login page
    return navigateTo(AUTH_ROUTES.LOGIN);
  }

  // Case 2: User IS authenticated AND bypass flag is enabled
  if (isAuthenticated && BYPASS_ONBOARDING) {
    // Treat user as fully onboarded: redirect from auth/onboarding pages to dashboard
    const isAuthOrOnboardingPage = isAllowedUnauthPage || isOnboardingPage;

    if (isAuthOrOnboardingPage) {
      const userRole = authStore.userProfile?.primaryRole || authStore.userProfileComplete?.primaryRole;
      const targetDashboard = getRoleDashboardRoute(userRole);

      if (to.path !== targetDashboard) {
        return navigateTo(targetDashboard);
      }
      return;
    }

    // Allow access to all other pages
    return;
  }

  // Case 3: User IS authenticated AND needs onboarding
  if (isAuthenticated && needsOnboarding) {
    // Allow access to onboarding pages
    if (isOnboardingPage) {
      return;
    }
    // Redirect from other pages to onboarding
    return navigateTo(AUTH_ROUTES.REGISTER_ACCOUNT_TYPE);
  }

  // Case 4: User IS authenticated AND completed onboarding
  if (isAuthenticated && !needsOnboarding) {
    // Redirect from auth/onboarding pages to role-specific dashboard
    if (isAllowedUnauthPage || isOnboardingPage) {
      // Get user role and redirect to appropriate dashboard
      const userRole = authStore.userProfile?.primaryRole || authStore.userProfileComplete?.primaryRole;
      const targetDashboard = getRoleDashboardRoute(userRole);

      if (to.path !== targetDashboard) {
        return navigateTo(targetDashboard);
      }
      return;
    }
    // Allow access to all other pages
    return;
  }
});
