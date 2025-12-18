<script setup lang="ts">
  import { ThemeConfigurator } from "@lq/ui";

  const themeConfigurator = ref<InstanceType<typeof ThemeConfigurator>>();

  const toggle = (event: Event) => {
    themeConfigurator.value?.toggle(event);
  };

  defineExpose({
    toggle,
  });
</script>

<template>
  <ThemeConfigurator ref="themeConfigurator" show-primary show-surface show-menu-type />
</template>
