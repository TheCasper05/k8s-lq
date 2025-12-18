<script setup lang="ts">
  import { useLayout } from "@lq/composables";
  import Ripple from "primevue/ripple";
  import StyleClass from "primevue/styleclass";

  const vRipple = Ripple;
  const vStyleclass = StyleClass;

  interface Props {
    label?: string;
    icon?: string;
    iconOnly?: boolean;
    collapsible?: boolean;
  }

  withDefaults(defineProps<Props>(), {
    label: undefined,
    icon: undefined,
    iconOnly: false,
    collapsible: false,
  });

  const { isDarkMode } = useLayout();
</script>

<template>
  <div class="flex flex-col gap-2">
    <!-- Group Header (for grouped/static variants with collapsible) -->
    <div
      v-if="label && !iconOnly && collapsible"
      v-ripple
      v-styleclass="{
        selector: '@next',
        enterFromClass: 'hidden',
        enterActiveClass: 'animate-slidedown',
        leaveToClass: 'hidden',
        leaveActiveClass: 'animate-slideup',
      }"
      class="flex cursor-pointer items-center rounded-lg px-4 py-2.5 mb-1 p-ripple transition-all duration-200 text-surface-700 dark:text-surface-300 hover:bg-surface-200 dark:hover:bg-surface-700 has-[+ul:not(.hidden)]:bg-surface-200 dark:has-[+ul:not(.hidden)]:bg-surface-800"
    >
      <Icon v-if="icon" :name="icon" class="mr-3 size-5" />
      <span class="font-medium text-sm">{{ label }}</span>
      <Icon name="solar:alt-arrow-down-linear" class="ml-auto h-4 w-4" />
    </div>

    <!-- Group Label (for non-collapsible) -->
    <span
      v-else-if="label && !iconOnly"
      class="px-4 py-2 text-xs font-semibold uppercase tracking-wider"
      :class="isDarkMode ? 'text-surface-400' : 'text-surface-500'"
    >
      {{ label }}
    </span>

    <!-- Navigation Items -->
    <ul
      v-if="collapsible"
      class="m-0 list-none space-y-1 overflow-hidden px-1"
      :class="iconOnly ? 'flex flex-col gap-2 w-full px-3' : ''"
    >
      <slot />
    </ul>
    <div v-else :class="iconOnly ? 'flex flex-col gap-2 w-full px-3' : 'space-y-1'">
      <slot />
    </div>
  </div>
</template>
