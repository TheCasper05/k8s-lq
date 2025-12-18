<script setup lang="ts">
  import type { PrimaryColor, SurfaceColor } from "@lq/composables";

  defineOptions({
    name: "ColorPicker",
  });

  interface Props {
    /**
     * Array of colors to display
     */
    colors: PrimaryColor[] | SurfaceColor[];
    /**
     * Currently selected color name
     */
    modelValue: string | null;
    /**
     * Label for the color picker
     */
    label?: string;
    /**
     * Function to determine if a color is selected
     */
    isSelected?: (colorName: string) => boolean;
  }

  const props = defineProps<Props>();

  const emit = defineEmits<{
    "update:modelValue": [value: string];
    "change": [value: string];
  }>();

  const handleColorSelect = (colorName: string) => {
    emit("update:modelValue", colorName);
    emit("change", colorName);
  };

  const isColorSelected = (colorName: string): boolean => {
    if (props.isSelected) {
      return props.isSelected(colorName);
    }
    return props.modelValue === colorName;
  };
</script>

<template>
  <div class="flex flex-col gap-2">
    <span v-if="label" class="text-sm text-surface-600 dark:text-surface-400 font-semibold">
      {{ label }}
    </span>
    <div class="flex flex-wrap gap-2">
      <button
        v-for="color of colors"
        :key="color.name"
        type="button"
        :title="color.name"
        :class="[
          'size-6 rounded-full p-0 cursor-pointer border-2',
          'transition-all duration-200',
          'hover:scale-110',
          'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500',
          {
            'ring-2 ring-primary-500 ring-offset-2 scale-110 border-primary-500': isColorSelected(color.name),
            'border-surface-300 dark:border-surface-600': !isColorSelected(color.name),
          },
        ]"
        :style="{ backgroundColor: color.palette['500'] }"
        :aria-label="`Select ${color.name} color`"
        :aria-pressed="isColorSelected(color.name)"
        @click="handleColorSelect(color.name)"
      />
    </div>
  </div>
</template>
