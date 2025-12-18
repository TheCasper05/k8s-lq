<script setup lang="ts">
  import { computed } from "vue";
  import Button from "primevue/button";
  import { useI18n } from "vue-i18n";

  interface Props {
    title?: string;
    description?: string;
    actionLabel?: string;
    showAction?: boolean;
  }

  interface Emits {
    action: [];
  }

  const props = withDefaults(defineProps<Props>(), {
    title: "",
    description: "",
    actionLabel: "",
    showAction: true,
  });

  defineEmits<Emits>();

  const { t } = useI18n();

  const displayTitle = computed(() => props.title || t("teacher.scenarios.emptyState.title"));
  const displayDescription = computed(() => props.description || t("teacher.scenarios.emptyState.description"));
  const displayActionLabel = computed(() => props.actionLabel || t("teacher.scenarios.emptyState.action"));
</script>

<template>
  <div class="flex flex-col items-center justify-center py-16 px-4">
    <div class="w-24 h-24 rounded-full bg-surface-100 dark:bg-surface-800 flex items-center justify-center mb-6">
      <Icon name="solar:inbox-linear" class="text-5xl text-surface-400 dark:text-surface-600" />
    </div>
    <h3 class="text-2xl font-semibold text-surface-900 dark:text-surface-0 mb-2">
      {{ displayTitle }}
    </h3>
    <p class="text-surface-600 dark:text-surface-400 text-center max-w-md mb-6">
      {{ displayDescription }}
    </p>
    <Button v-if="showAction" :label="displayActionLabel" @click="$emit('action')">
      <template #icon>
        <Icon name="solar:add-circle-linear" />
      </template>
    </Button>
  </div>
</template>
