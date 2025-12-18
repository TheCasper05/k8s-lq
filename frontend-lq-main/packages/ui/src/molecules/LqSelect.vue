<script setup lang="ts">
  import { computed } from "vue";
  import Select from "primevue/select";

  interface Props {
    options: unknown[];
    optionLabel?: string;
    optionValue?: string;
    placeholder?: string;
    showClear?: boolean;
    disabled?: boolean;
    loading?: boolean;
    pt?: Record<string, unknown>;

    valueIcon?: string;
    valueIconClass?: string;
    valueTextClass?: string;
    placeholderTextClass?: string;
  }

  const props = withDefaults(defineProps<Props>(), {
    optionLabel: undefined,
    optionValue: undefined,
    placeholder: undefined,
    showClear: false,
    disabled: false,
    loading: false,
    pt: undefined,

    valueIcon: "solar:filter-linear",
    valueIconClass: "text-primary-500 text-lg",
    valueTextClass: "flex items-center gap-2 text-surface-600 dark:text-surface-300",
    placeholderTextClass: "font-medium text-surface-600 dark:text-surface-400",
  });

  const modelValue = defineModel<unknown>();

  const defaultPT = {
    root: {
      class:
        "!rounded-xl !border !border-surface-200 dark:!border-surface-700 !bg-white dark:!bg-surface-900 !h-12 transition-colors duration-200 focus-within:!border-primary-500 dark:focus-within:!border-primary-400 focus-within:!border-2",
    },
    label: {
      class: "!h-full flex items-center !py-0",
    },
    dropdown: {
      class: "!h-full flex items-center",
    },
    clearIcon: {
      class: "!h-full flex items-center",
    },
  };

  const selectPT = computed(() => props.pt || defaultPT);

  const valueLabel = (value: unknown): string => {
    if (value === null || value === undefined) return "";
    if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") return String(value);
    if (typeof value === "object" && props.optionLabel) {
      const obj = value as Record<string, unknown>;
      const labelValue = obj[props.optionLabel];
      if (labelValue !== null && labelValue !== undefined) return String(labelValue);
    }
    return String(value);
  };
</script>

<template>
  <Select
    v-model="modelValue"
    :options="options"
    :option-label="optionLabel"
    :option-value="optionValue"
    :placeholder="placeholder"
    :show-clear="showClear"
    :disabled="disabled"
    :loading="loading"
    :pt="selectPT"
    class="w-full"
  >
    <template #value="slotProps">
      <slot name="value" v-bind="slotProps">
        <div :class="props.valueTextClass">
          <Icon v-if="props.valueIcon" :name="props.valueIcon" :class="props.valueIconClass" />
          <span v-if="slotProps.value">{{ valueLabel(slotProps.value) }}</span>
          <span v-else :class="props.placeholderTextClass">{{ props.placeholder }}</span>
        </div>
      </slot>
    </template>

    <template v-if="$slots.option" #option="slotProps">
      <slot name="option" v-bind="slotProps" />
    </template>

    <template v-if="$slots.dropdownicon" #dropdownicon="slotProps">
      <slot name="dropdownicon" v-bind="slotProps" />
    </template>

    <template v-if="$slots.header" #header="slotProps">
      <slot name="header" v-bind="slotProps" />
    </template>

    <template v-if="$slots.footer" #footer="slotProps">
      <slot name="footer" v-bind="slotProps" />
    </template>
  </Select>
</template>
