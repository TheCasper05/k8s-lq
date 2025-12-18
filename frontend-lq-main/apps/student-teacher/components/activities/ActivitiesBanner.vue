<script setup lang="ts">
  import Button from "primevue/button";
  import { LqBanner } from "@lq/ui";

  interface Emits {
    create: [];
  }

  defineEmits<Emits>();

  const { t } = useI18n();
</script>

<template>
  <LqBanner
    size="lg"
    :title="t('teacher.scenarios.bannerTitle')"
    :description="t('teacher.scenarios.bannerSubtitle')"
    class="mb-6 sm:mb-8"
    icon-container-class="size-12 sm:size-16 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center"
  >
    <template #icon>
      <Icon name="lucide:message-square" class="text-white text-2xl sm:text-3xl" />
    </template>

    <template #action>
      <Button
        class="bg-white text-primary-600 border-0 font-bold px-4 sm:px-6 py-2.5 sm:py-3 rounded-xl shadow-md hover:bg-surface-50 transition-colors w-full sm:w-auto flex justify-center text-sm sm:text-base"
        @click="$emit('create')"
      >
        <div class="flex items-center gap-2">
          <Icon name="lucide:plus" class="text-lg sm:text-xl" />
          <span>{{ t("teacher.scenarios.createNew") }}</span>
        </div>
      </Button>
    </template>
  </LqBanner>
</template>
