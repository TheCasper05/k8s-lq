<script setup lang="ts">
  import { useRoleLayout } from "~/composables/useRoleLayout";
  import type { QuickAction } from "~/composables/teacher/types";

  interface Props {
    actions: QuickAction[];
  }

  defineProps<Props>();
  const { withRolePrefix } = useRoleLayout();
  const router = useRouter();

  const handleActionClick = (action: QuickAction) => {
    const route = withRolePrefix(action.route);
    router.push(route);
  };

  const handleKeyDown = (event: KeyboardEvent, action: QuickAction) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      handleActionClick(action);
    }
  };

  const getActionClasses = (variant: "primary" | "default") => {
    if (variant === "primary") {
      return "bg-primary-600 dark:bg-primary-600 text-white hover:bg-primary-700 dark:hover:bg-primary-700";
    }
    return "bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 text-surface-900 dark:text-surface-50 hover:bg-surface-50 dark:hover:bg-surface-800";
  };

  const getIconClasses = (action: QuickAction) => {
    if (action.variant === "primary") {
      return "text-white";
    }
    // Map icon to color based on action type
    if (action.id === "browse-scenarios") {
      return "text-success-600 dark:text-success-400";
    }
    if (action.id === "view-classes") {
      return "text-teal-600 dark:text-teal-400";
    }
    return "text-primary-600 dark:text-primary-400";
  };
</script>

<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6" data-testid="quick-action-cards">
    <div
      v-for="action in actions"
      :key="action.id"
      :class="[
        'relative rounded-xl p-4 sm:p-6 cursor-pointer transition-all duration-200 shadow-sm hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
        getActionClasses(action.variant),
      ]"
      role="button"
      :tabindex="0"
      :aria-label="`${action.title}: ${action.description}`"
      data-testid="quick-action-card"
      @click="handleActionClick(action)"
      @keydown="handleKeyDown($event, action)"
    >
      <div class="flex items-center justify-between mb-1">
        <Icon
          :name="action.icon"
          class="text-3xl sm:text-4xl"
          :class="getIconClasses(action)"
          aria-hidden="true"
          data-testid="quick-action-icon"
        />
        <div
          v-if="action.badge"
          :class="[
            'text-xs font-medium px-2 py-1 rounded-lg',
            action.variant === 'primary'
              ? 'bg-success-600 dark:bg-success-700 text-white'
              : 'bg-surface-100 dark:bg-surface-800 text-surface-700 dark:text-surface-300',
          ]"
          data-testid="quick-action-badge"
        >
          {{ action.badge }}
        </div>
      </div>

      <div>
        <h3
          :class="[
            'text-lg sm:text-xl font-bold mb-1',
            action.variant === 'primary' ? 'text-white' : 'text-surface-900 dark:text-surface-50',
          ]"
          data-testid="quick-action-title"
        >
          {{ action.title }}
        </h3>
        <p
          :class="[
            'text-xs sm:text-sm',
            action.variant === 'primary' ? 'text-white/90' : 'text-surface-600 dark:text-surface-400',
          ]"
          data-testid="quick-action-description"
        >
          {{ action.description }}
        </p>
      </div>
    </div>
  </div>
</template>
