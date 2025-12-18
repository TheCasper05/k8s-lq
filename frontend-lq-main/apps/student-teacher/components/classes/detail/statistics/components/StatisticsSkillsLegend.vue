<template>
  <div class="mt-4 grid grid-cols-2 gap-4">
    <div class="flex items-center gap-2">
      <div class="w-3 h-3 rounded-full bg-info-500 dark:bg-info-400" />
      <span class="text-sm text-surface-700 dark:text-surface-300">
        {{ $t("classes.statistics.skillsLegend.pronunciation") }} 75%
      </span>
    </div>
    <div class="flex items-center gap-2">
      <div class="w-3 h-3 rounded-full bg-success-500 dark:bg-success-400" />
      <span class="text-sm text-surface-700 dark:text-surface-300">
        {{ $t("classes.statistics.skillsLegend.vocabulary") }} 89%
      </span>
    </div>
    <div class="flex items-center gap-2">
      <div class="w-3 h-3 rounded-full bg-warning-500 dark:bg-warning-400" />
      <span class="text-sm text-surface-700 dark:text-surface-300">
        {{ $t("classes.statistics.skillsLegend.grammar") }} 75%
      </span>
    </div>
    <div class="flex items-center gap-2">
      <div class="w-3 h-3 rounded-full bg-danger-500 dark:bg-danger-400" />
      <span class="text-sm text-surface-700 dark:text-surface-300">
        {{ $t("classes.statistics.skillsLegend.fluency") }} 67%
      </span>
    </div>
  </div>
</template>
