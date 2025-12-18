<script setup lang="ts">
  import { ref, computed } from "vue";
  import { useToast } from "primevue/usetoast";
  import { useClipboard } from "@vueuse/core";
  import { useI18n } from "#imports";

  const emit = defineEmits<{
    "add-students": [];
  }>();

  const toast = useToast();
  const { t } = useI18n();
  const inviteLink = ref("https://app-qa.lingoquest.com/invite/ABC123XYZ");
  const invitationCode = ref("");
  const { copy, isSupported } = useClipboard();

  const isValid = computed(() => {
    return invitationCode.value.trim().length > 0;
  });

  const copyLink = async () => {
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
        detail: t("students.linkCopied"),
        life: 3000,
      });
    } catch {
      toast.add({
        severity: "error",
        summary: t("common.error"),
        detail: t("students.copyFailed"),
        life: 3000,
      });
    }
  };

  const handleAdd = () => {
    if (!isValid.value) {
      toast.add({
        severity: "warn",
        summary: t("common.validationError"),
        detail: t("students.codeRequired"),
        life: 3000,
      });
      return;
    }

    // TODO: Implement actual add logic when backend is ready
    toast.add({
      severity: "success",
      summary: t("common.success"),
      detail: t("students.studentAdded"),
      life: 3000,
    });
    emit("add-students");
  };
</script>

<template>
  <div class="flex flex-col gap-6 py-4">
    <!-- Invite Link Section -->
    <div class="bg-gradient-to-r from-primary-500 to-warning-500 rounded-lg p-0.5">
      <div class="bg-surface-100 dark:bg-surface-900 rounded-[calc(0.5rem-2px)] p-6">
        <div class="flex items-center gap-2 mb-4">
          <Icon name="solar:link-line-duotone" class="text-primary-600 dark:text-primary-400" />
          <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-100">
            {{ $t("students.inviteLink") }}
          </h3>
        </div>

        <!-- Link Input with Copy Button -->
        <div class="flex gap-2 mb-3">
          <div class="flex-1 relative">
            <IconField class="w-full">
              <InputIcon>
                <Icon name="solar:link-line-duotone" />
              </InputIcon>
              <InputText :model-value="inviteLink" readonly class="w-full bg-white dark:bg-surface-800" />
            </IconField>
          </div>
          <Button :label="$t('students.copy')" class="bg-primary-600 hover:bg-primary-700" @click="copyLink">
            <template #icon>
              <Icon name="solar:copy-line-duotone" />
            </template>
          </Button>
        </div>

        <p class="text-sm text-surface-600 dark:text-surface-400">
          {{ $t("students.shareLinkDescription") }}
        </p>
      </div>
    </div>

    <!-- Divider with text -->
    <div class="relative flex items-center justify-center my-4">
      <div class="absolute inset-0 flex items-center">
        <div class="w-full border-t border-surface-200 dark:border-surface-700" />
      </div>
      <div class="relative bg-surface-0 dark:bg-surface-900 px-4">
        <span class="text-sm text-surface-600 dark:text-surface-400">
          {{ $t("students.orEnterInvitationCode") }}
        </span>
      </div>
    </div>

    <!-- Invitation Code Input -->
    <div class="flex flex-col gap-2">
      <label class="text-sm font-medium text-surface-700 dark:text-surface-300">
        {{ $t("students.studentInvitationCode") }}
      </label>
      <InputText v-model="invitationCode" :placeholder="$t('students.enterStudentCode')" class="w-full" />
    </div>

    <!-- Add Button -->
    <div class="flex justify-end pt-4">
      <Button
        :label="$t('students.addStudents')"
        :disabled="!isValid"
        class="bg-primary-600 hover:bg-primary-700"
        @click="handleAdd"
      />
    </div>
  </div>
</template>
