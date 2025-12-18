<script setup lang="ts">
  import { computed } from "vue";
  import InputText from "primevue/inputtext";
  import IconField from "primevue/iconfield";
  import InputIcon from "primevue/inputicon";

  interface Props {
    /**
     * The search query value (v-model)
     */
    modelValue?: string;
    /**
     * Placeholder text
     */
    placeholder?: string;

    /**
     * Icon name (SearchFilter compatibility)
     */
    iconName?: string;

    /**
     * Input width classes (SearchFilter compatibility)
     */
    width?: string;

    /**
     * Wrapper classes for the IconField container
     */
    containerClass?: string;
    /**
     * Icon name (default: solar:magnifer-linear)
     */
    icon?: string;
    /**
     * Icon position
     */
    iconPosition?: "left" | "right";
    /**
     * Custom input classes
     */
    inputClass?: string;
    /**
     * Disable the input
     */
    disabled?: boolean;
  }

  const props = withDefaults(defineProps<Props>(), {
    modelValue: "",
    placeholder: "Search...",
    iconName: undefined,
    width: "w-full",
    containerClass: "w-full",
    icon: "solar:magnifer-linear",
    iconPosition: "left",
    inputClass: "",
    disabled: false,
  });

  const emit = defineEmits<{
    "update:modelValue": [value: string];
    "search": [value: string];
  }>();

  const inputClasses = computed(() => {
    if (props.inputClass) return props.inputClass;
    return [
      "text-sm",
      props.width,
      "!rounded-xl",
      "!border",
      "!border-surface-200",
      "dark:!border-surface-700",
      "!bg-white",
      "dark:!bg-surface-900",
      "!h-12",
      "transition-colors",
      "duration-200",
      "focus:!border-primary-500",
      "dark:focus:!border-primary-400",
      "focus:!border-2",
      "focus:!ring-offset-0",
    ];
  });

  const containerClasses = computed(() => props.containerClass);

  const resolvedIcon = computed(() => props.iconName || props.icon);

  const handleInput = (event: Event) => {
    const value = (event.target as HTMLInputElement).value;
    emit("update:modelValue", value);
    emit("search", value);
  };
</script>

<template>
  <IconField :icon-position="iconPosition" :class="containerClasses">
    <InputIcon>
      <slot name="icon" :icon="resolvedIcon">
        <Icon :name="resolvedIcon" class="text-lg text-surface-400" />
      </slot>
    </InputIcon>
    <InputText
      :model-value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :class="inputClasses"
      @input="handleInput"
    />
  </IconField>
</template>
