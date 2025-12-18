<script setup lang="ts">
  import { ThemeToggle } from "@lq/ui";

  defineOptions({
    name: "ActionsPopoverContent",
  });

  const { t } = useI18n();

  interface Props {
    /**
     * Notification count badge
     * @default 0
     */
    notificationCount?: number;
    /**
     * Settings badge count
     * @default 0
     */
    settingsBadgeCount?: number;
  }

  withDefaults(defineProps<Props>(), {
    notificationCount: 0,
    settingsBadgeCount: 0,
  });

  const emit = defineEmits<{
    notificationClick: [];
    settingsClick: [];
  }>();

  const handleNotificationClick = () => {
    emit("notificationClick");
  };

  const handleSettingsClick = () => {
    emit("settingsClick");
  };
</script>

<template>
  <div class="flex flex-col p-1 min-w-[150px]">
    <!-- Theme Toggle -->
    <div
      class="flex items-center justify-between px-2 py-1 rounded-lg hover:bg-surface-100 dark:hover:bg-surface-800/50 transition-colors"
    >
      <span class="text-sm font-medium text-surface-700 dark:text-surface-200">{{ t("navbar.theme") }}</span>
      <ThemeToggle />
    </div>

    <!-- Separator -->
    <div class="my-1 border-t border-surface-200 dark:border-surface-700" />

    <!-- Notifications Button -->
    <button
      class="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-surface-100 dark:hover:bg-surface-800/50 transition-colors text-left w-full"
      @click="handleNotificationClick"
    >
      <div class="relative">
        <Icon name="solar:bell-linear" class="size-5 text-surface-600 dark:text-surface-400" />
        <span
          v-if="notificationCount > 0"
          class="absolute -top-1.5 -right-1.5 flex items-center justify-center min-w-[18px] h-[18px] px-1 text-[10px] font-semibold text-white bg-primary-500 rounded-full"
        >
          {{ notificationCount > 99 ? "99+" : notificationCount }}
        </span>
      </div>
      <span class="text-sm font-medium text-surface-700 dark:text-surface-200">{{ t("navbar.notifications") }}</span>
    </button>

    <!-- Settings Button -->
    <button
      class="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-surface-100 dark:hover:bg-surface-800/50 transition-colors text-left w-full"
      @click="handleSettingsClick"
    >
      <div class="relative">
        <Icon name="solar:settings-linear" class="size-5 text-surface-600 dark:text-surface-400" />
        <span
          v-if="settingsBadgeCount > 0"
          class="absolute -top-1.5 -right-1.5 flex items-center justify-center min-w-[18px] h-[18px] px-1 text-[10px] font-semibold text-white bg-primary-500 rounded-full"
        >
          {{ settingsBadgeCount > 99 ? "99+" : settingsBadgeCount }}
        </span>
      </div>
      <span class="text-sm font-medium text-surface-700 dark:text-surface-200">{{ t("navbar.settings") }}</span>
    </button>
  </div>
</template>
