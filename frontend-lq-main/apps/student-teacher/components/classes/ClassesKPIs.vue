<script setup lang="ts">
  import { computed } from "vue";
  import type { ClassStats } from "~/composables/classes/types";
  import { LqMetricCard, type LqMetric } from "@lq/ui";

  const props = defineProps<{
    stats: ClassStats;
  }>();

  const { t } = useI18n();

  const kpiMetrics = computed((): LqMetric[] => [
    {
      icon: "solar:book-line-duotone",
      label: t("classes.totalClasses"),
      value: props.stats.totalClasses,
      color: "primary",
    },
    {
      icon: "solar:clock-circle-line-duotone",
      label: t("classes.activeClasses"),
      value: props.stats.activeClasses,
      color: "warning",
    },
    {
      icon: "solar:users-group-rounded-line-duotone",
      label: t("classes.totalStudents"),
      value: props.stats.totalStudents,
      color: "primary",
    },
    {
      icon: "solar:calendar-line-duotone",
      label: t("classes.avgPerClass"),
      value: props.stats.avgPerClass,
      color: "success",
    },
  ]);
</script>

<template>
  <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
    <LqMetricCard v-for="(metric, index) in kpiMetrics" :key="index" :metric="metric" />
  </div>
</template>
