<script setup lang="ts">
  import { LqNavbar, ThemeToggle, ThemeConfigurator, ThemeConfiguratorContent } from "@lq/ui";
  import { useBreakpoints, breakpointsTailwind } from "@vueuse/core";
  import SchoolDropdown from "~/components/navbar/SchoolDropdown.vue";
  import ActionsPopoverContent from "~/components/navbar/ActionsPopoverContent.vue";
  import NotificationButton from "~/components/navbar/NotificationButton.vue";
  import SettingsButton from "~/components/navbar/SettingsButton.vue";
  import UserAvatarButton from "~/components/navbar/UserAvatarButton.vue";
  import UserProfilePopover from "~/components/profile/UserProfilePopover.vue";
  import type { MenuItem } from "primevue/menuitem";
  import { useAuthStore } from "@lq/stores";
  import Dialog from "primevue/dialog";
  import Popover from "primevue/popover";

  defineOptions({
    name: "AppTopbar",
  });

  interface Props {
    /**
     * Organization/App name to display
     * @default 'Alianza Educativa'
     */
    organizationName?: string;
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
    /**
     * User avatar URL
     * @default undefined
     */
    userAvatar?: string;
    /**
     * Content margin from sidebar
     * @default '0px'
     */
    contentMargin?: string;
  }

  const props = withDefaults(defineProps<Props>(), {
    organizationName: "Alianza Educativa",
    notificationCount: 0,
    settingsBadgeCount: 0,
    userAvatar: undefined,
    contentMargin: "0px",
  });

  const emit = defineEmits<{
    "notificationClick": [];
    "settingsClick": [];
    "userClick": [];
    "schoolSelect": [school: string];
    "toggle-sidebar": [];
  }>();

  const authStore = useAuthStore();
  const { userProfileComplete } = storeToRefs(authStore);

  const breakpoints = useBreakpoints(breakpointsTailwind);
  const isSmallerThanMd = breakpoints.smaller("md"); // < 768px

  const themeConfigurator = ref<InstanceType<typeof ThemeConfigurator>>();
  const userPopover = ref<InstanceType<typeof UserProfilePopover>>();
  const actionsPopover = ref<InstanceType<typeof Popover>>();
  const themeConfiguratorDialogVisible = ref(false);

  // Menu items for the school dropdown - using MenuItem interface
  const menuItems = computed<MenuItem[]>(() => {
    const activeId: string = "dashboard-1"; // This could be reactive based on current route
    return [
      {
        label: "Dashboard",
        icon: "solar:home-2-linear",
        command: () => handleSchoolSelect("dashboard-1"),
        data: { id: "dashboard-1", active: activeId === "dashboard-1" },
      },
      {
        label: "Dashboard",
        icon: "solar:home-2-linear",
        command: () => handleSchoolSelect("dashboard-2"),
        data: { id: "dashboard-2", active: activeId === "dashboard-2" },
      },
      {
        label: "Dashboard",
        icon: "solar:home-2-linear",
        command: () => handleSchoolSelect("dashboard-3"),
        data: { id: "dashboard-3", active: activeId === "dashboard-3" },
      },
      {
        label: "Dashboard",
        icon: "solar:home-2-linear",
        command: () => handleSchoolSelect("dashboard-4"),
        data: { id: "dashboard-4", active: activeId === "dashboard-4" },
      },
      {
        label: "Dashboard",
        icon: "solar:home-2-linear",
        command: () => handleSchoolSelect("dashboard-5"),
        data: { id: "dashboard-5", active: activeId === "dashboard-5" },
      },
    ];
  });

  const userName = computed(() => {
    const { firstName, lastName } = userProfileComplete.value || { firstName: "John", lastName: "Doe" };
    return `${firstName} ${lastName}`;
  });

  const handleSchoolSelect = (itemId: string) => {
    emit("schoolSelect", itemId);
  };

  const toggleSettings = (event?: Event) => {
    // Mobile: open dialog, Desktop: open popover
    if (isSmallerThanMd.value) {
      themeConfiguratorDialogVisible.value = true;
    } else if (event) {
      themeConfigurator.value?.toggle(event);
    }
    emit("settingsClick");
  };

  const toggleActionsPopover = (event: Event) => {
    actionsPopover.value?.toggle(event);
  };

  const handleNotificationClick = () => {
    actionsPopover.value?.hide();
    emit("notificationClick");
  };

  const handleSettingsClickFromPopover = () => {
    actionsPopover.value?.hide();
    toggleSettings();
  };

  const handleUserClick = (event?: MouseEvent) => {
    if (event) {
      userPopover.value?.toggle(event);
    }
    emit("userClick");
  };
</script>

<template>
  <LqNavbar :content-margin="props.contentMargin" @toggle-sidebar="emit('toggle-sidebar')">
    <!-- School Dropdown -->
    <template #start>
      <SchoolDropdown
        :organization-name="organizationName"
        :menu-items="menuItems"
        :show-text="!isSmallerThanMd"
        @select="handleSchoolSelect"
      />
    </template>

    <!-- Custom Actions (Language + Theme for Desktop, MenuBar for Mobile) -->
    <template #actions>
      <!-- Desktop: Language + Theme Toggle -->
      <template v-if="!isSmallerThanMd">
        <LanguageSelector />
        <ThemeToggle />
      </template>

      <!-- Mobile: LanguageSelector + Actions Button -->
      <div v-else class="flex items-center gap-2">
        <LanguageSelector />
        <button
          v-ripple
          type="button"
          :class="[
            'flex items-center gap-3 rounded-lg bg-surface-100 p-2 dark:bg-surface-800/20 transition-colors hover:bg-surface-200 dark:hover:bg-surface-700/30 focus:outline-none',
            'w-10 h-10 justify-center shrink-0',
          ]"
          @click="toggleActionsPopover"
        >
          <Icon name="ant-design:more-outlined" class="size-5 text-surface-500 dark:text-surface-400" />
        </button>
        <Popover ref="actionsPopover">
          <ActionsPopoverContent
            :notification-count="notificationCount"
            :settings-badge-count="settingsBadgeCount"
            @notification-click="handleNotificationClick"
            @settings-click="handleSettingsClickFromPopover"
          />
        </Popover>
      </div>
    </template>

    <!-- Desktop: Notifications with Icon -->
    <template v-if="!isSmallerThanMd" #notifications>
      <NotificationButton :count="notificationCount" @click="emit('notificationClick')">
        <template #icon>
          <Icon name="solar:bell-linear" class="size-5" />
        </template>
      </NotificationButton>
    </template>

    <!-- Desktop: Settings with Icon and ThemeConfigurator -->
    <template v-if="!isSmallerThanMd" #settings>
      <SettingsButton :count="settingsBadgeCount" @click="toggleSettings">
        <template #icon>
          <Icon name="solar:settings-linear" class="size-5" />
        </template>
      </SettingsButton>
      <ThemeConfigurator ref="themeConfigurator" show-primary show-surface show-menu-type />
    </template>

    <!-- User Avatar -->
    <template #user>
      <div class="cursor-pointer" @click="handleUserClick($event)">
        <UserAvatarButton :avatar-url="userAvatar" :user-name="userName" />
      </div>
    </template>
  </LqNavbar>

  <!-- User Profile Popover -->
  <UserProfilePopover ref="userPopover" :user-avatar="userAvatar" />

  <!-- Mobile: Theme Configurator Dialog -->
  <Dialog
    v-model:visible="themeConfiguratorDialogVisible"
    :header="$t('navbar.themeSettings')"
    modal
    dismissable-mask
    :style="{ width: '90vw', maxWidth: '400px' }"
  >
    <ThemeConfiguratorContent
      show-primary
      show-surface
      show-menu-type
      :primary-color-label="$t('themeConfigurator.primaryColor')"
      :surface-color-label="$t('themeConfigurator.surfaceColor')"
      :menu-type-label="$t('themeConfigurator.menuType')"
      :locked-text="$t('themeConfigurator.locked')"
      :menu-type-options="[
        {
          value: 'icon-only',
          label: $t('themeConfigurator.menuTypes.iconOnly.label'),
          description: $t('themeConfigurator.menuTypes.iconOnly.description'),
        },
        {
          value: 'grouped',
          label: $t('themeConfigurator.menuTypes.grouped.label'),
          description: $t('themeConfigurator.menuTypes.grouped.description'),
        },
        {
          value: 'simple',
          label: $t('themeConfigurator.menuTypes.simple.label'),
          description: $t('themeConfigurator.menuTypes.simple.description'),
        },
        {
          value: 'static',
          label: $t('themeConfigurator.menuTypes.static.label'),
          description: $t('themeConfigurator.menuTypes.static.description'),
        },
      ]"
    />
  </Dialog>
</template>
