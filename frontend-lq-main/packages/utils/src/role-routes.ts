/**
 * Role-based routing utilities
 *
 * Provides centralized mapping between user roles and their corresponding dashboard routes.
 * This ensures consistency across the application when redirecting users based on their roles.
 */

import { type AccountType, ROLE_DASHBOARD_ROUTES, ROLE_ROUTE_PREFIXES } from "@lq/types";

// Re-export all route constants for backward compatibility
export {
  ROLE_DASHBOARD_ROUTES,
  ROLE_ROUTE_PREFIXES,
  AUTH_ROUTES,
  ONBOARDING_PAGES,
  PROTECTED_AUTH_PAGES,
  PUBLIC_AUTH_PAGES,
} from "@lq/types";

/**
 * Get the dashboard route for a given role
 * @param role - User role
 * @returns Dashboard route path
 *
 * @example
 * ```ts
 * const route = getRoleDashboardRoute(AccountType.STUDENT);
 * // Returns: "/student/dashboard"
 * ```
 */
export function getRoleDashboardRoute(role: AccountType | string | null | undefined): string {
  if (!role) return "/";
  return ROLE_DASHBOARD_ROUTES[role as AccountType] || "/";
}

/**
 * Get the route prefix for a given role
 * @param role - User role
 * @returns Route prefix
 *
 * @example
 * ```ts
 * const prefix = getRoleRoutePrefix(AccountType.TEACHER);
 * // Returns: "/teacher"
 * ```
 */
export function getRoleRoutePrefix(role: AccountType | string | null | undefined): string {
  if (!role) return "";
  return ROLE_ROUTE_PREFIXES[role as AccountType] || "";
}
