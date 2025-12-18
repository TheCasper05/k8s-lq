<script setup lang="ts">
  import { ref, watch } from "vue";

  interface Props {
    modelValue?: string;
    placeholder?: string;
    debounce?: number;
  }

  const props = withDefaults(defineProps<Props>(), {
    modelValue: "",
    placeholder: "Search...",
    debounce: 300,
  });

  const emit = defineEmits<{
    "update:modelValue": [value: string];
    "search": [value: string];
  }>();

  const searchValue = ref(props.modelValue);
  let debounceTimer: ReturnType<typeof setTimeout>;

  watch(
    () => props.modelValue,
    (newValue) => {
      searchValue.value = newValue;
    },
  );

  const handleInput = () => {
    clearTimeout(debounceTimer);

    debounceTimer = setTimeout(() => {
      emit("update:modelValue", searchValue.value);
      emit("search", searchValue.value);
    }, props.debounce);
  };

  const clearSearch = () => {
    searchValue.value = "";
    emit("update:modelValue", "");
    emit("search", "");
  };
</script>

<template>
  <div class="relative">
    <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
      <svg class="size-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
        />
      </svg>
    </div>

    <input
      v-model="searchValue"
      type="search"
      :placeholder="placeholder"
      class="block w-full rounded-lg border border-gray-300 py-2 pl-10 pr-3 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
      @input="handleInput"
    />

    <button
      v-if="searchValue"
      type="button"
      class="absolute inset-y-0 right-0 flex items-center pr-3"
      @click="clearSearch"
    >
      <svg class="size-5 text-gray-400 hover:text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
  </div>
</template>
