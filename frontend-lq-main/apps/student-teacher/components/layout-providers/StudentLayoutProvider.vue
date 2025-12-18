<script setup lang="ts">
  import BaseAppLayout from "./BaseAppLayout.vue";
</script>

<template>
  <BaseAppLayout
    sidebar-variant="simple"
    topbar-title="Student Portal"
    :topbar-notification-count="5"
    sidebar-role="student"
  >
    <slot />
  </BaseAppLayout>
</template>
