<script setup lang="ts">
  import { LqCard } from "@lq/ui";
  import type { LeaderboardEntry } from "~/composables/classes/types";
  import StatisticsLeaderboardHeader from "./StatisticsLeaderboardHeader.vue";
  import StatisticsLeaderboardTopThree from "./StatisticsLeaderboardTopThree.vue";
  import StatisticsLeaderboardTable from "./StatisticsLeaderboardTable.vue";

  interface Props {
    topThree: LeaderboardEntry[];
    leaderboard: LeaderboardEntry[];
    getBadgeClass: (level: string) => string;
    getRankBadgeClass: (rank: number) => string;
  }

  defineProps<Props>();
</script>

<template>
  <LqCard variant="default" padding="p-6">
    <StatisticsLeaderboardHeader />
    <StatisticsLeaderboardTopThree :top-three="topThree" :get-badge-class="getBadgeClass" />
    <StatisticsLeaderboardTable
      :leaderboard="leaderboard"
      :get-badge-class="getBadgeClass"
      :get-rank-badge-class="getRankBadgeClass"
    />
  </LqCard>
</template>
