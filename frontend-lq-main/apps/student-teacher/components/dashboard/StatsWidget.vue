<script setup lang="ts">
  const stats = [
    {
      titleKey: "dashboard.stats.totalOrders",
      icon: "pi-shopping-cart",
      value: "1,234",
      subtitleKey: "dashboard.stats.last7Days",
    },
    {
      titleKey: "dashboard.stats.activeUsers",
      icon: "pi-users",
      value: "2,573",
      subtitleKey: "dashboard.stats.last7Days",
    },
    {
      titleKey: "dashboard.stats.revenue",
      icon: "pi-dollar",
      value: "$45,200",
      subtitleKey: "dashboard.stats.last7Days",
    },
    {
      titleKey: "dashboard.stats.successRate",
      icon: "pi-chart-line",
      value: "95%",
      subtitleKey: "dashboard.stats.last7Days",
    },
  ];
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
    <div
      v-for="(stat, index) in stats"
      :key="index"
      class="bg-surface-0 dark:bg-surface-900 p-6 rounded-xl border border-surface-200 dark:border-surface-700 flex flex-col gap-2"
    >
      <div class="flex items-start gap-2 justify-between">
        <span class="text-xl font-light leading-tight">{{ $t(stat.titleKey) }}</span>
        <span
          class="shrink-0 bg-primary-100 dark:bg-primary-400/20 text-primary rounded-lg w-8 h-8 flex items-center justify-center border border-primary-200 dark:border-primary-400/40"
        >
          <i :class="['pi', stat.icon, 'text-xl!', 'leading-none!']" />
        </span>
      </div>
      <div class="flex flex-col gap-1 w-full">
        <div class="text-3xl font-medium leading-tight">
          {{ stat.value }}
        </div>
        <div class="text-surface-600 dark:text-surface-400 text-sm leading-tight">
          {{ $t(stat.subtitleKey) }}
        </div>
      </div>
    </div>
  </div>
</template>
