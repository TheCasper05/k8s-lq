<script setup lang="ts">
  import { ref, watch } from "vue";
  import type { StudentFilters } from "~/composables/students/types";
  import Select from "primevue/select";
  import IconField from "primevue/iconfield";
  import InputIcon from "primevue/inputicon";

  const props = defineProps<{
    filters: StudentFilters;
    availableLevels: string[];
  }>();

  const emit = defineEmits<{
    "update:filters": [filters: StudentFilters];
    "export": [];
  }>();

  const localFilters = ref<StudentFilters>({ ...props.filters });

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
</script>

<template>
  <div class="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center">
    <Select
      v-model="localFilters.level"
      :options="availableLevels"
      :placeholder="$t('students.levels')"
      class="w-full sm:w-auto min-w-[150px]"
      @update:model-value="updateFilters"
    />
    <IconField class="flex-1">
      <InputIcon>
        <Icon name="solar:magnifer-zoom-in-line-duotone" />
      </InputIcon>
      <InputText
        v-model="localFilters.search"
        :placeholder="$t('students.searchPlaceholder')"
        class="w-full"
        @update:model-value="updateFilters"
      />
    </IconField>
    <Button :label="$t('students.export')" variant="outlined" severity="secondary" @click="$emit('export')">
      <template #icon>
        <Icon name="solar:download-line-duotone" />
      </template>
    </Button>
  </div>
</template>
