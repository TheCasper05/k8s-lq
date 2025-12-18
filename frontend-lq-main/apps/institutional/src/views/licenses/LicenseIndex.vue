<script setup lang="ts">
  import { useI18n } from "vue-i18n";
  import { Icon } from "@iconify/vue";

  const { t } = useI18n();
</script>

<template>
  <div class="p-6">
    <div class="bg-white rounded-2xl border border-gray-200 p-8 text-center">
      <Icon icon="solar:key-line-duotone" class="text-6xl text-gray-300 mb-4" />
      <h2 class="text-2xl font-bold text-gray-900 mb-2">{{ t("management.licenses.title") }}</h2>
      <p class="text-gray-600">{{ t("management.licenses.comingSoon") }}</p>
    </div>
  </div>
</template>
