import type { AccountType } from "@lq/types";
import { getRoleRoutePrefix } from "@lq/utils";
import { useRouter } from "vue-router";

/**
 * Composable for role-based navigation
 *
 * Provides utilities to generate routes with role prefixes and navigate to role-specific pages.
 * Designed for Nuxt applications with multi-role support.
 *
 * @example
 * ```ts
 * const { getRoleRoute, navigateToRolePage } = useRoleNavigation();
 *
 * // Get route with prefix
 * const profileRoute = getRoleRoute('/profile'); // "/student/profile"
 *
 * // Navigate to role-specific page
 * await navigateToRolePage('/settings');
 * ```
 */
export const useRoleNavigation = (getCurrentRole: () => AccountType | null) => {
  const router = useRouter();

  /**
   * Get the role prefix for the current user
   * @returns Role prefix (e.g., "/student", "/teacher", "/admin")
   */
  const getRolePrefix = (): string => {
    const role = getCurrentRole();
    return getRoleRoutePrefix(role);
  };

  /**
   * Get a route with the current role prefix
   * @param page - Page path without prefix (e.g., "/profile", "/settings")
   * @returns Full route with role prefix (e.g., "/student/profile")
   *
   * @example
   * ```ts
   * getRoleRoute('/profile') // "/student/profile" (if user is student)
   * getRoleRoute('profile')  // "/student/profile" (also works without leading slash)
   * ```
   */
  const getRoleRoute = (page: string): string => {
    const prefix = getRolePrefix();
    // Remove leading slash from page if present to avoid double slashes
    const cleanPage = page.startsWith("/") ? page : `/${page}`;
    return `${prefix}${cleanPage}`;
  };

  /**
   * Navigate to a page with the current role prefix
   * @param page - Page path without prefix
   *
   * @example
   * ```ts
   * await navigateToRolePage('/profile')
   * ```
   */
  const navigateToRolePage = async (page: string) => {
    const route = getRoleRoute(page);
    return await router.push(route);
  };

  /**
   * Redirect to a page with the current role prefix (replaces history)
   * @param page - Page path without prefix
   *
   * @example
   * ```ts
   * return redirectToRolePage('/profile')
   * ```
   */
  const redirectToRolePage = (page: string) => {
    const route = getRoleRoute(page);
    return router.replace(route);
  };

  return {
    getRolePrefix,
    getRoleRoute,
    navigateToRolePage,
    redirectToRolePage,
  };
};
