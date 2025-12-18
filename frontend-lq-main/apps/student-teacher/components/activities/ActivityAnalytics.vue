<script setup lang="ts">
  import ActivityMetricCard from "~/components/activities/cards/ActivityMetricCard.vue";
  import WeeklyProgressChart from "~/components/activities/analytics/WeeklyProgressChart.vue";
  import TopPerformersCard from "~/components/activities/analytics/TopPerformersCard.vue";
  import ScoreDistributionChart from "~/components/activities/analytics/ScoreDistributionChart.vue";
  import AdditionalInsightsCard from "~/components/activities/analytics/AdditionalInsightsCard.vue";
  import type { ActivityMetric, ChartConfig, TopPerformer, AnalyticsInsight } from "~/types/activities";

  interface Props {
    metrics: ActivityMetric[];
    weeklyProgress: ChartConfig;
    scoreDistribution: ChartConfig;
    topPerformers: TopPerformer[];
    insights: AnalyticsInsight[];
  }

  const { metrics, weeklyProgress, scoreDistribution, topPerformers, insights } = defineProps<Props>();
</script>

<template>
  <div class="space-y-6">
    <!-- Top Metrics Row -->
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
      <ActivityMetricCard v-for="metric in metrics" :key="metric.id" :metric="metric" variant="boxed" />
    </div>

    <!-- Middle Row: Weekly Progress & Top Performers -->
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
      <WeeklyProgressChart :chart-data="weeklyProgress" improvement-percentage="+ 35% improvement" />
      <TopPerformersCard :performers="topPerformers" />
    </div>

    <!-- Bottom Row: Score Distribution & Additional Insights -->
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
      <ScoreDistributionChart :chart-data="scoreDistribution" />
      <AdditionalInsightsCard :insights="insights" />
    </div>
  </div>
</template>
