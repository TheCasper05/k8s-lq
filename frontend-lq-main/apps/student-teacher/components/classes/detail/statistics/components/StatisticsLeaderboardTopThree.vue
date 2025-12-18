<script setup lang="ts">
  import type { LeaderboardEntry } from "~/composables/classes/types";

  interface Props {
    topThree: LeaderboardEntry[];
    getBadgeClass: (level: string) => string;
  }

  defineProps<Props>();
</script>

<template>
  <div v-if="topThree.length > 0" class="flex items-end justify-center gap-8 mb-8">
    <div v-if="topThree[1]" class="flex flex-col items-center">
      <div class="relative mb-2">
        <img
          :src="topThree[1].studentPhoto || 'https://i.pravatar.cc/150?img=2'"
          :alt="topThree[1].studentName"
          class="w-16 h-16 rounded-full border-2 border-surface-300"
        />
        <div
          class="absolute -bottom-1 -right-1 w-6 h-6 bg-surface-300 text-surface-700 rounded-full flex items-center justify-center text-xs font-bold"
        >
          2
        </div>
      </div>
      <div class="text-sm font-medium text-surface-900 dark:text-surface-50 text-center">
        {{ topThree[1].studentName.split(" ")[0] }}
      </div>
      <div class="text-xs text-surface-600 dark:text-surface-400">{{ topThree[1].practiceTime }}</div>
      <div class="mt-2 bg-surface-200 dark:bg-surface-700 rounded w-20 h-24 flex items-center justify-center">
        <span :class="getBadgeClass('B2')">B2</span>
      </div>
    </div>

    <div v-if="topThree[0]" class="flex flex-col items-center">
      <div class="relative mb-2">
        <Icon name="solar:crown-bold" class="absolute -top-6 left-1/2 -translate-x-1/2 text-yellow-400 text-2xl" />
        <img
          :src="topThree[0].studentPhoto || 'https://i.pravatar.cc/150?img=1'"
          :alt="topThree[0].studentName"
          class="w-20 h-20 rounded-full border-4 border-purple-500"
        />
        <div
          class="absolute -bottom-1 -right-1 w-8 h-8 bg-yellow-400 text-yellow-900 rounded-full flex items-center justify-center text-sm font-bold"
        >
          1
        </div>
      </div>
      <div class="text-base font-semibold text-surface-900 dark:text-surface-50 text-center">
        {{ topThree[0].studentName.split(" ")[0] }}
      </div>
      <div class="text-sm text-surface-600 dark:text-surface-400">{{ topThree[0].practiceTime }}</div>
      <div class="mt-2 bg-purple-600 rounded w-24 h-32 flex items-center justify-center">
        <span :class="getBadgeClass('B2')" class="!bg-white !text-purple-600">B2</span>
      </div>
    </div>

    <div v-if="topThree[2]" class="flex flex-col items-center">
      <div class="relative mb-2">
        <img
          :src="topThree[2].studentPhoto || 'https://i.pravatar.cc/150?img=3'"
          :alt="topThree[2].studentName"
          class="w-16 h-16 rounded-full border-2 border-orange-400"
        />
        <div
          class="absolute -bottom-1 -right-1 w-6 h-6 bg-orange-400 text-orange-900 rounded-full flex items-center justify-center text-xs font-bold"
        >
          3
        </div>
      </div>
      <div class="text-sm font-medium text-surface-900 dark:text-surface-50 text-center">
        {{ topThree[2].studentName.split(" ")[0] }}
      </div>
      <div class="text-xs text-surface-600 dark:text-surface-400">{{ topThree[2].practiceTime }}</div>
      <div class="mt-2 bg-surface-200 dark:bg-surface-700 rounded w-20 h-24 flex items-center justify-center">
        <span :class="getBadgeClass('B2')">B2</span>
      </div>
    </div>
  </div>
</template>
