<template>
  <div />
</template>

<script setup lang="ts">
  definePageMeta({
    layout: false,
    middleware: [
      function () {
        return navigateTo("/admin/dashboard");
      },
    ],
  });
</script>
