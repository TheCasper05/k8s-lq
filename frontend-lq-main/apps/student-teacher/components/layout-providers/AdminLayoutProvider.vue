<script setup lang="ts">
  import BaseAppLayout from "./BaseAppLayout.vue";
</script>

<template>
  <BaseAppLayout
    sidebar-variant="static"
    topbar-title="Admin Portal"
    :topbar-notification-count="8"
    sidebar-role="admin"
  >
    <slot />
  </BaseAppLayout>
</template>
