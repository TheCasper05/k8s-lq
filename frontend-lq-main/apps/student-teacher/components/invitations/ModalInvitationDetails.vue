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
        <p class="text-sm text-surface-900">{{ getRoleLabel(invitation.role, t) }}</p>
      </div>

      <!-- Estado -->
      <div class="flex flex-col gap-1">
        <label class="text-xs text-surface-600">{{ $t("invitations.details.status") }}</label>
        <div class="max-w-fit">
          <Tag
            :value="getStatusLabel(invitation.status, t)"
            :severity="getStatusSeverity(invitation.status)"
            rounded
            class="px-3! py-2! text-xs! font-semibold! flex items-center gap-1"
          >
            <template #icon>
              <Icon :name="getStatusIcon(invitation.status)" />
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
            <Icon name="solar:refresh-line-duotone" />
          </template>
        </Button>
        <Button
          v-if="invitation?.status === 'PENDING'"
          :label="$t('invitations.actions.cancel')"
          severity="danger"
          @click="$emit('cancel', invitation)"
        >
          <template #icon>
            <Icon name="solar:close-circle-line-duotone" />
          </template>
        </Button>
        <Button :label="$t('common.close')" severity="secondary" @click="$emit('update:visible', false)" />
      </div>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
  import type { InvitationFromAPI } from "~/utils/invitations/types";
  import {
    formatDateWithI18n,
    getStatusLabel,
    getStatusSeverity,
    getStatusIcon,
    getRoleLabel,
  } from "~/utils/invitations/invitationFormatters";

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
</script>
