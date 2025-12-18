import { useRoleLayout } from "./useRoleLayout";

/**
 * Composable for role-based redirects
 *
 * @example
 * ```ts
 * const { redirectToDashboard } = useRoleRedirect()
 * await redirectToDashboard()
 * ```
 */
export const useRoleRedirect = () => {
  const { layoutConfig } = useRoleLayout();

  /**
   * Redirect user to their role-specific dashboard
   */
  const redirectToDashboard = async () => {
    const dashboardRoute = layoutConfig.value?.dashboardRoute || "/";
    await navigateTo(dashboardRoute);
  };

  /**
   * Redirect user based on their role
   * Used after login/registration completion
   */
  const redirectByRole = async () => {
    await redirectToDashboard();
  };

  return {
    redirectToDashboard,
    redirectByRole,
  };
};
