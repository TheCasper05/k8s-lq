import { ref, computed } from "vue";
import type { CreateInvitationInput } from "@lq/graphql";
import type { LqDataTableColumn } from "@lq/ui";
import type { InvitationFromAPI } from "~/utils/invitations/types";
import { useInvitations } from "~/composables/useInvitations";
import { useInvitationStats } from "~/composables/useInvitationStats";
import { useInvitationMutations } from "~/composables/useInvitationMutations";
import { useInvitationExport } from "~/composables/useInvitationExport";
import { getStatusSeverity } from "~/utils/invitations/invitationFormatters";

export function useInvitationsPage() {
  const { t, locale } = useI18n();

  // Modal states
  const showInviteModal = ref(false);
  const showBulkUploadModal = ref(false);
  const showDetailsModal = ref(false);
  const selectedInvitation = ref<InvitationFromAPI | null>(null);
  const searchQuery = ref("");

  // Bulk upload error state
  const bulkUploadError = ref<string | undefined>(undefined);
  const bulkUploadHasPartialSuccess = ref(false);

  // Composables
  const { invitations, loading, error, refetch } = useInvitations(searchQuery);
  const { statsCards, statsResult } = useInvitationStats();

  // Wrapper for refetch to match expected type
  const refetchInvitations = async () => {
    await refetch();
  };

  const {
    handleInviteSubmit: handleInviteSubmitMutation,
    handleBulkUploadSubmit,
    resendInvitation: resendInvitationMutation,
    cancelInvitation,
    isCreatingInvitations,
    isBulkUploading,
  } = useInvitationMutations(refetchInvitations);

  // Helper function to get all invitations for export
  const getAllInvitations = (): InvitationFromAPI[] => {
    const allInvitations = statsResult.value?.searchInvitations?.objects || [];
    return allInvitations.filter((inv: InvitationFromAPI | null): inv is InvitationFromAPI => inv !== null);
  };

  const { exportData, exportMenuItems } = useInvitationExport(invitations, getAllInvitations);

  // Wrapper for handleInviteSubmit to close modal on success
  const handleInviteSubmit = async (payload: Array<CreateInvitationInput>) => {
    const success = await handleInviteSubmitMutation(payload);
    if (success) {
      showInviteModal.value = false;
    }
  };

  // Wrapper for handleBulkUploadSubmit to handle errors and modal closing
  const handleBulkUploadSubmitWithModal = async (file: File) => {
    const result = await handleBulkUploadSubmit(file);

    // Set error message if there's an error
    if (result.errorMessage) {
      bulkUploadError.value = result.errorMessage;
      bulkUploadHasPartialSuccess.value = result.hasPartialSuccess ?? false;
    } else {
      bulkUploadError.value = undefined;
      bulkUploadHasPartialSuccess.value = false;
    }

    // Close modal only on full success (no errors)
    if (result.success && !result.errorMessage) {
      showBulkUploadModal.value = false;
      bulkUploadError.value = undefined;
      bulkUploadHasPartialSuccess.value = false;
    }
  };

  // Clear bulk upload error
  const clearBulkUploadError = () => {
    bulkUploadError.value = undefined;
    bulkUploadHasPartialSuccess.value = false;
  };

  // Modal handlers
  const viewInvitation = (invitation: InvitationFromAPI) => {
    selectedInvitation.value = invitation;
    showDetailsModal.value = true;
  };

  const closeDetailsModal = () => {
    showDetailsModal.value = false;
    selectedInvitation.value = null;
  };

  const handleDetailsModalVisibility = (value: boolean) => {
    if (!value) {
      closeDetailsModal();
    }
  };

  // Wrapper for resendInvitation to handle modal closing
  const resendInvitation = async (invitation: InvitationFromAPI) => {
    const shouldClose = await resendInvitationMutation(invitation);
    if (shouldClose && showDetailsModal.value) {
      closeDetailsModal();
    }
  };

  // Wrapper for cancelInvitation to handle modal closing
  const cancelInvitationWithModal = async (invitation: InvitationFromAPI) => {
    await cancelInvitation(invitation);
    closeDetailsModal();
  };

  const uploadExcel = () => {
    showBulkUploadModal.value = true;
  };

  // Map stats cards to LqMetricCard format
  const metricsData = computed(() => {
    return statsCards.value.map((stat) => ({
      icon: stat.icon,
      label: stat.label,
      value: `${stat.value}${stat.suffix || ""}`,
      color: stat.color as "primary" | "info" | "success" | "warning" | "danger",
    }));
  });

  // Map status severity to LqTag variant
  const getTagVariant = (invitation: InvitationFromAPI): "primary" | "secondary" | "neutral" | "success" | "info" => {
    const severityMap: Record<string, "primary" | "secondary" | "neutral" | "success" | "info"> = {
      success: "success",
      info: "info",
      warn: "primary",
      warning: "primary",
      danger: "secondary",
      contrast: "neutral",
    };
    const severity = getStatusSeverity(invitation.status);
    return severityMap[severity] || "neutral";
  };

  // Table columns
  const columns = computed<LqDataTableColumn[]>(() => [
    { field: "email", header: t("invitations.table.email") },
    { field: "workspace", header: t("invitations.table.workspace") },
    { field: "role", header: t("invitations.table.role") },
    { field: "status", header: t("invitations.table.status") },
    { field: "createdBy", header: t("invitations.table.invitedBy") },
    { field: "createdAt", header: t("invitations.table.createdAt") },
    { field: "expiresAt", header: t("invitations.table.expiresAt") },
  ]);

  return {
    // State
    showInviteModal,
    showBulkUploadModal,
    showDetailsModal,
    selectedInvitation,
    searchQuery,
    bulkUploadError,
    bulkUploadHasPartialSuccess,

    // Data
    invitations,
    loading,
    error,
    metricsData,
    columns,
    exportMenuItems,

    // Mutations
    isCreatingInvitations,
    isBulkUploading,

    // Methods
    handleInviteSubmit,
    handleBulkUploadSubmitWithModal,
    clearBulkUploadError,
    viewInvitation,
    closeDetailsModal,
    handleDetailsModalVisibility,
    resendInvitation,
    cancelInvitationWithModal,
    uploadExcel,
    refetch,
    exportData,
    getTagVariant,

    // i18n
    t,
    locale,
  };
}
