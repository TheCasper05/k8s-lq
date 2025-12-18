<script setup lang="ts">
  import { LqCard } from "@lq/ui";
  import type { AnalyticsInsight } from "~/types/activities";

  interface Props {
    insights: AnalyticsInsight[];
  }

  defineProps<Props>();

  const { t } = useI18n();

  const getColorClasses = (index: number): string => {
    const colors = [
      "bg-indigo-100 text-indigo-600 dark:bg-indigo-500/20 dark:text-indigo-400",
      "bg-amber-100 text-amber-600 dark:bg-amber-500/20 dark:text-amber-400",
      "bg-emerald-100 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-400",
      "bg-blue-100 text-blue-600 dark:bg-blue-500/20 dark:text-blue-400",
      "bg-violet-100 text-violet-600 dark:bg-violet-500/20 dark:text-violet-400",
    ];
    return colors[index % colors.length];
  };
</script>

<template>
  <LqCard variant="default" padding="p-6" class="flex flex-col gap-6">
    <h3 class="text-base font-bold text-surface-900 dark:text-surface-0">
      {{ t("teacher.scenarios.detail.analytics.additionalInsights.title") }}
    </h3>
    <div class="space-y-4">
      <div
        v-for="(insight, index) in insights"
        :key="insight.id"
        class="flex items-center gap-4 px-4 py-4 rounded-xl border border-surface-100 dark:border-surface-800 bg-surface-50/50 dark:bg-surface-800/20"
      >
        <div
          class="w-12 h-12 rounded-xl flex items-center justify-center text-xl shrink-0"
          :class="getColorClasses(index)"
        >
          <Icon :name="insight.icon" />
        </div>
        <div>
          <div class="text-xs text-surface-500 dark:text-surface-400 mb-0.5">
            {{ insight.label }}
          </div>
          <div class="text-lg font-bold text-surface-900 dark:text-surface-0">
            {{ insight.value }}
          </div>
        </div>
      </div>
    </div>
  </LqCard>
</template>
