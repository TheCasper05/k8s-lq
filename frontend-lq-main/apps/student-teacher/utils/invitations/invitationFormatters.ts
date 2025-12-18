import type { AuthenticationInvitationStatusChoices } from "@lq/graphql";

/**
 * Configuration object for invitation status labels, severities, and icons
 */
export const invitationStatusConfig = {
  PENDING: {
    label: (t: (key: string) => string) => t("invitations.status.pending"),
    severity: "warn" as const,
    icon: "solar:clock-circle-line-duotone",
  },
  ACCEPTED: {
    label: (t: (key: string) => string) => t("invitations.status.accepted"),
    severity: "success" as const,
    icon: "solar:check-circle-line-duotone",
  },
  DECLINED: {
    label: (t: (key: string) => string) => t("invitations.status.declined"),
    severity: "danger" as const,
    icon: "solar:close-circle-line-duotone",
  },
  EXPIRED: {
    label: (t: (key: string) => string) => t("invitations.status.expired"),
    severity: "secondary" as const,
    icon: "solar:calendar-mark-line-duotone",
  },
  REVOKED: {
    label: (t: (key: string) => string) => t("invitations.status.revoked"),
    severity: "danger" as const,
    icon: "solar:forbidden-circle-line-duotone",
  },
};

/**
 * Configuration object for invitation role labels
 */
export const invitationRoleConfig: Record<string, (t: (key: string) => string) => string> = {
  STUDENT: (t) => t("invitations.roles.student"),
  TEACHER: (t) => t("invitations.roles.teacher"),
  COORDINATOR: (t) => t("invitations.roles.coordinator"),
  ADMIN_INSTITUCIONAL: (t) => t("invitations.roles.adminInstitucional"),
  ADMIN_SEDE: (t) => t("invitations.roles.adminSede"),
  VIEWER: (t) => t("invitations.roles.viewer"),
};

/**
 * Gets the translated label for an invitation status
 * @param status - The invitation status
 * @param t - Translation function
 * @returns Translated status label
 */
export function getStatusLabel(
  status: AuthenticationInvitationStatusChoices | null | undefined,
  t: (key: string) => string,
): string {
  if (!status) return t("invitations.status.unknown");
  return invitationStatusConfig[status]?.label(t) || status;
}

/**
 * Gets the severity for a status tag
 * @param status - The invitation status
 * @returns Severity level for PrimeVue Tag component
 */
export function getStatusSeverity(
  status: AuthenticationInvitationStatusChoices | null | undefined,
): "warn" | "success" | "danger" | "secondary" {
  if (!status) return "secondary";
  return invitationStatusConfig[status]?.severity || "secondary";
}

/**
 * Gets the icon for an invitation status
 * @param status - The invitation status
 * @returns Icon name for Iconify
 */
export function getStatusIcon(status: AuthenticationInvitationStatusChoices | null | undefined): string {
  if (!status) return "solar:info-circle-line-duotone";
  return invitationStatusConfig[status]?.icon || "solar:info-circle-line-duotone";
}

/**
 * Gets the translated label for an invitation role
 * @param role - The invitation role
 * @param t - Translation function
 * @returns Translated role label
 */
export function getRoleLabel(role: string, t: (key: string) => string): string {
  return invitationRoleConfig[role]?.(t) || role;
}

/**
 * Gets the translated short month name
 * @param monthIndex - Month index (0-11)
 * @param t - Translation function
 * @returns Translated short month name
 */
function getMonthShort(monthIndex: number, t: (key: string) => string): string {
  const monthKeys = [
    "invitations.dateFormat.months.short.jan",
    "invitations.dateFormat.months.short.feb",
    "invitations.dateFormat.months.short.mar",
    "invitations.dateFormat.months.short.apr",
    "invitations.dateFormat.months.short.may",
    "invitations.dateFormat.months.short.jun",
    "invitations.dateFormat.months.short.jul",
    "invitations.dateFormat.months.short.aug",
    "invitations.dateFormat.months.short.sep",
    "invitations.dateFormat.months.short.oct",
    "invitations.dateFormat.months.short.nov",
    "invitations.dateFormat.months.short.dec",
  ];
  return t(monthKeys[monthIndex] || monthKeys[0]);
}

/**
 * Converts locale code (e.g., "es") to locale string (e.g., "es-ES")
 * @param localeCode - Locale code from vue-i18n
 * @returns Locale string for date formatting
 */
function getLocaleString(localeCode: string): string {
  const localeMap: Record<string, string> = {
    es: "es-ES",
    en: "en-US",
    fr: "fr-FR",
    de: "de-DE",
    zh: "zh-CN",
    ar: "ar-SA",
  };
  return localeMap[localeCode] || localeCode;
}

/**
 * Formats a date with i18n support
 * @param date - Date string or Date object
 * @param t - Translation function
 * @param localeCode - Locale code from vue-i18n (e.g., "es", "en")
 * @returns Formatted date string
 */
export function formatDateWithI18n(
  date: string | Date | null | undefined,
  t: (key: string) => string,
  localeCode: string | { value: string } = "es",
): string {
  if (!date) return "N/A";
  try {
    const locale = typeof localeCode === "string" ? localeCode : localeCode.value;
    const localeString = getLocaleString(locale);
    const dateObj = typeof date === "string" ? new Date(date) : date;
    return dateObj.toLocaleDateString(localeString);
  } catch {
    return "N/A";
  }
}

/**
 * Formats an expiration date into day, month, and year components with i18n
 * @param date - Date string
 * @param t - Translation function
 * @returns Object with day, month, and year
 */
export function formatExpirationDate(date: string, t: (key: string) => string) {
  const dateObj = new Date(date);
  const day = dateObj.getDate();
  const month = getMonthShort(dateObj.getMonth(), t);
  const year = dateObj.getFullYear();

  return {
    day: day,
    month: month,
    year: year,
  };
}

/**
 * Formats a date for CSV export
 * @param date - Date string or null/undefined
 * @param t - Translation function
 * @param locale - Locale string (optional, defaults to "es-ES")
 * @returns Formatted date string or "N/A"
 */
export function formatDateForCSV(
  date: string | null | undefined,
  t: (key: string) => string,
  locale: string = "es-ES",
): string {
  return formatDateWithI18n(date, t, locale);
}

/**
 * Formats an expiration date for CSV export with i18n
 * @param date - Date string or null/undefined
 * @param t - Translation function
 * @returns Formatted expiration date string or "N/A"
 */
export function formatExpirationDateForCSV(date: string | null | undefined, t: (key: string) => string): string {
  if (!date) return "N/A";
  const dateObj = new Date(date);
  const day = dateObj.getDate();
  const month = getMonthShort(dateObj.getMonth(), t);
  const year = dateObj.getFullYear();
  return `${day} ${month} ${year}`;
}

/**
 * Formats the "invited by" field for display
 * @param createdBy - The user who created the invitation
 * @returns Formatted name string
 */
export function formatInvitedBy(
  createdBy: { firstName?: string | null; lastName?: string | null; email?: string | null } | null | undefined,
): string {
  if (!createdBy) return "N/A";
  const fullName = `${createdBy.firstName || ""} ${createdBy.lastName || ""}`.trim();
  return fullName || createdBy.email || "N/A";
}
