<script setup lang="ts">
  import Button from "primevue/button";

  interface Option {
    label: string;
    value: unknown;
    icon?: string;
  }

  const props = withDefaults(
    defineProps<{
      modelValue: unknown;
      options: Option[];
      widthClass?: string;
      heightClass?: string;
    }>(),
    {
      widthClass: undefined,
      heightClass: "h-12",
    },
  );

  const emit = defineEmits<{
    (e: "update:modelValue", value: unknown): void;
  }>();

  const isSelected = (value: unknown) => props.modelValue === value;
</script>

<template>
  <div
    :class="[
      'flex bg-white dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-xl p-1',
      props.heightClass,
      props.widthClass,
    ]"
  >
    <Button
      v-for="option in props.options"
      :key="String(option.value)"
      :label="option.label"
      unstyled
      class="flex-1 h-full text-sm font-medium rounded-lg transition-all duration-200 flex items-center justify-center gap-2 px-4 cursor-pointer select-none ring-0 outline-none border-0"
      :class="[
        isSelected(option.value)
          ? 'bg-primary-600 text-white shadow-sm'
          : 'text-surface-600 dark:text-surface-400 hover:text-surface-900 dark:hover:text-surface-0 hover:bg-surface-50 dark:hover:bg-surface-800/50 bg-transparent',
      ]"
      @click="emit('update:modelValue', option.value)"
    >
      <template #icon v-if="option.icon">
        <Icon :name="option.icon" />
      </template>
    </Button>
  </div>
</template>
