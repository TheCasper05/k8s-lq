<script setup lang="ts">
  import { ref, watch } from "vue";
  import type { ClassFilters } from "~/composables/classes/types";
  import { LqSearchInput, LqSelect } from "@lq/ui";

  const props = defineProps<{
    filters: ClassFilters;
    availableLevels: string[];
  }>();

  const emit = defineEmits<{
    "update:filters": [filters: ClassFilters];
    "export": [];
  }>();

  const localFilters = ref<ClassFilters>({ ...props.filters });

  watch(
    () => props.filters,
    (newFilters) => {
      localFilters.value = { ...newFilters };
    },
    { deep: true },
  );

  const updateFilters = () => {
    emit("update:filters", { ...localFilters.value });
  };

  const { t } = useI18n();
</script>

<template>
  <div class="w-full flex flex-col sm:flex-row gap-3 items-stretch sm:items-center">
    <div class="flex-1 min-w-0 w-full max-w-none">
      <LqSearchInput
        v-model="localFilters.search"
        :placeholder="t('classes.searchPlaceholder')"
        @update:model-value="updateFilters"
      />
    </div>
    <LqSelect
      v-model="localFilters.level"
      :options="availableLevels"
      :placeholder="$t('classes.allLevels')"
      class="w-full sm:w-auto sm:shrink-0 sm:min-w-[150px]"
      @update:model-value="updateFilters"
    >
      <template #value="slotProps">
        <div class="flex items-center gap-2 text-surface-600 dark:text-surface-300">
          <Icon name="solar:filter-linear" class="text-primary-500 text-lg" />
          <span v-if="slotProps.value">{{ slotProps.value }}</span>
          <span v-else class="font-medium text-surface-600 dark:text-surface-400">
            {{ $t("classes.allLevels") }}
          </span>
        </div>
      </template>
    </LqSelect>
    <Button
      :label="$t('common.export')"
      class="w-full sm:w-auto sm:shrink-0 !bg-emerald-500 hover:!bg-emerald-600 !border-emerald-500 !text-white !rounded-xl !font-semibold !px-4 sm:!px-6 !text-sm sm:!text-base"
      @click="$emit('export')"
    >
      <template #icon>
        <Icon name="solar:export-linear" class="mr-2 text-lg" />
      </template>
    </Button>
  </div>
</template>
