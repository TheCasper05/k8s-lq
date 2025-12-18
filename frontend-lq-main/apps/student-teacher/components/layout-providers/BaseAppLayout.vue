<script setup lang="ts">
  import AppBreadcrumb from "../AppBreadcrumb.vue";
  import Sidebar from "~/components/Sidebar.vue";
  import { useSidebar } from "~/composables/useSidebar";
  import { useLayout, type MenuType } from "@lq/composables";
  import { useBreakpoints, breakpointsTailwind } from "@vueuse/core";
  import { LqChatSupport, type ChatTranslations } from "@lq/ui";
  import logoCollapsed from "~/assets/images/logo-lq-collapsed.png";
  import botAvatar from "~/assets/images/lq-person-with-glasses.png";

  interface Props {
    sidebarVariant?: MenuType;
    sidebarRole?: "teacher" | "student" | "admin";
    topbarTitle?: string;
    topbarNotificationCount?: number;
    topbarSettingsBadgeCount?: number;
    showSidebar?: boolean;
    showTopbar?: boolean;
    showFooter?: boolean;
  }

  const props = withDefaults(defineProps<Props>(), {
    sidebarVariant: "simple",
    sidebarRole: "student",
    topbarTitle: "LingoQuesto",
    topbarNotificationCount: 0,
    topbarSettingsBadgeCount: 0,
    showSidebar: true,
    showTopbar: true,
    showFooter: false,
  });

  const { sidebarVisible, toggleSidebar, contentMargin } = useSidebar();
  const { menuType } = useLayout(props.sidebarRole);
  const { t } = useI18n();
  const breakpoints = useBreakpoints(breakpointsTailwind);
  const isSmallerThanLg = breakpoints.smaller("lg"); // < 1024px

  // Use responsive menu type - disable icon-only on mobile/tablet
  const effectiveSidebarVariant = computed(() => {
    if (isSmallerThanLg.value && menuType.value === "icon-only") {
      return props.sidebarVariant || "simple";
    }
    return menuType.value;
  });

  // Handle sidebar toggle from navbar
  const handleSidebarToggle = () => {
    toggleSidebar();
  };

  const quickActions = [
    "Getting started",
    "Managing classes",
    "Creating scenarios",
    "Student progress",
    "Technical issue",
  ];

  const chatTranslations = computed<ChatTranslations>(() => ({
    title: t("chatSupport.title"),
    subtitle: t("chatSupport.subtitle"),
    welcomeMessage: t("chatSupport.welcomeMessage"),
    placeholder: t("chatSupport.placeholder"),
    disclaimer: t("chatSupport.disclaimer"),
    botResponseSimulated: t("chatSupport.botResponseSimulated"),
    tooltips: {
      refresh: t("chatSupport.tooltips.refresh"),
      minimize: t("chatSupport.tooltips.minimize"),
      close: t("chatSupport.tooltips.close"),
    },
  }));
</script>

<template>
  <div class="base-app-layout relative min-h-screen bg-surface-50 dark:bg-surface-950">
    <!-- Sidebar - Slot allows providers to customize -->
    <ClientOnly v-if="showSidebar">
      <slot name="sidebar">
        <Sidebar v-model:visible="sidebarVisible" :variant="effectiveSidebarVariant" :role="props.sidebarRole" />
      </slot>
    </ClientOnly>

    <!-- Topbar -->
    <ClientOnly v-if="showTopbar">
      <AppTopbar
        :organization-name="topbarTitle"
        :notification-count="topbarNotificationCount"
        :settings-badge-count="topbarSettingsBadgeCount"
        :content-margin="contentMargin"
        @toggle-sidebar="handleSidebarToggle"
      />
    </ClientOnly>

    <!-- Main Content Area -->
    <div class="min-h-screen flex flex-col transition-all duration-300" :style="{ marginLeft: contentMargin }">
      <div class="flex flex-col w-full gap-6 flex-1 p-8 pt-20">
        <AppBreadcrumb />
        <main>
          <slot />
        </main>
      </div>

      <!-- Footer -->
      <ClientOnly v-if="showFooter">
        <AppFooter v-if="false" />
      </ClientOnly>
    </div>

    <!-- Global Toast -->
    <Toast />

    <!-- Chat Support Widget -->
    <ClientOnly>
      <LqChatSupport
        :logo-src="logoCollapsed"
        :bot-avatar-src="botAvatar"
        :quick-actions="quickActions"
        :translations="chatTranslations"
        bot-name="Nova"
      />
    </ClientOnly>
  </div>
</template>
