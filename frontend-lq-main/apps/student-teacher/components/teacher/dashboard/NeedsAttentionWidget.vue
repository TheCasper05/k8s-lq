<script setup lang="ts">
  import { useRoleLayout } from "~/composables/useRoleLayout";
  import type { AttentionItem } from "~/composables/teacher/types";
  import { LqCard } from "@lq/ui";

  interface Props {
    items: AttentionItem[];
  }

  defineProps<Props>();
  const { withRolePrefix } = useRoleLayout();
  const router = useRouter();

  const handleAction = (item: AttentionItem) => {
    const route = withRolePrefix(item.actionRoute);
    router.push(route);
  };

  const handleViewAll = () => {
    const route = withRolePrefix("/attention");
    router.push(route);
  };

  const getSeverityClasses = (severity: "success" | "warning" | "danger") => {
    const classes = {
      success:
        "bg-success-100 dark:bg-success-900/30 text-success-700 dark:text-success-400 border-success-200 dark:border-success-800",
      warning:
        "bg-warning-100 dark:bg-warning-900/30 text-warning-700 dark:text-warning-400 border-warning-200 dark:border-warning-800",
      danger:
        "bg-danger-100 dark:bg-danger-900/30 text-danger-700 dark:text-danger-400 border-danger-200 dark:border-danger-800",
    };
    return classes[severity];
  };

  const getSeverityIcon = (severity: "success" | "warning" | "danger") => {
    const icons = {
      success: "solar:chart-2-line-duotone",
      warning: "solar:clock-circle-line-duotone",
      danger: "solar:danger-triangle-line-duotone",
    };
    return icons[severity];
  };
</script>

<template>
  <LqCard data-testid="needs-attention-widget">
    <template #header>
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Icon name="solar:bell-bing-line-duotone" class="text-xl text-warning-600 dark:text-warning-400" />
          <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-50">
            {{ $t("teacher.dashboard.needsAttention.title") }}
          </h3>
        </div>
        <Button
          :label="$t('teacher.dashboard.needsAttention.viewAll')"
          text
          size="small"
          icon-pos="right"
          data-testid="view-all-attention-button"
          @click="handleViewAll"
        >
          <template #icon>
            <Icon name="solar:arrow-right-line-duotone" />
          </template>
        </Button>
      </div>
    </template>

    <div v-if="items.length === 0" class="text-center py-8 text-surface-500 dark:text-surface-400">
      {{ $t("teacher.dashboard.needsAttention.empty") }}
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="item in items"
        :key="item.id"
        :class="['p-4 rounded-lg border', getSeverityClasses(item.severity)]"
        data-testid="attention-item"
      >
        <div class="flex items-start gap-4">
          <!-- Icon -->
          <div class="shrink-0">
            <Icon
              :name="getSeverityIcon(item.severity)"
              class="text-xl"
              :class="{
                'text-warning-600 dark:text-warning-400': item.severity === 'warning',
                'text-danger-600 dark:text-danger-400': item.severity === 'danger',
                'text-success-600 dark:text-success-400': item.severity === 'success',
              }"
            />
          </div>

          <!-- Title and Description -->
          <div class="flex-1 min-w-0">
            <h4 class="font-semibold text-sm mb-1">{{ item.title }}</h4>
            <p class="text-sm opacity-90">{{ item.description }}</p>
          </div>

          <!-- Action Button -->
          <div class="shrink-0">
            <Button
              :label="item.actionLabel"
              size="small"
              :severity="item.severity === 'warning' ? 'warn' : item.severity"
              data-testid="attention-action-button"
              @click="handleAction(item)"
            />
          </div>
        </div>
      </div>
    </div>
  </LqCard>
</template>
