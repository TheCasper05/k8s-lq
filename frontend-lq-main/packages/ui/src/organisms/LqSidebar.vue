<script setup lang="ts">
  import { computed } from "vue";
  import { useBreakpoints, breakpointsTailwind } from "@vueuse/core";
  import Drawer from "primevue/drawer";
  import { useLayout } from "@lq/composables";

  interface Props {
    visible?: boolean;
    position?: "left" | "right";
    variant?: "icon-only" | "grouped" | "simple" | "static";
    isMenuLocked?: boolean;
    logoCollapsed?: string;
    logoExpanded?: string;
    logoAlt?: string;
    hasSecondaryNav?: boolean;
  }

  const props = withDefaults(defineProps<Props>(), {
    visible: true,
    position: "left",
    variant: "simple",
    isMenuLocked: false,
    logoCollapsed: undefined,
    logoExpanded: undefined,
    logoAlt: "Logo",
    hasSecondaryNav: false,
  });

  const emit = defineEmits<{
    "toggle-menu-lock": [];
    "update:visible": [value: boolean];
  }>();

  const { isDarkMode } = useLayout();
  const breakpoints = useBreakpoints(breakpointsTailwind);
  const isSmallerThanLg = breakpoints.smaller("lg"); // < 1024px
  const isSmallerThanMd = breakpoints.smaller("md"); // < 768px

  const isIconOnlyVariant = computed(() => props.variant === "icon-only");

  // Handle drawer visibility
  const handleDrawerHide = () => {
    emit("update:visible", false);
  };

  // Sidebar width based on variant and screen size
  const sidebarWidth = computed(() => {
    // Mobile (< 768px): full width
    if (isSmallerThanMd.value) {
      return "100%";
    }
    // Tablet (768px - 1023px): 25% width
    if (isSmallerThanLg.value) {
      return "30%";
    }
    // Desktop (>= 1024px): Icon-only variant uses narrow width
    return props.variant === "icon-only" ? "65px" : "290px";
  });

  // Gradient backgrounds V3
  const sidebarBackground = computed(() => {
    return isDarkMode.value
      ? "linear-gradient(180deg, #2E323F 0%, #0A061A 100%)"
      : "linear-gradient(180deg, #FAFBFC 0%, #F6F8FA 100%)";
  });
</script>

<template>
  <!-- Mobile/Tablet: Drawer (controlled by visible prop) -->
  <Drawer
    v-if="isSmallerThanLg"
    :visible="visible"
    :position="position"
    :show-close-icon="false"
    :pt="{
      root: { class: 'rounded-r-[24px] overflow-hidden' },
      content: { class: 'p-0 h-full' },
    }"
    :style="{
      width: sidebarWidth,
      background: sidebarBackground,
    }"
    @update:visible="handleDrawerHide"
  >
    <!-- Sidebar Content -->
    <div class="relative z-10 flex h-full flex-col">
      <!-- Icon-Only Variant (looks like collapsed but uses expanded navigation) -->
      <template v-if="isIconOnlyVariant">
        <div class="flex h-full flex-col items-center py-4">
          <!-- Logo Icon -->
          <div class="mb-6 flex items-center justify-center">
            <slot name="logo-collapsed">
              <img v-if="logoCollapsed" :src="logoCollapsed" :alt="logoAlt" class="size-auto" />
            </slot>
          </div>

          <div class="h-px w-12 mb-4" :class="isDarkMode ? 'bg-white/10' : 'bg-black/10'" />

          <!-- Icon-Only Navigation (all items from expanded navigation) -->
          <slot name="navigation-expanded" />

          <!-- Footer -->
          <div class="mt-auto pb-4">
            <slot name="footer" />
          </div>
        </div>
      </template>

      <!-- Full Width Variants (Grouped, Simple, Static) -->
      <template v-else>
        <div class="flex h-full flex-col">
          <!-- Header Slot -->
          <slot name="header" />

          <div class="h-px mx-6 mb-4" :class="isDarkMode ? 'bg-white/10' : 'bg-black/10'" />

          <!-- Scrollable Navigation Area -->
          <nav class="flex-1 overflow-y-auto px-4">
            <slot name="navigation-expanded" />
          </nav>

          <!-- Footer -->
          <div class="mt-auto px-4 pb-4">
            <slot name="footer" />
          </div>
        </div>
      </template>
    </div>
  </Drawer>

  <!-- Desktop: Fixed Sidebar (always visible, ignores visible prop) -->
  <div
    v-if="!isSmallerThanLg"
    :class="[
      'fixed top-0 bottom-0 transition-all duration-300 z-40 rounded-r-[24px] overflow-hidden',
      position === 'left' ? 'left-0' : 'right-0',
      isDarkMode ? 'ring-1 ring-white/5' : 'ring-1 ring-black/10',
    ]"
    :style="{
      width: sidebarWidth,
      background: sidebarBackground,
    }"
  >
    <!-- Sidebar Content -->
    <div class="relative z-10 flex h-full flex-col">
      <!-- Icon-Only Variant (looks like collapsed but uses expanded navigation) -->
      <template v-if="isIconOnlyVariant">
        <div class="flex h-full flex-col items-center py-4">
          <!-- Logo Icon -->
          <div class="mb-6 flex items-center justify-center">
            <slot name="logo-collapsed">
              <img v-if="logoCollapsed" :src="logoCollapsed" :alt="logoAlt" class="size-auto" />
            </slot>
          </div>

          <div class="h-px w-12 mb-4" :class="isDarkMode ? 'bg-white/10' : 'bg-black/10'" />

          <!-- Icon-Only Navigation (all items from expanded navigation) -->
          <slot name="navigation-expanded" />

          <!-- Footer -->
          <div class="mt-auto pb-4">
            <slot name="footer" />
          </div>
        </div>
      </template>

      <!-- Full Width Variants (Grouped, Simple, Static) -->
      <template v-else>
        <div class="flex h-full flex-col">
          <!-- Header Slot -->
          <slot name="header" />

          <div class="h-px mx-6 mb-4" :class="isDarkMode ? 'bg-white/10' : 'bg-black/10'" />

          <!-- Scrollable Navigation Area -->
          <nav class="flex-1 overflow-y-auto px-4">
            <slot name="navigation-expanded" />
          </nav>

          <!-- Footer -->
          <div class="mt-auto px-4 pb-4">
            <slot name="footer" />
          </div>
        </div>
      </template>
    </div>
  </div>
</template>
