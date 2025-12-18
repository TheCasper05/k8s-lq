<script setup lang="ts">
  import type { Student } from "~/composables/students/types";
  import type { Assignment, AssignmentGrade } from "~/composables/classes/types";
  import { useClassStatisticsProvider } from "~/composables/classes/useClassStatisticsProvider";
  import StatisticsMetricsCards from "./components/StatisticsMetricsCards.vue";
  import StatisticsLeaderboardCard from "./components/StatisticsLeaderboardCard.vue";
  import StatisticsAssignmentsChartCard from "./components/StatisticsAssignmentsChartCard.vue";
  import StatisticsSkillsChartCard from "./components/StatisticsSkillsChartCard.vue";
  import StatisticsStudyTimeChartCard from "./components/StatisticsStudyTimeChartCard.vue";

  interface Props {
    students: Student[];
    assignments: Assignment[];
    grades: AssignmentGrade[];
  }

  const props = defineProps<Props>();

  const {
    leaderboard,
    assignmentsChartData,
    skillsChartData,
    studyTimeChartData,
    metricsCards,
    topThree,
    getBadgeClass,
    getRankBadgeClass,
    barChartOptions,
    doughnutChartOptions,
    lineChartOptions,
  } = useClassStatisticsProvider(props.students, props.assignments, props.grades);
</script>

<template>
  <div class="space-y-4 md:space-y-6">
    <!-- Top Metrics Cards -->
    <StatisticsMetricsCards :metrics="metricsCards" />

    <!-- Leaderboard Section -->
    <StatisticsLeaderboardCard
      :top-three="topThree"
      :leaderboard="leaderboard"
      :get-badge-class="getBadgeClass"
      :get-rank-badge-class="getRankBadgeClass"
    />

    <!-- Charts Section -->
    <div class="space-y-4 md:space-y-6">
      <!-- First Row: Assignments + Skills -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
        <!-- Assignments Chart -->
        <StatisticsAssignmentsChartCard :data="assignmentsChartData" :options="barChartOptions" />

        <!-- Skills Chart -->
        <StatisticsSkillsChartCard :data="skillsChartData" :options="doughnutChartOptions" />
      </div>

      <!-- Second Row: Study Time (full width) -->
      <StatisticsStudyTimeChartCard :data="studyTimeChartData" :options="lineChartOptions" />
    </div>
  </div>
</template>
