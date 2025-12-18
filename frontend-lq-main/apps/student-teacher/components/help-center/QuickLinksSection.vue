<script setup lang="ts">
  import { LqCard } from "@lq/ui";
  import type { QuickLink } from "~/composables/help-center/useHelpCenterData";
  import QuickLinkItem from "./QuickLinkItem.vue";

  interface Props {
    links: QuickLink[];
  }

  defineProps<Props>();
</script>

<template>
  <LqCard>
    <template #header>
      <h3 class="text-xl font-bold text-surface-900 dark:text-surface-50">
        {{ $t("helpCenter.quickLinks") }}
      </h3>
    </template>

    <div class="space-y-2">
      <QuickLinkItem v-for="link in links" :key="link.id" :link="link" />
    </div>
  </LqCard>
</template>
