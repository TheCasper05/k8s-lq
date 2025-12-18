import { useAuthStore } from "@lq/stores";
import { AccountType } from "@lq/types";
import { getRoleRoutePrefix, getRoleDashboardRoute } from "@lq/utils";

export type SidebarVariant = "icon-only" | "simple" | "grouped" | "static";

export interface RoleLayoutConfig {
  provider: string;
  sidebarVariant: SidebarVariant;
  dashboardRoute: string;
  features: string[];
  permissions: string[];
}

export interface UseRoleLayoutReturn {
  currentRole: ComputedRef<AccountType | null>;
  layoutConfig: ComputedRef<RoleLayoutConfig | null>;
  isStudent: ComputedRef<boolean>;
  isTeacher: ComputedRef<boolean>;
  isAdmin: ComputedRef<boolean>;
  hasFeature: (feature: string) => boolean;
  hasPermission: (permission: string) => boolean;
  withRolePrefix: (path: string) => string;
}

/**
 * Composable for role-based layout configuration
 *
 * @example
 * ```ts
 * const { currentRole, layoutConfig, hasFeature } = useRoleLayout()
 *
 * if (hasFeature('analytics')) {
 *   // Show analytics dashboard
 * }
 * ```
 */
export const useRoleLayout = (): UseRoleLayoutReturn => {
  const authStore = useAuthStore();
  const config = useRuntimeConfig();
  const BYPASS_ONBOARDING = config.public.bypassOnboarding;

  // Current user role from auth store
  const currentRole = computed<AccountType | null>(() => {
    const role = authStore.userProfile?.primaryRole || authStore.userProfileComplete?.primaryRole;

    if (role) {
      return role as AccountType;
    }

    // In bypass mode, fall back to a default role so layout can render
    if (BYPASS_ONBOARDING) {
      return AccountType.TEACHER;
    }

    return null;
  });

  // Role-based layout configuration
  const layoutConfig = computed<RoleLayoutConfig | null>(() => {
    const role = currentRole.value;
    if (!role) return null;

    switch (role) {
      case AccountType.STUDENT:
        return {
          provider: "StudentLayoutProvider",
          sidebarVariant: "simple",
          dashboardRoute: getRoleDashboardRoute(AccountType.STUDENT),
          features: ["notifications", "settings", "messages", "courses"],
          permissions: ["view:courses", "submit:assignments", "view:progress"],
        };

      case AccountType.TEACHER:
        return {
          provider: "TeacherLayoutProvider",
          sidebarVariant: "grouped",
          dashboardRoute: getRoleDashboardRoute(AccountType.TEACHER),
          features: ["notifications", "settings", "messages", "analytics", "grading"],
          permissions: ["view:courses", "create:assignments", "grade:assignments", "view:analytics", "manage:students"],
        };

      case AccountType.ADMIN_INSTITUCIONAL:
        return {
          provider: "AdminLayoutProvider",
          sidebarVariant: "static",
          dashboardRoute: getRoleDashboardRoute(AccountType.ADMIN_INSTITUCIONAL),
          features: ["notifications", "settings", "messages", "analytics", "admin-panel", "user-management"],
          permissions: ["*"], // Admin has all permissions
        };

      default:
        console.warn(`[useRoleLayout] Unknown role: ${role}`);
        return null;
    }
  });

  // Role checks
  const isStudent = computed(() => currentRole.value === AccountType.STUDENT);
  const isTeacher = computed(() => currentRole.value === AccountType.TEACHER);
  const isAdmin = computed(() => currentRole.value === AccountType.ADMIN_INSTITUCIONAL);

  // Feature check
  const hasFeature = (feature: string): boolean => {
    const config = layoutConfig.value;
    if (!config) return false;
    return config.features.includes(feature);
  };

  // Permission check
  const hasPermission = (permission: string): boolean => {
    const config = layoutConfig.value;
    if (!config) return false;

    // Admin has all permissions
    if (config.permissions.includes("*")) return true;

    return config.permissions.includes(permission);
  };

  /**
   * Add role prefix to a route path
   * @param path - Route path without role prefix (e.g., "/dashboard")
   * @returns Path with role prefix (e.g., "/student/dashboard")
   *
   * @example
   * ```ts
   * const { withRolePrefix } = useRoleLayout()
   * const route = withRolePrefix("/dashboard") // "/student/dashboard" for students
   * ```
   */
  const withRolePrefix = (path: string): string => {
    const role = currentRole.value;
    if (!role) return path;

    const prefix = getRoleRoutePrefix(role);

    // If path already starts with a role prefix, return as is
    if (path.startsWith("/student") || path.startsWith("/teacher") || path.startsWith("/admin")) {
      return path;
    }

    // Remove leading slash from path if present
    const cleanPath = path.startsWith("/") ? path.slice(1) : path;

    return `${prefix}/${cleanPath}`;
  };

  return {
    currentRole,
    layoutConfig,
    isStudent,
    isTeacher,
    isAdmin,
    hasFeature,
    hasPermission,
    withRolePrefix,
  };
};
