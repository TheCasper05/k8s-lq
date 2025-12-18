import type { InvitationFromAPI } from "./types";
import {
  formatDateForCSV,
  formatExpirationDateForCSV,
  formatInvitedBy,
  getRoleLabel,
  getStatusLabel,
} from "./invitationFormatters";

/**
 * Escapes CSV values to handle commas, quotes, and newlines
 * @param value - The value to escape
 * @returns Escaped CSV value
 */
function escapeCSV(value: string): string {
  if (value.includes(",") || value.includes('"') || value.includes("\n")) {
    return `"${value.replace(/"/g, '""')}"`;
  }
  return value;
}

/**
 * Converts invitation data to CSV format
 * @param data - Array of invitations
 * @param t - Translation function
 * @returns CSV content as string
 */
export function convertToCSV(data: InvitationFromAPI[], t: (key: string) => string): string {
  const headers = [
    t("invitations.table.email"),
    t("invitations.table.workspace"),
    t("invitations.table.role"),
    t("invitations.table.status"),
    t("invitations.table.invitedBy"),
    t("invitations.table.createdAt"),
    t("invitations.table.expiresAt"),
  ];

  const rows = data.map((invitation) => {
    return [
      invitation.email || "",
      invitation.workspace?.name || "N/A",
      getRoleLabel(invitation.role, t),
      getStatusLabel(invitation.status, t),
      formatInvitedBy(invitation.createdBy),
      formatDateForCSV(invitation.createdAt, t),
      formatExpirationDateForCSV(invitation.expiresAt, t),
    ];
  });

  const csvContent = [headers.map(escapeCSV).join(","), ...rows.map((row) => row.map(escapeCSV).join(","))].join("\n");

  return csvContent;
}

/**
 * Downloads a CSV file
 * @param csvContent - The CSV content as string
 * @param filename - The filename for the download
 */
export function downloadCSV(csvContent: string, filename: string): void {
  const blob = new Blob(["\uFEFF" + csvContent], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);

  link.setAttribute("href", url);
  link.setAttribute("download", filename);
  link.style.visibility = "hidden";

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  URL.revokeObjectURL(url);
}
