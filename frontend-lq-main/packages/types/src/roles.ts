/**
 * Role Types and Permissions
 *
 * Defines user roles and their associated permissions for the application.
 * Shared across all apps in the monorepo.
 */

import { AccountType } from "./enums";

export interface RolePermissions {
  canAccessDashboard: boolean;
  canManageStudents: boolean;
  canGradeAssignments: boolean;
  canViewAnalytics: boolean;
  canManageInstitution: boolean;
}

export const ROLE_PERMISSIONS: Record<AccountType, RolePermissions> = {
  [AccountType.STUDENT]: {
    canAccessDashboard: true,
    canManageStudents: false,
    canGradeAssignments: false,
    canViewAnalytics: false,
    canManageInstitution: false,
  },
  [AccountType.TEACHER]: {
    canAccessDashboard: true,
    canManageStudents: true,
    canGradeAssignments: true,
    canViewAnalytics: true,
    canManageInstitution: false,
  },
  [AccountType.ADMIN_INSTITUCIONAL]: {
    canAccessDashboard: true,
    canManageStudents: true,
    canGradeAssignments: true,
    canViewAnalytics: true,
    canManageInstitution: true,
  },
};
