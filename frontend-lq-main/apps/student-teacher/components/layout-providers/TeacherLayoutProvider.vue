<script setup lang="ts">
  import BaseAppLayout from "./BaseAppLayout.vue";
</script>

<template>
  <BaseAppLayout
    sidebar-variant="grouped"
    topbar-title="Teacher Portal"
    :topbar-notification-count="15"
    :topbar-settings-badge-count="2"
    sidebar-role="teacher"
  >
    <slot />
  </BaseAppLayout>
</template>
