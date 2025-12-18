<script setup lang="ts">
  import { LqCard } from "@lq/ui";
  import type { TopPerformer } from "~/types/activities";

  interface Props {
    performers: TopPerformer[];
    showProgressAlert?: boolean;
  }

  withDefaults(defineProps<Props>(), {
    showProgressAlert: true,
  });

  const { t } = useI18n();
</script>

<template>
  <LqCard variant="default" padding="p-6" class="flex flex-col gap-4">
    <div>
      <h3 class="text-base font-bold text-surface-900 dark:text-surface-0 flex items-center gap-2">
        <Icon name="lucide:trophy" class="text-xl text-amber-500" />
        <span>{{ t("teacher.scenarios.detail.analytics.topPerformers.title") }}</span>
      </h3>
      <p class="text-xs text-surface-500 dark:text-surface-400 mt-1">
        {{ t("teacher.scenarios.detail.analytics.topPerformers.description") }}
      </p>
    </div>

    <div class="space-y-4">
      <div v-for="student in performers" :key="student.id" class="relative">
        <!-- Medal Icon -->
        <div class="absolute -left-3 -top-3 z-10">
          <div
            class="w-8 h-8 rounded-full flex items-center justify-center text-lg shadow-sm border-4 border-white dark:border-surface-900"
            :class="[
              student.rank === 1 ? 'bg-amber-400 text-amber-900' : '',
              student.rank === 2 ? 'bg-slate-300 text-slate-700' : '',
              student.rank === 3 ? 'bg-orange-300 text-orange-800' : '',
            ]"
          >
            <span v-if="student.rank === 1" class="text-base">🥇</span>
            <span v-else-if="student.rank === 2" class="text-base">🥈</span>
            <span v-else class="text-base">🥉</span>
          </div>
        </div>

        <!-- Performer card -->
        <div
          class="flex items-center justify-between gap-4 px-5 py-4 rounded-xl border transition-all"
          :class="[
            student.rank === 1
              ? 'bg-amber-50 border-amber-200 dark:bg-amber-500/10 dark:border-amber-500/20'
              : 'bg-surface-0 border-surface-200 dark:bg-surface-800/50 dark:border-surface-700 shadow-sm',
          ]"
        >
          <div class="flex items-center gap-3 pl-2">
            <div
              class="w-10 h-10 rounded-full flex items-center justify-center text-xl shrink-0"
              :class="[student.rank === 1 ? 'bg-amber-200/50' : 'bg-emerald-100/50 dark:bg-emerald-500/10']"
            >
              {{ student.emoji }}
            </div>
            <div>
              <div class="text-sm font-bold text-surface-900 dark:text-surface-0">
                {{ student.name }}
              </div>
              <div class="text-xs text-surface-500 dark:text-surface-400">
                {{ student.className }}
              </div>
            </div>
          </div>

          <div
            class="px-3 py-1.5 rounded-lg text-sm font-bold text-white min-w-[60px] text-center"
            :class="[student.rank === 1 ? 'bg-amber-400 shadow-amber-200/50' : 'bg-blue-500 shadow-blue-200/50']"
          >
            {{ student.score }}%
          </div>
        </div>
      </div>
    </div>

    <div
      v-if="showProgressAlert"
      class="mt-auto px-4 py-4 rounded-xl border border-blue-100 dark:border-blue-900/30 bg-blue-50 dark:bg-blue-500/5 flex items-start gap-4"
    >
      <div class="w-10 h-10 rounded-full bg-blue-500 text-white flex items-center justify-center shrink-0 shadow-sm">
        <Icon name="lucide:target" class="text-xl" />
      </div>
      <div>
        <p class="text-sm font-bold text-blue-900 dark:text-blue-100 mb-1">
          {{ t("teacher.scenarios.detail.analytics.topPerformers.greatProgress") }}
        </p>
        <p class="text-xs text-blue-600 dark:text-blue-300 leading-relaxed">
          {{ t("teacher.scenarios.detail.analytics.topPerformers.greatProgressMessage") }}
        </p>
      </div>
    </div>
  </LqCard>
</template>
