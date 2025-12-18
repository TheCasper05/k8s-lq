import { AccountType } from "./enums";

/**
 * Map of user roles to their dashboard routes
 */
export const ROLE_DASHBOARD_ROUTES: Record<AccountType, string> = {
  [AccountType.STUDENT]: "/student/dashboard",
  [AccountType.TEACHER]: "/teacher/dashboard",
  [AccountType.ADMIN_INSTITUCIONAL]: "/admin/dashboard",
};

/**
 * Map of user roles to their route prefixes
 */
export const ROLE_ROUTE_PREFIXES: Record<AccountType, string> = {
  [AccountType.STUDENT]: "/student",
  [AccountType.TEACHER]: "/teacher",
  [AccountType.ADMIN_INSTITUCIONAL]: "/admin",
};

/**
 * Authentication route constants
 * Centralized definition of all authentication-related routes
 */
export const AUTH_ROUTES = {
  LOGIN: "/auth/login",
  LOGIN_EMAIL: "/auth/login/email",
  FORGOT_PASSWORD: "/auth/forgot-password",
  FORGOT_PASSWORD_CHECK_EMAIL: "/auth/forgot-password/check-email",
  FORGOT_PASSWORD_RESET: "/auth/forgot-password/reset",
  REGISTER: "/auth/register",
  REGISTER_VERIFY_EMAIL: "/auth/verify-email",
  REGISTER_ACCOUNT_TYPE: "/auth/register/account-type",
  REGISTER_LANGUAGE_PREFS: "/auth/register/language-preferences",
  REGISTER_PERSONAL_INFO: "/auth/register/personal-info",
  REGISTER_INSTITUTION_INFO: "/auth/register/institution-info",
  GOOGLE_CALLBACK: "/auth/google/callback",
  MICROSOFT_CALLBACK: "/auth/microsoft/callback",
} as const;

/**
 * Onboarding flow pages
 * These pages are part of the user registration/onboarding process
 */
export const ONBOARDING_PAGES = [
  AUTH_ROUTES.REGISTER_ACCOUNT_TYPE,
  AUTH_ROUTES.REGISTER_LANGUAGE_PREFS,
  AUTH_ROUTES.REGISTER_PERSONAL_INFO,
  AUTH_ROUTES.REGISTER_INSTITUTION_INFO,
] as const;

/**
 * Protected auth pages that require active flow (no direct access/refresh)
 * Users must navigate to these pages through the proper flow
 */
export const PROTECTED_AUTH_PAGES = [AUTH_ROUTES.LOGIN_EMAIL, ...ONBOARDING_PAGES] as const;

/**
 * Public auth pages that don't require authentication
 * These pages can be accessed by unauthenticated users
 */
export const PUBLIC_AUTH_PAGES = [
  AUTH_ROUTES.LOGIN,
  AUTH_ROUTES.LOGIN_EMAIL,
  AUTH_ROUTES.FORGOT_PASSWORD,
  AUTH_ROUTES.FORGOT_PASSWORD_CHECK_EMAIL,
  AUTH_ROUTES.FORGOT_PASSWORD_RESET,
  AUTH_ROUTES.REGISTER,
  AUTH_ROUTES.REGISTER_VERIFY_EMAIL,
  AUTH_ROUTES.GOOGLE_CALLBACK,
  AUTH_ROUTES.MICROSOFT_CALLBACK,
  ...ONBOARDING_PAGES,
] as const;
