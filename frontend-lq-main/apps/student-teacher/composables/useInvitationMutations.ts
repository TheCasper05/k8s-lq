import { ref } from "vue";
import { useMutation } from "@vue/apollo-composable";
import {
  CREATE_INVITATIONS,
  UPDATE_INVITATIONS,
  RESEND_INVITATION,
  type CreateInvitationInput,
  type UpdateInvitationInput,
  type AuthenticationInvitationStatusChoices,
  type CreateInvitationsMutation,
  type UpdateInvitationsMutation,
  type ResendInvitationMutation,
} from "@lq/graphql";
import type { InvitationFromAPI } from "~/utils/invitations/types";
import {
  extractErrorsFromReport,
  extractBulkUploadErrors,
  extractUpdateErrors,
  extractApolloError,
  handleBulkUploadGraphQLError,
} from "~/utils/invitations/errorHandling";
import { fileToBase64 } from "~/utils/invitations/utils";
import { useAppToast } from "~/composables/useAppToast";

type CreateInvitationsResponse = {
  data?: CreateInvitationsMutation;
};

/**
 * Result type for bulk upload operations
 */
export type BulkUploadResult = {
  success: boolean;
  errorMessage?: string;
  hasPartialSuccess?: boolean;
};

/**
 * Composable for managing invitation mutations (create, update, resend, cancel, bulk upload)
 * @param refetch - Function to refetch invitations after mutations
 * @returns Mutation functions and loading states
 */
export function useInvitationMutations(refetch: () => Promise<void>) {
  const { t } = useI18n();
  const toast = useAppToast();

  const { mutate: createInvitations, loading: isCreatingInvitations } = useMutation(CREATE_INVITATIONS);
  const { mutate: updateInvitations } = useMutation(UPDATE_INVITATIONS);
  const { mutate: resendInvitationMutation } = useMutation(RESEND_INVITATION);
  const isBulkUploading = ref(false);

  /**
   * Handles the submission of new invitations
   * @param payload - Array of invitation inputs to create
   * @returns Whether the submission was successful
   */
  const handleInviteSubmit = async (payload: Array<CreateInvitationInput>): Promise<boolean> => {
    try {
      const result = (await createInvitations({
        inputCreateInvitations: payload,
      })) as CreateInvitationsResponse;

      const errorsReport = result?.data?.createInvitations?.errorsReport;
      const createdInvitations = result?.data?.createInvitations?.objects || [];

      if (errorsReport && errorsReport.length > 0) {
        const errorMessages = extractErrorsFromReport(errorsReport, payload, t);
        const successCount = createdInvitations.length;
        const errorCount = errorsReport.length;

        if (successCount > 0) {
          toast.warning({
            summaryKey: "invitations.messages.createError",
            detail: t("invitations.messages.createdPartial", {
              success: successCount,
              error: errorCount,
              details: errorMessages,
            }),
            life: 6000,
          });
        } else {
          toast.error({
            summaryKey: "invitations.messages.createError",
            detail: errorMessages,
            life: 6000,
          });
          return false;
        }
      } else {
        const count = createdInvitations.length;
        toast.success({
          summaryKey: "invitations.messages.createSuccess",
          detail: t("invitations.messages.created", { count }),
        });
      }

      await refetch();
      return true;
    } catch (error) {
      const errorMessage = extractApolloError(error, t, "invitations.messages.genericError");

      toast.error({
        summaryKey: "invitations.messages.createError",
        detail: errorMessage,
        life: 5000,
      });
      return false;
    }
  };

  /**
   * Handles bulk upload of invitations from Excel file
   * @param file - The Excel file to upload
   * @returns Result object with success status and error message if any
   */
  const handleBulkUploadSubmit = async (file: File): Promise<BulkUploadResult> => {
    isBulkUploading.value = true;

    try {
      // Convert file to base64
      const base64File = await fileToBase64(file);

      // Call the mutation with the base64 file
      const result = (await createInvitations({
        file: base64File,
      })) as CreateInvitationsResponse;

      const errorsReport = result?.data?.createInvitations?.errorsReport;
      const createdInvitations = result?.data?.createInvitations?.objects || [];

      // Case 1: Errors in errorsReport (data.createInvitations.errorsReport)
      if (errorsReport && errorsReport.length > 0) {
        const errorMessages = extractBulkUploadErrors(errorsReport, t);
        const successCount = createdInvitations.length;
        const errorCount = errorsReport.length;

        if (successCount > 0) {
          toast.warning({
            summaryKey: "invitations.messages.bulkUploadPartial",
            detail: t("invitations.messages.createdPartialBulk", {
              success: successCount,
              error: errorCount,
              details: errorMessages,
            }),
            life: 8000,
          });
          await refetch();
          return {
            success: true,
            errorMessage: errorMessages,
            hasPartialSuccess: true,
          };
        } else {
          toast.error({
            summaryKey: "invitations.messages.bulkUploadError",
            detail: errorMessages,
            life: 8000,
          });
          await refetch();
          return {
            success: false,
            errorMessage: errorMessages,
            hasPartialSuccess: false,
          };
        }
      }

      // Success case - no errors
      const count = createdInvitations.length;
      if (count > 0) {
        toast.success({
          summaryKey: "invitations.messages.bulkUploadSuccess",
          detail: t("invitations.messages.createdBulk", { count }),
        });

        await refetch();
        return {
          success: true,
          hasPartialSuccess: false,
        };
      }
      return {
        success: false,
        errorMessage: t("invitations.messages.noInvitationsCreated"),
        hasPartialSuccess: false,
      };
    } catch (error) {
      // Case 2: Errors in GraphQL errors array (errors[].message)
      const { errorMessage, hasCorrectRows } = handleBulkUploadGraphQLError(error, t);

      toast.show(hasCorrectRows ? "warn" : "error", {
        summaryKey: hasCorrectRows
          ? "invitations.messages.bulkUploadPartialValidation"
          : "invitations.messages.bulkUploadError",
        detail: errorMessage,
        life: hasCorrectRows ? 8000 : 5000,
      });
      return {
        success: hasCorrectRows,
        errorMessage,
        hasPartialSuccess: hasCorrectRows,
      };
    } finally {
      isBulkUploading.value = false;
    }
  };

  /**
   * Resends an invitation
   * @param invitation - The invitation to resend
   * @returns Whether the modal should be closed
   */
  const resendInvitation = async (invitation: InvitationFromAPI): Promise<boolean> => {
    if (!invitation.id) {
      toast.error({
        summaryKey: "invitations.messages.resendError",
        detailKey: "invitations.messages.invalidInvitation",
      });
      return false;
    }

    try {
      const result = (await resendInvitationMutation({
        invitationId: invitation.id,
      })) as { data?: ResendInvitationMutation };

      const resendResult = result?.data?.resendInvitation;

      if (!resendResult) {
        toast.error({
          summaryKey: "invitations.messages.resendError",
          detailKey: "invitations.messages.genericError",
          life: 5000,
        });
        return false;
      }

      if (resendResult.success) {
        toast.success({
          summaryKey: "invitations.messages.resendSuccess",
          detail: resendResult.message || t("invitations.messages.invitationResent"),
        });
        await refetch();
        return true;
      } else {
        toast.error({
          summaryKey: "invitations.messages.resendError",
          detail: resendResult.message || t("invitations.messages.genericError"),
          life: 5000,
        });
        return true;
      }
    } catch (error) {
      const errorMessage = extractApolloError(error, t, "invitations.messages.genericError");

      toast.error({
        summaryKey: "invitations.messages.resendError",
        detail: errorMessage,
        life: 5000,
      });
      return false;
    }
  };

  /**
   * Cancels (revokes) an invitation
   * @param invitation - The invitation to cancel
   */
  const cancelInvitation = async (invitation: InvitationFromAPI) => {
    if (!invitation.id) {
      toast.error({
        summaryKey: "invitations.messages.cancelError",
        detailKey: "invitations.messages.invalidInvitation",
      });
      return;
    }

    try {
      const updateInput: UpdateInvitationInput = {
        id: invitation.id,
        status: "REVOKED" as AuthenticationInvitationStatusChoices,
      } as UpdateInvitationInput;

      const result = (await updateInvitations({
        inputUpdateInvitations: [updateInput],
      })) as { data?: UpdateInvitationsMutation };

      const errorsReport = result?.data?.updateInvitations?.errorsReport;
      const updatedInvitations = result?.data?.updateInvitations?.objects || [];

      if (errorsReport && errorsReport.length > 0) {
        const errorMessages = extractUpdateErrors(errorsReport, t);

        toast.error({
          summaryKey: "invitations.messages.cancelError",
          detail: errorMessages,
          life: 5000,
        });
        return;
      }

      if (updatedInvitations.length > 0) {
        toast.success({
          summaryKey: "invitations.messages.cancelSuccess",
          detailKey: "invitations.messages.invitationRevoked",
        });
        await refetch();
      }
    } catch (error) {
      const errorMessage = extractApolloError(error, t, "invitations.messages.genericError");

      toast.error({
        summaryKey: "invitations.messages.cancelError",
        detail: errorMessage,
        life: 5000,
      });
    }
  };

  return {
    handleInviteSubmit,
    handleBulkUploadSubmit,
    resendInvitation,
    cancelInvitation,
    isCreatingInvitations,
    isBulkUploading,
  };
}
