<script setup lang="ts">
  export interface SecuritySectionProps {
    user: {
      twoFactorEnabled: boolean;
    };
  }

  defineProps<SecuritySectionProps>();

  const emit = defineEmits<{
    "change-password": [];
  }>();
</script>

<template>
  <div
    class="bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 p-6 shadow-sm"
  >
    <h3 class="font-bold text-lg text-surface-900 dark:text-surface-100 mb-4">{{ $t("profile.security") }}</h3>

    <div class="space-y-3">
      <!-- Change Password Card -->
      <div
        class="flex items-center justify-between p-4 bg-surface-50 dark:bg-surface-800 rounded-xl cursor-pointer hover:bg-surface-100 dark:hover:bg-surface-700 transition-colors group"
        @click="emit('change-password')"
      >
        <div class="flex items-center gap-4">
          <div
            class="w-10 h-10 rounded-xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center text-purple-600 dark:text-purple-400"
          >
            <Icon name="solar:lock-password-bold-duotone" class="text-xl" />
          </div>
          <div>
            <p class="text-sm font-semibold text-surface-900 dark:text-surface-100">
              {{ $t("profile.changePassword") }}
            </p>
            <p class="text-xs text-surface-500 dark:text-surface-400">{{ $t("profile.updatePassword") }}</p>
          </div>
        </div>
        <Icon
          name="solar:pen-new-square-bold-duotone"
          class="text-surface-400 group-hover:text-purple-600 transition-colors"
        />
      </div>

      <!-- 2FA Card -->
      <div class="flex items-center justify-between p-4 bg-surface-50 dark:bg-surface-800 rounded-xl">
        <div class="flex items-center gap-4">
          <div
            class="w-10 h-10 rounded-xl bg-green-100 dark:bg-green-900/30 flex items-center justify-center text-green-600 dark:text-green-400"
          >
            <Icon name="solar:shield-check-bold-duotone" class="text-xl" />
          </div>
          <div>
            <p class="text-sm font-semibold text-surface-900 dark:text-surface-100">
              {{ $t("profile.twoFactorAuth") }}
            </p>
            <p class="text-xs text-surface-500 dark:text-surface-400">{{ $t("profile.additionalProtection") }}</p>
          </div>
        </div>
        <Badge
          :value="user.twoFactorEnabled ? $t('profile.active') : $t('profile.comingSoon')"
          :severity="user.twoFactorEnabled ? 'success' : 'secondary'"
          class="!text-xs !px-2 !py-0.5"
        />
      </div>
    </div>
  </div>
</template>
