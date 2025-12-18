<script setup lang="ts">
  interface Props {
    placeholder?: string;
    iconName?: string;
    width?: string;
  }

  withDefaults(defineProps<Props>(), {
    placeholder: "Search...",
    iconName: "solar:filter-linear",
    width: "w-64",
  });

  const modelValue = defineModel<string>();
</script>

<template>
  <IconField icon-position="left">
    <InputIcon>
      <Icon :name="iconName" class="text-lg text-surface-400" />
    </InputIcon>
    <InputText v-model="modelValue" :placeholder="placeholder" :class="['text-sm', width]" />
  </IconField>
</template>
