/**
 * Role Layout Middleware
 *
 * Automatically assigns the correct layout based on route and authentication state.
 * Runs after onboarding and role-guard middlewares.
 */

import { useAuthStore } from "@lq/stores";

export default defineNuxtRouteMiddleware((to) => {
  const authStore = useAuthStore();
  const { isAuthenticated } = authStore;
  const config = useRuntimeConfig();
  const BYPASS_ONBOARDING = config.public.bypassOnboarding;

  // Authentication routes always use 'auth' layout
  if (to.path.startsWith("/auth")) {
    setPageLayout("auth");
    return;
  }

  // Authenticated users (or bypass mode) use 'app' layout
  if (isAuthenticated || BYPASS_ONBOARDING) {
    setPageLayout("app");
    return;
  }

  // Fallback to auth layout
  setPageLayout("auth");
});
