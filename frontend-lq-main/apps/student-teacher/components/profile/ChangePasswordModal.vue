<script setup lang="ts">
  import { ref, computed } from "vue";

  const props = defineProps<{
    visible: boolean;
  }>();

  const emit = defineEmits<{
    "update:visible": [value: boolean];
    "submit": [data: { currentPassword: string; newPassword: string }];
  }>();

  const currentPassword = ref("");
  const newPassword = ref("");
  const confirmPassword = ref("");

  const show = computed({
    get: () => props.visible,
    set: (value) => emit("update:visible", value),
  });

  // Validation rules
  const hasMinLength = computed(() => newPassword.value.length >= 8);
  const hasUpperCase = computed(() => /[A-Z]/.test(newPassword.value));
  const hasNumber = computed(() => /\d/.test(newPassword.value));
  const passwordsMatch = computed(() => newPassword.value && newPassword.value === confirmPassword.value);

  const isValid = computed(
    () =>
      hasMinLength.value &&
      hasUpperCase.value &&
      hasNumber.value &&
      passwordsMatch.value &&
      currentPassword.value.length > 0,
  );

  const handleSubmit = () => {
    if (isValid.value) {
      emit("submit", {
        currentPassword: currentPassword.value,
        newPassword: newPassword.value,
      });
      show.value = false;
      // Reset fields
      currentPassword.value = "";
      newPassword.value = "";
      confirmPassword.value = "";
    }
  };

  const handleCancel = () => {
    show.value = false;
  };
</script>

<template>
  <Dialog
    v-model:visible="show"
    modal
    :style="{ width: '450px' }"
    :pt="{
      root: { class: '!rounded-2xl !shadow-2xl !border-0' },
      header: { class: '!p-6 !pb-2 !rounded-t-2xl' },
      content: { class: '!p-6 !pt-4' },
    }"
  >
    <!-- Custom Header -->
    <template #header>
      <div class="flex items-center gap-3 w-full">
        <div
          class="w-10 h-10 rounded-xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center text-purple-600 dark:text-purple-400"
        >
          <Icon name="solar:lock-password-bold-duotone" class="text-xl" />
        </div>
        <span class="text-xl font-bold text-surface-900 dark:text-surface-100">{{ $t("profile.changePassword") }}</span>
      </div>
    </template>

    <div class="flex flex-col gap-5">
      <!-- Current Password -->
      <div class="flex flex-col gap-2">
        <label class="text-sm font-semibold text-surface-700 dark:text-surface-300">
          {{ $t("profile.currentPassword") }}
        </label>
        <InputText
          v-model="currentPassword"
          type="password"
          :placeholder="$t('profile.currentPasswordPlaceholder')"
          class="w-full !rounded-xl !py-3"
        />
      </div>

      <!-- New Password -->
      <div class="flex flex-col gap-2">
        <label class="text-sm font-semibold text-surface-700 dark:text-surface-300">
          {{ $t("profile.newPassword") }}
        </label>
        <InputText
          v-model="newPassword"
          type="password"
          :placeholder="$t('profile.newPasswordPlaceholder')"
          class="w-full !rounded-xl !py-3"
        />
      </div>

      <!-- Confirm Password -->
      <div class="flex flex-col gap-2">
        <label class="text-sm font-semibold text-surface-700 dark:text-surface-300">
          {{ $t("profile.confirmPassword") }}
        </label>
        <InputText
          v-model="confirmPassword"
          type="password"
          :placeholder="$t('profile.confirmPasswordPlaceholder')"
          class="w-full !rounded-xl !py-3"
        />
      </div>

      <!-- Validation Box -->
      <div class="bg-purple-50 dark:bg-purple-900/20 border border-purple-100 dark:border-purple-800 rounded-xl p-4">
        <p class="text-sm font-bold text-purple-600 dark:text-purple-400 mb-2">
          {{ $t("profile.passwordRequirements") }}
        </p>
        <ul class="space-y-1">
          <li class="flex items-center gap-2 text-xs text-surface-600 dark:text-surface-400">
            <Icon
              name="solar:record-circle-bold-duotone"
              class="text-[10px]"
              :class="hasMinLength ? 'text-purple-500' : 'text-surface-300'"
            />
            <span>{{ $t("profile.minCharacters") }}</span>
          </li>
          <li class="flex items-center gap-2 text-xs text-surface-600 dark:text-surface-400">
            <Icon
              name="solar:record-circle-bold-duotone"
              class="text-[10px]"
              :class="hasUpperCase ? 'text-purple-500' : 'text-surface-300'"
            />
            <span>{{ $t("profile.uppercase") }}</span>
          </li>
          <li class="flex items-center gap-2 text-xs text-surface-600 dark:text-surface-400">
            <Icon
              name="solar:record-circle-bold-duotone"
              class="text-[10px]"
              :class="hasNumber ? 'text-purple-500' : 'text-surface-300'"
            />
            <span>{{ $t("profile.number") }}</span>
          </li>
        </ul>
      </div>

      <!-- Actions -->
      <div class="flex gap-3 mt-2">
        <Button
          :label="$t('profile.cancel')"
          severity="secondary"
          class="flex-1 !bg-surface-200 dark:!bg-surface-700 !text-surface-700 dark:!text-surface-200 !border-0 !rounded-xl !py-3 !font-bold hover:!bg-surface-300"
          @click="handleCancel"
        />
        <Button
          :label="$t('profile.update')"
          class="flex-1 !bg-purple-600 !border-purple-600 !text-white !rounded-xl !py-3 !font-bold hover:!bg-purple-700"
          :disabled="!isValid"
          @click="handleSubmit"
        />
      </div>
    </div>
  </Dialog>
</template>
