<script setup lang="ts">
  import { computed } from "vue";
  import LqCard from "../molecules/LqCard.vue";

  export interface LqMetric {
    icon: string;
    label: string;
    value: string | number;
    description?: string;
    badge?: string;
    color?: "primary" | "info" | "success" | "warning" | "danger";
    trend?: string;
  }

  interface Props {
    metric: LqMetric;
    /**
     * Variant of the metric card
     * - default: Vertical layout with large value
     * - horizontal: Horizontal layout with icon on left
     * - boxed: Compact layout with icon and optional trend badge
     */
    variant?: "default" | "horizontal" | "boxed";
    /**
     * Position of the label in boxed variant
     * - top: Label above value (default)
     * - bottom: Label below value
     */
    labelPosition?: "top" | "bottom";
  }

  const props = withDefaults(defineProps<Props>(), {
    variant: "default",
    labelPosition: "top",
  });

  const textClass = computed(() => {
    const colorMap: Record<string, string> = {
      primary: "text-primary-600 dark:text-primary-400",
      info: "text-blue-600 dark:text-blue-400",
      success: "text-emerald-600 dark:text-emerald-400",
      warning: "text-amber-600 dark:text-amber-400",
      danger: "text-rose-600 dark:text-rose-400",
    };

    return colorMap[props.metric.color || "primary"];
  });

  const bgClass = computed(() => {
    const colorMap: Record<string, string> = {
      primary: "bg-primary-100 dark:bg-primary-500/10 text-primary-600 dark:text-primary-400",
      info: "bg-blue-100 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400",
      success: "bg-emerald-100 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400",
      warning: "bg-amber-100 dark:bg-amber-500/10 text-amber-600 dark:text-amber-400",
      danger: "bg-rose-100 dark:bg-rose-500/10 text-rose-600 dark:text-rose-400",
    };

    return colorMap[props.metric.color || "primary"];
  });

  const cardPadding = computed(() => {
    if (props.variant === "horizontal") return "p-4 sm:p-6";
    if (props.variant === "boxed") return "p-3 sm:p-4 md:p-5";
    return "p-3 sm:p-4 md:p-5";
  });

  const descriptionClass = computed(() => {
    const colorMap: Record<string, string> = {
      primary: "text-primary-500 dark:text-primary-400",
      info: "text-blue-500 dark:text-blue-400",
      success: "text-emerald-500 dark:text-emerald-400",
      warning: "text-amber-500 dark:text-amber-400",
      danger: "text-rose-500 dark:text-rose-400",
    };

    return colorMap[props.metric.color || "primary"];
  });
</script>

<template>
  <LqCard :variant="variant" :padding="cardPadding" hoverable class="h-full">
    <!-- Default (Vertical) Variant -->
    <template v-if="variant === 'default'">
      <div class="flex items-start justify-between mb-2">
        <span class="text-base sm:text-lg font-bold text-surface-700 dark:text-surface-200">
          {{ metric.label }}
        </span>
        <Icon :name="metric.icon" :class="textClass" class="text-xl sm:text-2xl" />
      </div>

      <div class="text-3xl sm:text-4xl md:text-5xl font-bold" :class="textClass">
        {{ metric.value }}
      </div>
    </template>

    <!-- Horizontal Variant -->
    <template v-else-if="variant === 'horizontal'">
      <div class="flex items-center gap-3 sm:gap-5">
        <div class="w-12 h-12 sm:w-16 sm:h-16 rounded-2xl flex items-center justify-center shrink-0" :class="bgClass">
          <Icon :name="metric.icon" class="text-2xl sm:text-3xl" />
        </div>
        <div>
          <div class="text-sm sm:text-base text-surface-600 dark:text-surface-400 font-medium mb-1">
            {{ metric.label }}
          </div>
          <div class="text-2xl sm:text-3xl font-bold text-surface-900 dark:text-surface-0">
            {{ metric.value }}
          </div>
        </div>
      </div>
    </template>

    <!-- Boxed Variant (Default for metrics cards) -->
    <template v-else-if="variant === 'boxed'">
      <div class="flex flex-col gap-2 sm:gap-3">
        <!-- Icon with optional trend badge -->
        <div class="flex items-center gap-2">
          <div class="w-9 h-9 sm:w-10 sm:h-10 rounded-lg flex items-center justify-center shrink-0" :class="bgClass">
            <Icon :name="metric.icon" class="text-lg sm:text-xl" />
          </div>
          <span v-if="metric.trend" class="px-2 py-1 rounded text-xs font-semibold" :class="bgClass">
            {{ metric.trend }}
          </span>
        </div>

        <!-- Label Top (default) -->
        <div v-if="labelPosition === 'top'" class="text-xs sm:text-sm text-surface-500 dark:text-surface-400">
          {{ metric.label }}
        </div>

        <!-- Value with optional badge -->
        <div class="flex items-baseline gap-2">
          <div class="text-xl sm:text-2xl font-bold text-surface-900 dark:text-surface-50">
            {{ metric.value }}
          </div>
          <span
            v-if="metric.badge"
            class="px-2 py-0.5 rounded text-xs font-semibold bg-info-100 dark:bg-info-900/30 text-info-700 dark:text-info-400"
          >
            {{ metric.badge }}
          </span>
        </div>

        <!-- Label Bottom -->
        <div v-if="labelPosition === 'bottom'" class="text-xs sm:text-sm text-surface-500 dark:text-surface-400">
          {{ metric.label }}
        </div>

        <!-- Description -->
        <div v-if="metric.description" class="text-xs sm:text-sm font-medium" :class="descriptionClass">
          {{ metric.description }}
        </div>
      </div>
    </template>
  </LqCard>
</template>
