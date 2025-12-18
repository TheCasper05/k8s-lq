<script setup lang="ts">
  import { useLayout, type MenuType } from "@lq/composables";
  import { useBreakpoints, breakpointsTailwind } from "@vueuse/core";
  import { LqSidebar, LqChatSupportTrigger } from "@lq/ui";
  import SidebarHeader from "~/components/sidebar/SidebarHeader.vue";
  import SidebarNavGroup from "~/components/sidebar/SidebarNavGroup.vue";
  import SidebarNavItem from "~/components/sidebar/SidebarNavItem.vue";
  import { useSidebarConfig, type UserRole } from "~/composables/useSidebarConfig";
  import logoCollapsed from "~/assets/images/logo-lq-collapsed.png";

  defineOptions({
    name: "AppSidebar",
  });

  interface Props {
    visible?: boolean;
    position?: "left" | "right";
    variant?: MenuType;
    role?: UserRole;
  }

  const props = withDefaults(defineProps<Props>(), {
    visible: false,
    position: "left",
    variant: undefined,
    role: "student",
  });

  const emit = defineEmits<{
    "update:visible": [value: boolean];
  }>();

  // Get dark mode state and menu type from theme system
  const { menuType: globalMenuType, menuTypeLocked, toggleMenuTypeLock } = useLayout();
  const route = useRoute();
  const breakpoints = useBreakpoints(breakpointsTailwind);
  const isSmallerThanLg = breakpoints.smaller("lg"); // < 1024px

  // Watch route changes to close drawer on navigation (mobile/tablet)
  watch(
    () => route.path,
    () => {
      emit("update:visible", false);
    },
  );

  // Handle close button click
  const handleClose = () => {
    emit("update:visible", false);
  };

  // Get sidebar configuration based on role
  const sidebarConfig = useSidebarConfig(props.role);

  // Current variant - uses prop if provided, otherwise uses global theme setting
  const currentVariant = computed(() => {
    return props.variant ?? globalMenuType.value;
  });

  // Determine if we should use grouped layout (menuGroups) or flat layout (menuItems)
  const useGroupedLayout = computed(() => {
    return (
      sidebarConfig.menuGroups.length > 0 && currentVariant.value !== "simple" && currentVariant.value !== "icon-only"
    );
  });
</script>

<template>
  <LqSidebar
    :visible="visible"
    :position="position"
    :variant="currentVariant"
    :is-menu-locked="menuTypeLocked.value"
    logo-alt="LingoQuesto Logo"
    :has-secondary-nav="sidebarConfig.hasSecondaryNav"
    @toggle-menu-lock="toggleMenuTypeLock"
    @update:visible="emit('update:visible', $event)"
  >
    <!-- Header with Logo and Lock Button -->
    <template #header>
      <SidebarHeader
        logo-alt="LingoQuesto Logo"
        :show-close-button="isSmallerThanLg.value"
        :show-lock-button="sidebarConfig.showLockButton && currentVariant !== 'icon-only'"
        :is-locked="menuTypeLocked.value"
        :lock-tooltip="menuTypeLocked.value ? 'Desbloquear selección de menú' : 'Bloquear selección de menú'"
        @toggle-lock="toggleMenuTypeLock"
        @close="handleClose"
      >
        <template #logo>
          <img src="~/assets/images/logo-lq-grouped.png" alt="LingoQuesto Logo" class="size-auto" />
        </template>
      </SidebarHeader>
    </template>

    <!-- Logo Collapsed (for icon-only variant) -->
    <template #logo-collapsed>
      <img src="~/assets/images/logo-lq-collapsed.png" alt="LingoQuesto Logo" class="size-auto" />
    </template>
    <!-- Collapsed Navigation (not used with Drawer implementation) -->
    <template #navigation-collapsed>
      <SidebarNavGroup icon-only>
        <template v-if="useGroupedLayout">
          <SidebarNavItem
            v-for="item in sidebarConfig.menuItems"
            :key="item.label"
            v-tooltip.right="item.label"
            :to="item.to!"
            :icon="item.icon"
            :badge="item.badge"
            icon-only
          />
        </template>
        <template v-else>
          <SidebarNavItem
            v-for="item in sidebarConfig.menuItems"
            :key="item.label"
            v-tooltip.right="item.label"
            :to="item.to!"
            :icon="item.icon"
            :badge="item.badge"
            icon-only
          />
        </template>
      </SidebarNavGroup>
    </template>

    <!-- Expanded Navigation (Icon-Only/Grouped/Simple/Static variants) -->
    <template #navigation-expanded>
      <!-- Icon-Only Variant -->
      <template v-if="currentVariant === 'icon-only'">
        <SidebarNavGroup icon-only>
          <SidebarNavItem
            v-for="item in sidebarConfig.menuItems"
            :key="item.label"
            v-tooltip.right="item.label"
            :to="item.to!"
            :icon="item.icon"
            :badge="item.badge"
            icon-only
          />
        </SidebarNavGroup>
      </template>

      <!-- Simple Variant -->
      <template v-else-if="currentVariant === 'simple'">
        <SidebarNavGroup>
          <SidebarNavItem
            v-for="item in sidebarConfig.menuItems"
            :key="item.label"
            :to="item.to!"
            :icon="item.icon"
            :label="item.label"
            :badge="item.badge"
          />
        </SidebarNavGroup>
      </template>

      <!-- Grouped Variant -->
      <template v-else-if="currentVariant === 'grouped' && useGroupedLayout">
        <div class="space-y-1">
          <div
            v-for="section in sidebarConfig.menuGroups"
            :key="section.label"
            class="rounded-lg p-2 transition-all duration-200 has-[ul:not(.hidden)]:bg-surface-100 dark:has-[ul:not(.hidden)]:bg-white/5"
          >
            <SidebarNavGroup :label="section.label" :icon="section.icon" collapsible>
              <SidebarNavItem
                v-for="item in section.items"
                :key="item.label"
                :to="item.to!"
                :icon="item.icon"
                :label="item.label"
                :badge="item.badge"
              />
            </SidebarNavGroup>
          </div>
        </div>
      </template>

      <!-- Static Variant -->
      <template v-else-if="currentVariant === 'static' && useGroupedLayout">
        <SidebarNavGroup
          v-for="section in sidebarConfig.menuGroups"
          :key="section.label"
          :label="section.label"
          class="mb-6 last:mb-0"
        >
          <SidebarNavItem
            v-for="item in section.items"
            :key="item.label"
            :to="item.to!"
            :icon="item.icon"
            :label="item.label"
            :badge="item.badge"
            show-active-bar
          />
        </SidebarNavGroup>
      </template>

      <!-- Fallback: Simple layout for grouped/static if no groups defined -->
      <template v-else>
        <SidebarNavGroup>
          <SidebarNavItem
            v-for="item in sidebarConfig.menuItems"
            :key="item.label"
            :to="item.to!"
            :icon="item.icon"
            :label="item.label"
            :badge="item.badge"
          />
        </SidebarNavGroup>
      </template>
    </template>

    <!-- Footer with Chat Trigger -->
    <template #footer>
      <LqChatSupportTrigger :variant="currentVariant" :logo-src="logoCollapsed" />
    </template>
  </LqSidebar>
</template>
