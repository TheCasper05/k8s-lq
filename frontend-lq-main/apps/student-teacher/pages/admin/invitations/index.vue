<script setup lang="ts">
  import { LqMetricCard, LqBanner, LqCard, LqTag, LqDataTable } from "@lq/ui";
  import IconField from "primevue/iconfield";
  import InputIcon from "primevue/inputicon";
  import Button from "primevue/button";
  import SplitButton from "primevue/splitbutton";
  import InputText from "primevue/inputtext";
  import ProgressSpinner from "primevue/progressspinner";
  import Message from "primevue/message";
  import ModalNewInvitation from "~/components/invitations/ModalNewInvitation.vue";
  import ModalInvitationDetails from "~/components/invitations/ModalInvitationDetails.vue";
  import ModalBulkUpload from "~/components/invitations/ModalBulkUpload.vue";
  import { downloadInvitationTemplate } from "~/utils/invitations/utils";
  import {
    getRoleLabel,
    getStatusLabel,
    formatExpirationDate,
    formatDateWithI18n,
  } from "~/utils/invitations/invitationFormatters";
  import { useInvitationsPage } from "~/composables/admin/invitations/useInvitationsPage";

  definePageMeta({
    layout: "app",
  });

  const {
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
  } = useInvitationsPage();
</script>

<template>
  <div class="p-6">
    <div>
      <!-- Stats Cards -->
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

      <!-- Modals -->
      <ModalNewInvitation
        :visible="showInviteModal"
        :loading="isCreatingInvitations"
        @update:visible="(value) => (showInviteModal = value)"
        @submit="handleInviteSubmit"
      />

      <ModalBulkUpload
        :visible="showBulkUploadModal"
        :loading="isBulkUploading"
        :error-message="bulkUploadError"
        :has-partial-success="bulkUploadHasPartialSuccess"
        @update:visible="
          (value) => {
            showBulkUploadModal = value;
            if (!value) {
              bulkUploadError = undefined;
              bulkUploadHasPartialSuccess = false;
            }
          }
        "
        @submit="handleBulkUploadSubmitWithModal"
        @clear-error="clearBulkUploadError"
      />

      <ModalInvitationDetails
        :visible="showDetailsModal"
        :invitation="selectedInvitation"
        @update:visible="handleDetailsModalVisibility"
        @resend="resendInvitation"
        @cancel="cancelInvitationWithModal"
      />

      <!-- Banner -->
      <section class="mb-6">
        <LqBanner :title="t('invitations.title')" :description="t('invitations.description')">
          <template #icon>
            <div class="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center">
              <svg
                class="w-10 h-10 text-white"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
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
                :label="t('invitations.actions.downloadTemplate')"
                unstyled
                class="bg-white/10 hover:bg-white/20 border border-white/30 text-white px-3 py-2 rounded-xl font-medium transition-all flex items-center justify-center gap-2"
                @click="downloadInvitationTemplate"
              >
                <template #icon>
                  <Icon name="solar:document-text-line-duotone" />
                </template>
              </Button>

              <Button
                :label="t('invitations.actions.uploadExcel')"
                unstyled
                class="bg-white/10 hover:bg-white/20 border border-white/30 text-white px-3 py-2 rounded-xl font-medium transition-all flex items-center justify-center gap-2"
                @click="uploadExcel"
              >
                <template #icon>
                  <Icon name="solar:upload-line-duotone" />
                </template>
              </Button>

              <Button
                :label="t('invitations.actions.inviteUser')"
                unstyled
                class="bg-white text-primary-600 dark:text-primary-700 hover:bg-surface-50 px-3 py-2 rounded-xl font-bold shadow-lg transition-all flex items-center justify-center gap-2"
                @click="showInviteModal = true"
              >
                <template #icon>
                  <Icon name="solar:add-circle-line-duotone" class="text-xs" />
                </template>
              </Button>
            </div>
          </template>
        </LqBanner>
      </section>

      <!-- Search and Export -->
      <section class="mb-6">
        <div class="flex items-center gap-4">
          <div class="flex-1 relative">
            <IconField>
              <InputIcon>
                <Icon name="solar:magnifer-line-duotone" class="text-surface-700 dark:text-surface-300" />
              </InputIcon>
              <InputText
                v-model="searchQuery"
                :placeholder="t('invitations.actions.searchPlaceholder')"
                class="w-full rounded-xl border-surface-200 bg-surface-50 dark:bg-surface-900 dark:border-surface-800"
              />
            </IconField>
          </div>

          <div class="relative">
            <SplitButton
              :label="t('invitations.actions.export')"
              :model="exportMenuItems"
              severity="success"
              @click="exportData"
            >
              <template #icon>
                <Icon name="solar:download-line-duotone" />
              </template>
              <template #dropdownicon>
                <Icon name="solar:alt-arrow-down-line-duotone" class="text-sm" />
              </template>
            </SplitButton>
          </div>
        </div>
      </section>

      <!-- Data Table -->
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
                {{ t("invitations.messages.loading") }}
              </p>
            </div>
          </div>

          <!-- Error State -->
          <div v-else-if="error" class="p-6">
            <Message severity="error" :closable="false">
              <div class="flex flex-col gap-2">
                <span class="font-semibold">{{ t("invitations.messages.loadError") }}</span>
                <span class="text-sm">{{ error.message }}</span>
                <Button :label="t('invitations.actions.retry')" class="mt-2 w-fit" @click="refetch()">
                  <template #icon>
                    <Icon name="solar:refresh-line-duotone" />
                  </template>
                </Button>
              </div>
            </Message>
          </div>

          <!-- Empty State -->
          <div v-else-if="invitations.length === 0" class="flex flex-col items-center justify-center py-20 px-6">
            <div
              class="w-24 h-24 bg-surface-50 dark:bg-surface-800 rounded-full flex items-center justify-center mb-6"
            >
              <Icon name="solar:inbox-line-duotone" class="text-5xl text-surface-400 dark:text-surface-500" />
            </div>
            <h3 class="text-xl font-bold text-surface-900 dark:text-surface-50 mb-2">
              {{ t("invitations.empty.title") }}
            </h3>
            <p class="text-surface-600 dark:text-surface-400 text-center mb-6 max-w-md">
              {{ t("invitations.empty.description") }}
            </p>
            <Button
              :label="t('invitations.actions.inviteUser')"
              class="bg-primary-600 dark:bg-primary-700 text-white px-6 py-3 rounded-xl font-bold shadow-lg hover:bg-primary-700 dark:hover:bg-primary-600 transition-all"
              @click="showInviteModal = true"
            >
              <template #icon>
                <Icon name="solar:add-circle-line-duotone" />
              </template>
            </Button>
          </div>

          <!-- Data Table -->
          <LqDataTable v-else :data="invitations" :columns="columns" :loading="false" class="text-sm">
            <template #cell-email="{ data }">
              <span class="text-surface-900 dark:text-surface-100 font-medium">{{ data.email }}</span>
            </template>

            <template #cell-workspace="{ data }">
              <span class="text-surface-700 dark:text-surface-300">{{ data.workspace?.name || "N/A" }}</span>
            </template>

            <template #cell-role="{ data }">
              <span class="text-surface-700 dark:text-surface-300">{{ getRoleLabel(data.role, t) }}</span>
            </template>

            <template #cell-status="{ data }">
              <div class="flex justify-center">
                <LqTag :label="getStatusLabel(data.status, t)" :variant="getTagVariant(data)" />
              </div>
            </template>

            <template #cell-createdBy="{ data }">
              <span class="text-surface-700 dark:text-surface-300">
                {{
                  data.createdBy
                    ? `${data.createdBy.firstName || ""} ${data.createdBy.lastName || ""}`.trim() ||
                      data.createdBy.email
                    : "N/A"
                }}
              </span>
            </template>

            <template #cell-createdAt="{ data }">
              <span class="text-surface-700 dark:text-surface-300">
                {{ formatDateWithI18n(data.createdAt, t, locale) }}
              </span>
            </template>

            <template #cell-expiresAt="{ data }">
              <div v-if="data.expiresAt" class="font-semibold text-sm">
                <div class="text-warning-600">{{ formatExpirationDate(data.expiresAt, t).day }}</div>
                <div class="text-warning-600">{{ formatExpirationDate(data.expiresAt, t).month }}</div>
                <div class="text-warning-600">{{ formatExpirationDate(data.expiresAt, t).year }}</div>
              </div>
            </template>

            <template #actions="{ data }">
              <div class="flex items-center gap-2">
                <Button unstyled class="w-8 h-8" @click="viewInvitation(data)">
                  <template #icon>
                    <Icon name="solar:eye-line-duotone" />
                  </template>
                </Button>

                <Button
                  v-if="data.status === 'PENDING'"
                  unstyled
                  class="w-8 h-8 text-primary-600"
                  @click="resendInvitation(data)"
                >
                  <template #icon>
                    <Icon name="solar:refresh-line-duotone" />
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
                    <Icon name="solar:close-circle-line-duotone" />
                  </template>
                </Button>
              </div>
            </template>
          </LqDataTable>
        </LqCard>
      </section>
    </div>
  </div>
</template>
