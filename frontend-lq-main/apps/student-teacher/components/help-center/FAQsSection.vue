<script setup lang="ts">
  import { LqCard } from "@lq/ui";
  import type { FAQ } from "~/composables/help-center/useHelpCenterData";
  import FAQItem from "./FAQItem.vue";

  interface Props {
    faqs: FAQ[];
  }

  defineProps<Props>();

  const handleFAQClick = (_faqId: string) => {
    // TODO: Expand/collapse FAQ answer
  };
</script>

<template>
  <LqCard>
    <template #header>
      <div class="flex items-center gap-2">
        <div class="w-8 h-8 rounded-full bg-success-100 dark:bg-success-900/30 flex items-center justify-center">
          <Icon
            name="solar:question-circle-bold"
            class="text-lg text-success-600 dark:text-success-400"
            aria-hidden="true"
          />
        </div>
        <h3 class="text-xl font-bold text-surface-900 dark:text-surface-50">
          {{ $t("helpCenter.faqs") }}
        </h3>
      </div>
    </template>

    <div class="space-y-2">
      <FAQItem v-for="faq in faqs" :key="faq.id" :faq="faq" @click="handleFAQClick" />
    </div>
  </LqCard>
</template>
