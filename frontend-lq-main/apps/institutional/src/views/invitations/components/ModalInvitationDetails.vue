<script setup lang="ts">
  import Dialog from "primevue/dialog";
  import Button from "primevue/button";
  import Tag from "primevue/tag";
  import { Icon } from "@iconify/vue";
  import { useI18n } from "vue-i18n";
  import type { InvitationFromAPI } from "../utils/types";
  import { formatDateWithI18n } from "../utils/invitationFormatters";

  const { t, locale } = useI18n();

  // Props
  defineProps<{
    visible: boolean;
    invitation: InvitationFromAPI | null;
  }>();

  // Emits
  defineEmits<{
    "update:visible": [value: boolean];
    "resend": [invitation: InvitationFromAPI];
    "cancel": [invitation: InvitationFromAPI];
  }>();

  // Funciones auxiliares
  const getStatusLabel = (status: string | null | undefined) => {
    if (!status) return t("invitations.status.unknown");
    const labels: Record<string, string> = {
      PENDING: t("invitations.status.pending"),
      ACCEPTED: t("invitations.status.accepted"),
      DECLINED: t("invitations.status.declined"),
      EXPIRED: t("invitations.status.expired"),
      REVOKED: t("invitations.status.revoked"),
    };
    return labels[status] || status;
  };

  const getStatusSeverity = (
    status: string | null | undefined,
  ): "warn" | "success" | "danger" | "secondary" | "info" | "contrast" | undefined => {
    if (!status) return "secondary";
    const severities: Record<string, "warn" | "success" | "danger" | "secondary"> = {
      PENDING: "warn",
      ACCEPTED: "success",
      DECLINED: "danger",
      EXPIRED: "secondary",
      REVOKED: "danger",
    };
    return severities[status] || "secondary";
  };

  const getStatusIcon = (status: string | null | undefined) => {
    if (!status) return "solar:info-circle-line-duotone";
    const icons: Record<string, string> = {
      PENDING: "solar:clock-circle-line-duotone",
      ACCEPTED: "solar:check-circle-line-duotone",
      DECLINED: "solar:close-circle-line-duotone",
      EXPIRED: "solar:calendar-mark-line-duotone",
      REVOKED: "solar:forbidden-circle-line-duotone",
    };
    return icons[status] || "solar:info-circle-line-duotone";
  };

  const getRoleLabel = (role: string) => {
    const labels: Record<string, string> = {
      STUDENT: t("invitations.roles.student"),
      TEACHER: t("invitations.roles.teacher"),
      COORDINATOR: t("invitations.roles.coordinator"),
      ADMIN_INSTITUCIONAL: t("invitations.roles.adminInstitucional"),
      ADMIN_SEDE: t("invitations.roles.adminSede"),
      VIEWER: t("invitations.roles.viewer"),
    };
    return labels[role] || role;
  };
</script>

<template>
  <Dialog
    :visible="visible"
    modal
    :header="$t('invitations.invitationDetails')"
    :style="{ width: '640px', maxWidth: '100%' }"
    @update:visible="$emit('update:visible', $event)"
  >
    <div v-if="invitation" class="flex flex-col gap-6">
      <!-- Correo Electrónico -->
      <div class="flex flex-col gap-1">
        <label class="text-xs text-surface-600">{{ $t("invitations.details.email") }}</label>
        <p class="text-sm text-surface-900">{{ invitation.email }}</p>
      </div>

      <!-- Workspace -->
      <div class="flex flex-col gap-1">
        <label class="text-xs text-surface-600">{{ $t("invitations.details.workspace") }}</label>
        <p class="text-sm text-surface-900">{{ invitation.workspace?.name || "N/A" }}</p>
      </div>

      <!-- Rol Asignado -->
      <div class="flex flex-col gap-1">
        <label class="text-xs text-surface-600">{{ $t("invitations.details.role") }}</label>
        <p class="text-sm text-surface-900">{{ getRoleLabel(invitation.role) }}</p>
      </div>

      <!-- Estado -->
      <div class="flex flex-col gap-1">
        <label class="text-xs text-surface-600">{{ $t("invitations.details.status") }}</label>
        <div class="max-w-fit">
          <Tag
            :value="getStatusLabel(invitation.status)"
            :severity="getStatusSeverity(invitation.status)"
            rounded
            class="px-3! py-2! text-xs! font-semibold! flex items-center gap-1"
          >
            <template #icon>
              <Icon :icon="getStatusIcon(invitation.status)" />
            </template>
          </Tag>
        </div>
      </div>

      <!-- Invitado Por -->
      <div class="flex flex-col gap-1">
        <label class="text-xs text-surface-600">{{ $t("invitations.details.invitedBy") }}</label>
        <p class="text-sm text-surface-900">
          {{
            invitation.createdBy
              ? `${invitation.createdBy.firstName || ""} ${invitation.createdBy.lastName || ""}`.trim() ||
                invitation.createdBy.email
              : "N/A"
          }}
        </p>
      </div>

      <!-- Fechas -->
      <div class="flex gap-8">
        <div class="flex flex-col gap-2 flex-1">
          <label class="text-xs text-surface-600">{{ $t("invitations.details.createdAt") }}</label>
          <p class="text-sm text-surface-900">
            {{ formatDateWithI18n(invitation.createdAt, t, locale) }}
          </p>
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label class="text-xs text-surface-600">{{ $t("invitations.details.expiresAt") }}</label>
          <p class="text-sm text-surface-900">
            {{ formatDateWithI18n(invitation.expiresAt, t, locale) }}
          </p>
        </div>
      </div>

      <!-- Mensaje de Bienvenida -->
      <div v-if="invitation.welcomeMessage" class="flex flex-col gap-2">
        <label class="text-xs text-surface-600">{{ $t("invitations.details.welcomeMessage") }}</label>
        <p class="text-sm text-surface-900 bg-surface-50 p-3 rounded-lg">{{ invitation.welcomeMessage }}</p>
      </div>

      <!-- Revocado por -->
      <div v-if="invitation.revokedBy" class="flex flex-col gap-1">
        <label class="text-xs text-surface-600">{{ $t("invitations.details.revokedBy") }}</label>
        <p class="text-sm text-surface-900">
          {{
            `${invitation.revokedBy.firstName || ""} ${invitation.revokedBy.lastName || ""}`.trim() ||
            invitation.revokedBy.email
          }}
        </p>
      </div>
    </div>

    <!-- Footer -->
    <template #footer>
      <div class="flex justify-end gap-2 w-full">
        <Button
          v-if="invitation?.status === 'PENDING'"
          :label="$t('invitations.actions.resend')"
          severity="secondary"
          @click="$emit('resend', invitation)"
        >
          <template #icon>
            <Icon icon="solar:refresh-line-duotone" />
          </template>
        </Button>
        <Button
          v-if="invitation?.status === 'PENDING'"
          :label="$t('invitations.actions.cancel')"
          severity="danger"
          @click="$emit('cancel', invitation)"
        >
          <template #icon>
            <Icon icon="solar:close-circle-line-duotone" />
          </template>
        </Button>
        <Button :label="$t('common.close')" severity="secondary" @click="$emit('update:visible', false)" />
      </div>
    </template>
  </Dialog>
</template>
