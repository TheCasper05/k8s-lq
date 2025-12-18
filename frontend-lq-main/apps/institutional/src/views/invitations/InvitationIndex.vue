<script setup lang="ts">
  import { ref, computed } from "vue";
  import { useI18n } from "vue-i18n";
  import type { CreateInvitationInput } from "@lq/graphql";
  import IconField from "primevue/iconfield";
  import InputIcon from "primevue/inputicon";
  import DataTable from "primevue/datatable";
  import Column from "primevue/column";
  import Button from "primevue/button";
  import SplitButton from "primevue/splitbutton";
  import InputText from "primevue/inputtext";
  import ProgressSpinner from "primevue/progressspinner";
  import Message from "primevue/message";
  import { Icon } from "@iconify/vue";
  import { LqMetricCard, LqBanner, LqCard, LqTag } from "@lq/ui";
  import ModalNewInvitation from "./components/ModalNewInvitation.vue";
  import ModalInvitationDetails from "./components/ModalInvitationDetails.vue";
  import ModalBulkUpload from "./components/ModalBulkUpload.vue";
  import { downloadInvitationTemplate } from "./utils/utils";
  import type { InvitationFromAPI } from "./utils/types";
  import { useInvitations } from "./composables/useInvitations";
  import { useInvitationStats } from "./composables/useInvitationStats";
  import { useInvitationMutations } from "./composables/useInvitationMutations";
  import { useInvitationExport } from "./composables/useInvitationExport";
  import {
    getStatusLabel,
    getStatusSeverity,
    getRoleLabel,
    formatExpirationDate,
    formatDateWithI18n,
  } from "./utils/invitationFormatters";

  const { t, locale } = useI18n();

  // Modal states
  const showInviteModal = ref(false);
  const showBulkUploadModal = ref(false);
  const showDetailsModal = ref(false);
  const selectedInvitation = ref<InvitationFromAPI | null>(null);
  const searchQuery = ref("");

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

  // Wrapper for handleBulkUploadSubmit to close modal on success (including partial success)
  const handleBulkUploadSubmitWithModal = async (file: File) => {
    const success = await handleBulkUploadSubmit(file);
    // Close modal on any success (full or partial)
    if (success) {
      showBulkUploadModal.value = false;
    }
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
</script>

<template>
  <div class="p-6">
    <div>
      <section class="mb-6">
        <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
          <LqMetricCard
            v-for="(metric, index) in metricsData"
            :key="index"
            :metric="metric"
            variant="boxed"
            label-position="top"
          />
        </div>
      </section>

      <ModalNewInvitation
        :visible="showInviteModal"
        :loading="isCreatingInvitations"
        @update:visible="(value) => (showInviteModal = value)"
        @submit="handleInviteSubmit"
      />

      <ModalBulkUpload
        :visible="showBulkUploadModal"
        :loading="isBulkUploading"
        @update:visible="(value) => (showBulkUploadModal = value)"
        @submit="handleBulkUploadSubmitWithModal"
      />

      <ModalInvitationDetails
        :visible="showDetailsModal"
        :invitation="selectedInvitation"
        @update:visible="handleDetailsModalVisibility"
        @resend="resendInvitation"
        @cancel="cancelInvitationWithModal"
      />

      <section class="mb-6">
        <LqBanner :title="$t('invitations.title')" :description="$t('invitations.description')">
          <template #icon>
            <div class="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center">
              <svg class="w-10 h-10 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                <path d="M16 3.13a4 4 0 0 1 0 7.75" />
              </svg>
            </div>
          </template>
          <template #action>
            <div class="flex items-center gap-3">
              <Button
                :label="$t('invitations.actions.downloadTemplate')"
                unstyled
                class="bg-white/10 hover:bg-white/20 border border-white/30 text-white px-3! py-2! rounded-xl font-medium transition-all flex items-center justify-center gap-2"
                @click="downloadInvitationTemplate"
              >
                <template #icon>
                  <Icon icon="solar:document-text-line-duotone" />
                </template>
              </Button>

              <Button
                :label="$t('invitations.actions.uploadExcel')"
                unstyled
                class="bg-white/10 hover:bg-white/20 border border-white/30 text-white px-3! py-2! rounded-xl font-medium transition-all flex items-center justify-center gap-2"
                @click="uploadExcel"
              >
                <template #icon>
                  <Icon icon="solar:upload-line-duotone" />
                </template>
              </Button>

              <Button
                :label="$t('invitations.actions.inviteUser')"
                unstyled
                class="bg-white text-primary-600 dark:text-primary-700 hover:bg-surface-50 px-3! py-2! rounded-xl font-bold shadow-lg transition-all flex items-center justify-center gap-2"
                @click="showInviteModal = true"
              >
                <template #icon>
                  <Icon icon="solar:add-circle-line-duotone" class="text-xs" />
                </template>
              </Button>
            </div>
          </template>
        </LqBanner>
      </section>

      <section class="mb-6">
        <div class="flex items-center gap-4">
          <div class="flex-1 relative">
            <IconField>
              <InputIcon>
                <Icon icon="solar:magnifer-line-duotone" class="text-surface-700" />
              </InputIcon>
              <InputText
                v-model="searchQuery"
                :placeholder="$t('invitations.actions.searchPlaceholder')"
                class="w-full rounded-xl! border-surface-200! bg-surface-50!"
              />
            </IconField>
          </div>

          <div class="relative">
            <SplitButton
              :label="$t('invitations.actions.export')"
              :model="exportMenuItems"
              severity="success"
              @click="exportData"
            >
              <template #icon>
                <Icon icon="solar:download-line-duotone" />
              </template>
              <template #dropdownicon>
                <Icon icon="solar:alt-arrow-down-line-duotone" class="text-sm" />
              </template>
            </SplitButton>
          </div>
        </div>
      </section>

      <section>
        <LqCard variant="default" padding="p-0">
          <!-- Loading State -->
          <div v-if="loading" class="flex items-center justify-center py-20">
            <div class="text-center">
              <ProgressSpinner
                style="width: 50px; height: 50px"
                stroke-width="4"
                fill="transparent"
                animation-duration="1s"
              />
              <p class="mt-4 text-surface-600 dark:text-surface-400 font-medium">
                {{ $t("invitations.messages.loading") }}
              </p>
            </div>
          </div>

          <!-- Error State -->
          <div v-else-if="error" class="p-6">
            <Message severity="error" :closable="false">
              <div class="flex flex-col gap-2">
                <span class="font-semibold">{{ $t("invitations.messages.loadError") }}</span>
                <span class="text-sm">{{ error.message }}</span>
                <Button :label="$t('invitations.actions.retry')" class="mt-2 w-fit" @click="refetch()">
                  <template #icon>
                    <Icon icon="solar:refresh-line-duotone" />
                  </template>
                </Button>
              </div>
            </Message>
          </div>

          <!-- Empty State -->
          <div v-else-if="invitations.length === 0" class="flex flex-col items-center justify-center py-20 px-6">
            <div class="w-24 h-24 bg-surface-50 dark:bg-surface-800 rounded-full flex items-center justify-center mb-6">
              <Icon icon="solar:inbox-line-duotone" class="text-5xl text-surface-400 dark:text-surface-500" />
            </div>
            <h3 class="text-xl font-bold text-surface-900 dark:text-surface-50 mb-2">
              {{ $t("invitations.empty.title") }}
            </h3>
            <p class="text-surface-600 dark:text-surface-400 text-center mb-6 max-w-md">
              {{ $t("invitations.empty.description") }}
            </p>
            <Button
              :label="$t('invitations.actions.inviteUser')"
              class="bg-primary-600 dark:bg-primary-700 text-white px-6 py-3 rounded-xl font-bold shadow-lg hover:bg-primary-700 dark:hover:bg-primary-600 transition-all"
              @click="showInviteModal = true"
            >
              <template #icon>
                <Icon icon="solar:add-circle-line-duotone" />
              </template>
            </Button>
          </div>

          <!-- Data Table -->
          <DataTable v-else :value="invitations" class="text-sm">
            <Column
              field="email"
              :header="$t('invitations.table.email')"
              class="font-medium"
              :pt="{
                headerCell: { class: 'bg-surface-50 text-center p-4' },
                columnHeaderContent: { class: 'justify-center' },
              }"
            >
              <template #body="{ data }">
                <span class="text-surface-900 font-medium">{{ data.email }}</span>
              </template>
            </Column>

            <Column
              field="workspace"
              :header="$t('invitations.table.workspace')"
              :pt="{
                headerCell: { class: 'bg-surface-50! text-center!' },
                columnHeaderContent: { class: 'justify-center' },
              }"
            >
              <template #body="{ data }">
                <span class="text-surface-700">{{ data.workspace?.name || "N/A" }}</span>
              </template>
            </Column>

            <Column
              field="role"
              :header="$t('invitations.table.role')"
              :pt="{
                headerCell: { class: 'bg-surface-50! text-center!' },
                columnHeaderContent: { class: 'justify-center' },
              }"
            >
              <template #body="{ data }">
                <span class="text-surface-700">{{ getRoleLabel(data.role, t) }}</span>
              </template>
            </Column>

            <Column
              field="status"
              :header="$t('invitations.table.status')"
              :pt="{
                headerCell: { class: 'bg-surface-50! text-center!' },
                columnHeaderContent: { class: 'justify-center' },
              }"
            >
              <template #body="{ data }">
                <div class="flex justify-center">
                  <LqTag :label="getStatusLabel(data.status, t)" :variant="getTagVariant(data)" />
                </div>
              </template>
            </Column>

            <Column
              field="createdBy"
              :header="$t('invitations.table.invitedBy')"
              :pt="{
                headerCell: { class: 'bg-surface-50! text-center!' },
                columnHeaderContent: { class: 'justify-center' },
              }"
            >
              <template #body="{ data }">
                <span class="text-surface-700">
                  {{
                    data.createdBy
                      ? `${data.createdBy.firstName || ""} ${data.createdBy.lastName || ""}`.trim() ||
                        data.createdBy.email
                      : "N/A"
                  }}
                </span>
              </template>
            </Column>

            <Column
              field="createdAt"
              :header="$t('invitations.table.createdAt')"
              :pt="{
                headerCell: { class: 'bg-surface-50 text-center' },
                columnHeaderContent: { class: 'justify-center' },
              }"
            >
              <template #body="{ data }">
                <span class="text-surface-700">
                  {{ formatDateWithI18n(data.createdAt, t, locale) }}
                </span>
              </template>
            </Column>

            <Column
              field="expiresAt"
              :header="$t('invitations.table.expiresAt')"
              :pt="{
                headerCell: { class: 'bg-surface-50 text-center' },
                columnHeaderContent: { class: 'justify-center' },
              }"
            >
              <template #body="{ data }">
                <div v-if="data.expiresAt" class="font-semibold text-sm">
                  <div class="text-warning-600">{{ formatExpirationDate(data.expiresAt, t).day }}</div>
                  <div class="text-warning-600">{{ formatExpirationDate(data.expiresAt, t).month }}</div>
                  <div class="text-warning-600">{{ formatExpirationDate(data.expiresAt, t).year }}</div>
                </div>
              </template>
            </Column>

            <Column
              :header="$t('invitations.table.actions')"
              class="w-32"
              :pt="{
                headerCell: { class: 'bg-surface-50 text-center' },
                columnHeaderContent: { class: 'justify-center' },
              }"
            >
              <template #body="{ data }">
                <div class="flex items-center gap-2">
                  <Button unstyled class="w-8 h-8" @click="viewInvitation(data)">
                    <template #icon>
                      <Icon icon="solar:eye-line-duotone" />
                    </template>
                  </Button>

                  <Button
                    v-if="data.status === 'PENDING'"
                    unstyled
                    class="w-8 h-8 text-primary-600"
                    @click="resendInvitation(data)"
                  >
                    <template #icon>
                      <Icon icon="solar:refresh-line-duotone" />
                    </template>
                  </Button>

                  <Button
                    v-if="data.status === 'PENDING'"
                    unstyled
                    severity="danger"
                    class="w-8 h-8"
                    @click="cancelInvitationWithModal(data)"
                  >
                    <template #icon>
                      <Icon icon="solar:close-circle-line-duotone" />
                    </template>
                  </Button>
                </div>
              </template>
            </Column>
          </DataTable>
        </LqCard>
      </section>
    </div>
  </div>
</template>
