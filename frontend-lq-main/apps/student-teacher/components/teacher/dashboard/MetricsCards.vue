<script setup lang="ts">
  import { computed } from "vue";
  import type { DashboardMetrics } from "~/composables/teacher/types";
  import { LqMetricCard, type LqMetric } from "@lq/ui";

  interface Props {
    metrics: DashboardMetrics;
  }

  const props = defineProps<Props>();
  const { t } = useI18n();

  const metricCards = computed((): LqMetric[] => [
    {
      icon: props.metrics.totalStudents.icon,
      label: t(`teacher.dashboard.metrics.${props.metrics.totalStudents.i18nKey}`),
      value: props.metrics.totalStudents.value,
      color: props.metrics.totalStudents.color,
      trend: props.metrics.totalStudents.change
        ? `${props.metrics.totalStudents.change > 0 ? "+" : ""}${props.metrics.totalStudents.change}%`
        : undefined,
    },
    {
      icon: props.metrics.activeScenarios.icon,
      label: t(`teacher.dashboard.metrics.${props.metrics.activeScenarios.i18nKey}`),
      value: props.metrics.activeScenarios.value,
      color: props.metrics.activeScenarios.color,
      trend: props.metrics.activeScenarios.change
        ? `${props.metrics.activeScenarios.change > 0 ? "+" : ""}${props.metrics.activeScenarios.change}%`
        : undefined,
    },
    {
      icon: props.metrics.totalPracticeTime.icon,
      label: t(`teacher.dashboard.metrics.${props.metrics.totalPracticeTime.i18nKey}`),
      value: props.metrics.totalPracticeTime.value,
      color: props.metrics.totalPracticeTime.color,
      trend: props.metrics.totalPracticeTime.change
        ? `${props.metrics.totalPracticeTime.change > 0 ? "+" : ""}${props.metrics.totalPracticeTime.change}%`
        : undefined,
    },
    {
      icon: props.metrics.totalTimeSaved.icon,
      label: t(`teacher.dashboard.metrics.${props.metrics.totalTimeSaved.i18nKey}`),
      value: props.metrics.totalTimeSaved.value,
      color: props.metrics.totalTimeSaved.color,
      trend: props.metrics.totalTimeSaved.change
        ? `${props.metrics.totalTimeSaved.change > 0 ? "+" : ""}${props.metrics.totalTimeSaved.change}%`
        : undefined,
    },
  ]);
</script>

<template>
  <div data-testid="metrics-cards">
    <!-- Main Metrics Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <LqMetricCard
        v-for="(metric, index) in metricCards"
        :key="index"
        :metric="metric"
        variant="boxed"
        data-testid="metric-card"
        label-position="bottom"
      />
    </div>
  </div>
</template>
