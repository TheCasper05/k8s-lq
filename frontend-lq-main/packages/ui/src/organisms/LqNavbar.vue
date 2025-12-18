<script setup lang="ts">
  import { useBreakpoints, breakpointsTailwind } from "@vueuse/core";
  import Button from "primevue/button";

  interface Props {
    contentMargin?: string;
    showMenuButton?: boolean;
  }

  const props = withDefaults(defineProps<Props>(), {
    contentMargin: "0px",
    showMenuButton: true,
  });

  defineEmits<{
    "toggle-sidebar": [];
  }>();

  const breakpoints = useBreakpoints(breakpointsTailwind);
  const isSmallerThanLg = breakpoints.smaller("lg"); // < 1024px

  defineOptions({
    name: "LqNavbar",
  });
</script>

<template>
  <div
    class="fixed top-0 left-0 right-0 bg-transparent backdrop-blur-md transition-all duration-300 h-16 z-50 shadow-none"
    :style="{ marginLeft: props.contentMargin }"
  >
    <div class="flex h-full items-center justify-between gap-2 sm:gap-3 md:gap-4 px-3 sm:px-4 md:px-6">
      <!-- Left Section: Menu Button (Mobile/Tablet) + Organization Name / Breadcrumbs -->
      <div class="flex min-w-12 flex-1 items-center gap-3">
        <!-- Hamburger Menu Button (Mobile/Tablet only) -->
        <Button
          v-if="isSmallerThanLg && showMenuButton"
          icon="pi pi-bars"
          text
          rounded
          severity="secondary"
          class="!w-10 !h-10"
          @click="$emit('toggle-sidebar')"
        />

        <slot name="start" />
      </div>

      <!-- Right Section: Actions -->
      <div class="flex items-center gap-2 sm:gap-3">
        <!-- Custom Actions Slot -->
        <slot name="actions" />

        <!-- Notifications Button -->
        <slot name="notifications" />

        <!-- Settings Button -->
        <slot name="settings" />

        <!-- User Avatar -->
        <slot name="user" />
      </div>
    </div>
  </div>
</template>
