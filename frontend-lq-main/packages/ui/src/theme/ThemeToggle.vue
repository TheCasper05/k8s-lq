<script setup lang="ts">
  import { useLayout } from "@lq/composables";
  import { computed } from "vue";

  interface Props {
    /**
     * Icon to show when in light mode (for dark mode button)
     * @default 'solar:sun-line-duotone'
     */
    lightIcon?: string;
    /**
     * Icon to show when in dark mode (for light mode button)
     * @default 'solar:moon-line-duotone'
     */
    darkIcon?: string;
    /**
     * Button size
     * @default 'medium'
     */
    size?: "small" | "medium" | "large";
    /**
     * Additional CSS classes
     */
    class?: string;
    /**
     * Button variant style
     * @default 'default'
     */
    variant?: "default" | "auth";
  }

  const props = withDefaults(defineProps<Props>(), {
    lightIcon: "solar:sun-line-duotone",
    darkIcon: "solar:moon-line-duotone",
    size: "medium",
    class: "",
    variant: "default",
  });

  const { isDarkMode, toggleDarkMode } = useLayout();

  const sizeClasses = {
    small: "size-8",
    medium: "size-10",
    large: "size-12",
  };

  const variantClasses = computed(() => {
    if (props.variant === "auth") {
      return "bg-white/80 hover:bg-white text-secondary-600 dark:bg-surface-800/80 dark:hover:bg-surface-700 dark:text-surface-400 rounded-full items-center justify-center duration-200 transition-all shadow-md border border-surface-300 dark:border-surface-600 hover:border-surface-500/80 dark:hover:border-surface-700 hover:shadow-lg";
    }
    return "bg-surface-100 hover:bg-surface-200 text-surface-600 dark:bg-surface-800 dark:hover:bg-surface-700 dark:text-surface-400 rounded-lg";
  });
</script>

<template>
  <div class="relative">
    <button
      v-ripple
      type="button"
      :class="[sizeClasses[size], variantClasses, props.class]"
      :aria-label="isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'"
      @click="toggleDarkMode"
    >
      <slot name="icon">
        <div class="flex justify-center items-center">
          <Icon :name="isDarkMode ? lightIcon : darkIcon" class="text-xl" />
        </div>
      </slot>
    </button>
  </div>
</template>
