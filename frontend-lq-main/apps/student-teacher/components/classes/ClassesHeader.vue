<script setup lang="ts">
  import { LqHero } from "@lq/ui";
  import Button from "primevue/button";

  defineEmits<{
    "create-class": [];
  }>();

  const { t } = useI18n();
</script>

<template>
  <LqHero
    variant="banner"
    size="lg"
    :title="t('classes.title')"
    :description="t('classes.subtitle')"
    class="mt-5"
    icon-container-class="size-16 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center"
  >
    <template #icon>
      <Icon name="solar:book-line-duotone" class="text-white text-3xl" />
    </template>

    <template #action>
      <Button
        class="bg-white text-primary-600 border-0 font-bold px-4 sm:px-6 py-2.5 sm:py-3 rounded-xl shadow-md hover:bg-surface-50 transition-colors w-full sm:w-auto flex justify-center text-sm sm:text-base"
        @click="$emit('create-class')"
      >
        <div class="flex items-center gap-2">
          <Icon name="lucide:plus" class="text-lg sm:text-xl" />
          <span>{{ t("classes.createNewClass") }}</span>
        </div>
      </Button>
    </template>
  </LqHero>
</template>
