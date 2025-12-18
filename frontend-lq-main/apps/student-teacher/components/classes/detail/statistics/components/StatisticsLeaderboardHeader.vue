<template>
  <div class="flex items-center gap-2 mb-6">
    <Icon name="solar:cup-star-line-duotone" class="text-warning-500 dark:text-warning-400 text-2xl" />
    <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-50">
      {{ $t("classes.statistics.leaderboard") }}
    </h3>
    <span class="text-sm text-surface-600 dark:text-surface-400 ml-auto">
      {{ $t("classes.statistics.justNow") }}
    </span>
    <button
      type="button"
      class="text-surface-600 dark:text-surface-400 hover:text-surface-900 dark:hover:text-surface-100"
    >
      <Icon name="solar:refresh-circle-line-duotone" class="text-lg" />
    </button>
  </div>
</template>
