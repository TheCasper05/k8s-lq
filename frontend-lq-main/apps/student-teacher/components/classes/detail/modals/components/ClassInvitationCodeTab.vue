<script setup lang="ts">
  import { useI18n } from "vue-i18n";
  import { useToast } from "primevue/usetoast";
  import { useClipboard } from "@vueuse/core";
  import { useAddClassStudents } from "~/composables/classes/useAddClassStudents";

  const emit = defineEmits<{
    "copy-link": [];
  }>();

  const toast = useToast();
  const { t } = useI18n();
  const { invitationCode, inviteLink } = useAddClassStudents();
  const { copy, isSupported } = useClipboard();

  const sendLink = async () => {
    try {
      if (isSupported.value) {
        await copy(inviteLink.value);
      } else {
        // Fallback for browsers that don't support Clipboard API
        const input = document.createElement("input");
        input.value = inviteLink.value;
        document.body.appendChild(input);
        input.select();
        document.execCommand("copy");
        document.body.removeChild(input);
      }

      toast.add({
        severity: "success",
        summary: t("common.success"),
        detail: t("classes.students.linkCopied"),
        life: 3000,
      });
      emit("copy-link");
    } catch {
      toast.add({
        severity: "error",
        summary: t("common.error"),
        detail: t("classes.students.copyFailed"),
        life: 3000,
      });
    }
  };

  const copyCode = async () => {
    try {
      if (isSupported.value) {
        await copy(invitationCode.value);
      } else {
        // Fallback for browsers that don't support Clipboard API
        const input = document.createElement("input");
        input.value = invitationCode.value;
        document.body.appendChild(input);
        input.select();
        document.execCommand("copy");
        document.body.removeChild(input);
      }

      toast.add({
        severity: "success",
        summary: t("common.success"),
        detail: t("classes.students.codeCopied"),
        life: 3000,
      });
    } catch {
      toast.add({
        severity: "error",
        summary: t("common.error"),
        detail: t("classes.students.copyFailed"),
        life: 3000,
      });
    }
  };
</script>

<template>
  <div class="flex flex-col gap-6 py-4">
    <!-- Invite Link Section -->
    <div class="flex flex-col gap-3">
      <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-100">
        {{ $t("classes.students.inviteLink") }}
      </h3>

      <!-- Link Input with Send Button -->
      <div class="flex gap-2">
        <div class="flex-1">
          <InputText :model-value="inviteLink" readonly class="w-full" />
        </div>
        <Button :label="$t('classes.students.send')" variant="secondary" class="flex-shrink-0" @click="sendLink">
          <template #icon>
            <Icon name="solar:copy-line-duotone" />
          </template>
        </Button>
      </div>

      <p class="text-sm text-surface-600 dark:text-surface-400">
        {{ $t("classes.students.shareLinkDescription") }}
      </p>
    </div>

    <!-- Invitation Code Section -->
    <div class="flex flex-col gap-3">
      <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-100">
        {{ $t("classes.students.studentInvitationCode") }}
      </h3>

      <p class="text-sm text-surface-600 dark:text-surface-400">
        {{ $t("classes.students.sendStudentCode") }}
      </p>

      <!-- Code Input with Copy Button Inside -->
      <div class="relative">
        <InputText :model-value="invitationCode" readonly class="w-full pr-24" />
        <button
          type="button"
          class="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1.5 px-3 py-1.5 text-sm text-surface-700 dark:text-surface-300 hover:text-surface-900 dark:hover:text-surface-100 transition-colors"
          @click="copyCode"
        >
          <Icon name="solar:copy-line-duotone" class="text-base" />
          <span>{{ $t("classes.students.copy") }}</span>
        </button>
      </div>
    </div>
  </div>
</template>
