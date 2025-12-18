import type { MenuItem } from "@lq/composables";
import { useRoleLayout } from "./useRoleLayout";

export type UserRole = "teacher" | "student" | "admin";

export interface SidebarMenuGroup {
  label: string;
  icon: string;
  items: MenuItem[];
}

export interface SidebarConfig {
  role: UserRole;
  menuGroups: SidebarMenuGroup[];
  menuItems: MenuItem[];
  showLockButton: boolean;
  hasSecondaryNav: boolean;
}

/**
 * Composable that provides sidebar configuration based on user role
 */
export function useSidebarConfig(role: UserRole): SidebarConfig {
  const { withRolePrefix } = useRoleLayout();

  // Teacher configuration
  const teacherConfig: SidebarConfig = {
    role: "teacher",
    showLockButton: true,
    hasSecondaryNav: true,
    menuGroups: [
      {
        label: "Teaching",
        icon: "solar:book-2-linear",
        items: [
          { label: "Dashboard", icon: "solar:home-2-linear", to: withRolePrefix("/dashboard") },
          { label: "Activities", icon: "solar:chat-round-dots-linear", to: withRolePrefix("/activities") },
          { label: "My Classes", icon: "solar:users-group-rounded-linear", to: withRolePrefix("/classes") },
          { label: "Assignments", icon: "solar:clipboard-list-linear", to: withRolePrefix("/assignments") },
          { label: "Grading", icon: "solar:document-text-linear", to: withRolePrefix("/grading"), badge: 12 },
        ],
      },
      {
        label: "Resources",
        icon: "solar:folder-linear",
        items: [
          { label: "Materials", icon: "solar:file-text-linear", to: withRolePrefix("/materials") },
          { label: "Analytics", icon: "solar:chart-2-linear", to: withRolePrefix("/analytics") },
        ],
      },
      {
        label: "Account",
        icon: "solar:user-linear",
        items: [{ label: "Profile", icon: "solar:user-linear", to: withRolePrefix("/profile") }],
      },
      {
        label: "System",
        icon: "solar:settings-linear",
        items: [{ label: "Design System", icon: "solar:palette-linear", to: withRolePrefix("/design-system") }],
      },
    ],
    menuItems: [],
  };

  // Student configuration
  const studentConfig: SidebarConfig = {
    role: "student",
    showLockButton: false,
    hasSecondaryNav: false,
    menuGroups: [],
    menuItems: [
      { label: "Dashboard", icon: "solar:home-2-linear", to: withRolePrefix("/dashboard") },
      { label: "My Courses", icon: "solar:book-linear", to: withRolePrefix("/courses") },
      { label: "Assignments", icon: "solar:clipboard-list-linear", to: withRolePrefix("/assignments") },
      { label: "Progress", icon: "solar:chart-linear", to: withRolePrefix("/progress") },
      { label: "Messages", icon: "solar:chat-round-dots-linear", to: withRolePrefix("/messages"), badge: 3 },
      { label: "Profile", icon: "solar:user-linear", to: withRolePrefix("/profile") },
      { label: "Design System", icon: "solar:palette-linear", to: withRolePrefix("/design-system") },
    ],
  };

  // Admin configuration
  const adminConfig: SidebarConfig = {
    role: "admin",
    showLockButton: false,
    hasSecondaryNav: true,
    menuGroups: [
      {
        label: "Administration",
        icon: "solar:shield-user-linear",
        items: [
          { label: "Dashboard", icon: "solar:home-2-linear", to: withRolePrefix("/dashboard") },
          { label: "Users", icon: "solar:users-group-rounded-linear", to: withRolePrefix("/users") },
          { label: "Institutions", icon: "solar:buildings-linear", to: withRolePrefix("/institutions") },
          { label: "Invitations", icon: "solar:letter-line-duotone", to: withRolePrefix("/invitations") },
        ],
      },
      {
        label: "Content",
        icon: "solar:document-linear",
        items: [
          { label: "Courses", icon: "solar:book-linear", to: withRolePrefix("/courses") },
          { label: "Materials", icon: "solar:file-text-linear", to: withRolePrefix("/materials") },
        ],
      },
      {
        label: "System",
        icon: "solar:settings-linear",
        items: [
          { label: "Settings", icon: "solar:settings-linear", to: withRolePrefix("/settings") },
          { label: "Logs", icon: "solar:document-text-linear", to: withRolePrefix("/logs") },
          { label: "Design System", icon: "solar:palette-linear", to: withRolePrefix("/design-system") },
        ],
      },
    ],
    menuItems: [],
  };

  // Select config based on role
  const configs: Record<UserRole, SidebarConfig> = {
    teacher: teacherConfig,
    student: studentConfig,
    admin: adminConfig,
  };

  const config = configs[role];

  // Flatten menu groups to menu items if needed (for simple/icon-only variants)
  if (config.menuGroups.length > 0 && config.menuItems.length === 0) {
    config.menuItems = config.menuGroups.flatMap((group) => group.items);
  }

  return config;
}
