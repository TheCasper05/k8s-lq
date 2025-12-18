/**
 * Role Guard Middleware
 *
 * Protects routes based on user roles.
 * Prevents users from accessing routes they don't have permission for.
 */

import { useAuthStore } from "@lq/stores";
import { type AccountType, ROLE_ROUTE_PREFIXES } from "@lq/types";
import { getRoleDashboardRoute, getRoleRoutePrefix } from "@lq/utils";

export default defineNuxtRouteMiddleware((to) => {
  const authStore = useAuthStore();
  const { isAuthenticated, userProfile, userProfileComplete } = authStore;
  const config = useRuntimeConfig();
  const BYPASS_ONBOARDING = config.public.bypassOnboarding;

  // In bypass mode we don't enforce role-based route restrictions
  if (BYPASS_ONBOARDING) {
    return;
  }

  // Skip for auth routes
  if (to.path.startsWith("/auth")) {
    return;
  }

  // Skip if not authenticated (handled by onboarding middleware)
  if (!isAuthenticated) {
    return;
  }

  // Get user role (cast to AccountType for consistency)
  // userProfile comes from GraphQL (string), userProfileComplete uses AccountType
  const userRole = (userProfile?.primaryRole || userProfileComplete?.primaryRole) as AccountType;

  if (!userRole) {
    console.error("[role-guard] No user role found");
    return navigateTo("/auth/login");
  }

  // Get the route prefix for the user's role
  const userRolePrefix = getRoleRoutePrefix(userRole);

  // Get all role-specific prefixes from centralized constant
  const roleSpecificPrefixes = Object.values(ROLE_ROUTE_PREFIXES);
  const isRoleSpecificRoute = roleSpecificPrefixes.some((prefix) => to.path.startsWith(prefix));

  // Check if user is trying to access a route that doesn't match their role
  if (isRoleSpecificRoute && !to.path.startsWith(userRolePrefix)) {
    console.warn(`[role-guard] User with role ${userRole} attempted to access ${to.path}`);

    // Redirect to user's dashboard
    return navigateTo(getRoleDashboardRoute(userRole));
  }
});
