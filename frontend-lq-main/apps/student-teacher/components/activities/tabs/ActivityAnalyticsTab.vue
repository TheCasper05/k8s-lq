<script setup lang="ts">
  import ActivityAnalytics from "~/components/activities/ActivityAnalytics.vue";
  import type { ActivityMetric, ChartConfig, TopPerformer, AnalyticsInsight } from "~/types/activities";

  interface Props {
    metrics: ActivityMetric[];
    weeklyProgress: ChartConfig;
    scoreDistribution: ChartConfig;
    topPerformers: TopPerformer[];
    insights: AnalyticsInsight[];
  }

  defineProps<Props>();
</script>

<template>
  <div class="animate-fade-in">
    <ActivityAnalytics
      :metrics="metrics"
      :weekly-progress="weeklyProgress"
      :score-distribution="scoreDistribution"
      :top-performers="topPerformers"
      :insights="insights"
    />
  </div>
</template>
