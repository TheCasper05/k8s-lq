import { computed } from "vue";
import type { InvitationFromAPI } from "~/utils/invitations/types";
import { convertToCSV, downloadCSV } from "~/utils/invitations/invitationExport";
import { useAppToast } from "~/composables/useAppToast";

/**
 * Composable for managing invitation exports
 * @param invitations - Computed list of filtered invitations
 * @param allInvitations - All invitations from stats query
 * @returns Export functions and menu items
 */
export function useInvitationExport(
  invitations: { value: InvitationFromAPI[] },
  allInvitations: () => InvitationFromAPI[],
) {
  const { t } = useI18n();
  const toast = useAppToast();

  /**
   * Exports all invitations to CSV
   */
  const exportAllData = () => {
    const filteredInvitations = allInvitations();

    if (filteredInvitations.length === 0) {
      toast.warning({
        summaryKey: "invitations.messages.exportError",
        detailKey: "invitations.messages.noDataToExport",
      });
      return;
    }

    const csvContent = convertToCSV(filteredInvitations, t);
    const timestamp = new Date().toISOString().split("T")[0];
    downloadCSV(csvContent, `invitations_all_${timestamp}.csv`);

    toast.success({
      summaryKey: "invitations.messages.exportSuccess",
      detail: t("invitations.messages.exportedAll", { count: filteredInvitations.length }),
    });
  };

  /**
   * Exports filtered table data to CSV
   */
  const exportTableData = () => {
    if (invitations.value.length === 0) {
      toast.warning({
        summaryKey: "invitations.messages.exportError",
        detailKey: "invitations.messages.noDataToExport",
      });
      return;
    }

    const csvContent = convertToCSV(invitations.value, t);
    const timestamp = new Date().toISOString().split("T")[0];
    downloadCSV(csvContent, `invitations_table_${timestamp}.csv`);

    toast.success({
      summaryKey: "invitations.messages.exportSuccess",
      detail: t("invitations.messages.exportedTable", { count: invitations.value.length }),
    });
  };

  /**
   * Default export function (exports all data)
   */
  const exportData = () => {
    exportAllData();
  };

  const exportMenuItems = computed(() => [
    {
      label: t("invitations.export.allData"),
      icon: "solar:database-line-duotone",
      command: () => exportAllData(),
    },
    {
      label: t("invitations.export.tableData"),
      icon: "solar:table-line-duotone",
      command: () => exportTableData(),
    },
  ]);

  return {
    exportAllData,
    exportTableData,
    exportData,
    exportMenuItems,
  };
}
