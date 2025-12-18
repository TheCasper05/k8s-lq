<script setup lang="ts">
  import { computed } from "vue";
  import type { StudentStats } from "~/composables/students/types";
  import { LqMetricCard, type LqMetric } from "@lq/ui";
  import { useI18n } from "#imports";

  const { t } = useI18n();

  const props = defineProps<{
    stats: StudentStats;
  }>();

  const kpiMetrics = computed((): LqMetric[] => [
    {
      icon: "solar:users-group-rounded-line-duotone",
      label: t("students.totalStudents"),
      value: props.stats.totalStudents,
      color: "info",
      trend: `+${props.stats.monthlyChangePercent}%`,
    },
    {
      icon: "solar:clock-circle-line-duotone",
      label: t("students.studyHours"),
      value: `${props.stats.totalStudyHours}h`,
      color: "success",
      trend: `+${props.stats.monthlyHoursChangePercent}%`,
    },
    {
      icon: "solar:chart-2-line-duotone",
      label: t("students.averageProgress"),
      value: `${props.stats.averageProgress}%`,
      color: "primary",
    },
  ]);
</script>

<template>
  <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6">
    <LqMetricCard v-for="(metric, index) in kpiMetrics" :key="index" :metric="metric" variant="boxed" />
  </div>
</template>
