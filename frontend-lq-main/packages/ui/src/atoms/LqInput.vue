<script setup lang="ts">
  import { computed } from "vue";

  interface Props {
    id?: string;
    modelValue?: string | number;
    type?: string;
    label?: string;
    placeholder?: string;
    disabled?: boolean;
    required?: boolean;
    error?: string;
    hint?: string;
  }

  const props = withDefaults(defineProps<Props>(), {
    id: undefined,
    modelValue: undefined,
    type: "text",
    label: undefined,
    placeholder: undefined,
    disabled: false,
    required: false,
    error: undefined,
    hint: undefined,
  });

  const emit = defineEmits<{
    "update:modelValue": [value: string];
    "blur": [event: FocusEvent];
    "focus": [event: FocusEvent];
  }>();

  const internalValue = computed({
    get: () => props.modelValue,
    set: (value) => emit("update:modelValue", String(value)),
  });

  const inputClasses = computed(() => {
    const base =
      "block w-full rounded-lg border px-4 py-2 focus:outline-none focus:ring-2 focus:ring-offset-0 disabled:cursor-not-allowed disabled:bg-gray-50 disabled:text-gray-500";

    if (props.error) {
      return `${base} border-red-300 text-red-900 placeholder-red-300 focus:border-red-500 focus:ring-red-500`;
    }

    return `${base} border-gray-300 focus:border-primary-500 focus:ring-primary-500`;
  });
</script>

<template>
  <div class="w-full">
    <label v-if="label" :for="id" class="mb-2 block text-sm font-medium text-gray-700">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>

    <div class="relative">
      <input
        :id="id"
        v-model="internalValue"
        :type="type"
        :placeholder="placeholder"
        :disabled="disabled"
        :required="required"
        :class="inputClasses"
        @blur="emit('blur', $event)"
        @focus="emit('focus', $event)"
      />

      <div v-if="error" class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
        <svg class="size-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
          <path
            fill-rule="evenodd"
            d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
            clip-rule="evenodd"
          />
        </svg>
      </div>
    </div>

    <p v-if="error" class="mt-1 text-sm text-red-600">{{ error }}</p>
    <p v-else-if="hint" class="mt-1 text-sm text-gray-500">{{ hint }}</p>
  </div>
</template>
