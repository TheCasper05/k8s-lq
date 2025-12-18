<script setup lang="ts">
  import { useLayout } from "@lq/composables";
  import Toast from "primevue/toast";

  if (import.meta.client) {
    const _layout = useLayout();
  }

  onMounted(() => {});
</script>

<template>
  <Toast
    position="top-right"
    :breakpoints="{ '640px': { position: 'top-center' }, '768px': { width: '25rem' } }"
    :pt="{
      root: { class: 'text-sm sm:text-base max-w-[20rem] sm:max-w-[25rem]' },
      message: { class: 'p-2 sm:p-3' },
      content: { class: 'gap-2 sm:gap-3 items-start' },
      icon: { class: 'mt-0.5' },
      text: { class: 'text-sm sm:text-base flex-1' },
      summary: { class: 'font-semibold text-sm sm:text-base' },
      detail: { class: 'text-xs sm:text-sm' },
      transition: {
        enterFromClass: 'toast-enter-from',
        enterActiveClass: 'toast-enter-active',
        leaveActiveClass: 'toast-leave-active',
        leaveToClass: 'toast-leave-to',
      },
    }"
  />
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

<style>
  /* Toast positioning - Mobile/Tablet (centered) */
  @media (max-width: 767px) {
    .p-toast-top-center {
      left: 50% !important;
      transform: translateX(-50%);
    }

    .p-toast-top-center .p-toast-message {
      margin: 0 auto;
    }
  }

  /* Toast transitions - Desktop (from/to right) */
  @media (min-width: 768px) {
    .toast-enter-from,
    .toast-leave-to {
      transform: translateX(100%);
      opacity: 0;
    }
  }

  /* Toast transitions - Mobile/Tablet (from/to top) */
  @media (max-width: 767px) {
    .toast-enter-from,
    .toast-leave-to {
      transform: translateY(-100%);
      opacity: 0;
    }
  }

  /* Toast transition timing */
  .toast-enter-active,
  .toast-leave-active {
    transition: all 0.3s ease-out;
  }

  /* Page transitions - Forward (going to next page, e.g., login -> dashboard) */
  .page-forward-enter-active,
  .page-forward-leave-active {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .page-forward-enter-from {
    opacity: 0;
    transform: translateX(30px); /* Enter from right */
  }

  .page-forward-leave-to {
    opacity: 0;
    transform: translateX(-30px); /* Exit to left */
  }

  .page-forward-enter-to,
  .page-forward-leave-from {
    opacity: 1;
    transform: translateX(0);
  }

  /* Page transitions - Backward (going back, e.g., logout, back button) */
  .page-backward-enter-active,
  .page-backward-leave-active {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .page-backward-enter-from {
    opacity: 0;
    transform: translateX(-30px); /* Enter from left */
  }

  .page-backward-leave-to {
    opacity: 0;
    transform: translateX(30px); /* Exit to right */
  }

  .page-backward-enter-to,
  .page-backward-leave-from {
    opacity: 1;
    transform: translateX(0);
  }

  /* Layout transitions - For auth -> default layout changes */
  .layout-enter-active,
  .layout-leave-active {
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .layout-enter-from {
    opacity: 0;
    transform: translateY(20px) scale(0.98);
  }

  .layout-leave-to {
    opacity: 0;
    transform: translateY(-20px) scale(0.98);
  }

  .layout-enter-to,
  .layout-leave-from {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
</style>
