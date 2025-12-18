<script setup lang="ts">
  import { LqCard } from "@lq/ui";

  const handleEmailSupport = () => {
    // TODO: Open email client or support form
    window.location.href = "mailto:support@lingoquesto.com";
  };

  const handleChatSupport = () => {
    // TODO: Open chat support widget
  };
</script>

<template>
  <LqCard class="bg-success-50 dark:bg-success-900/20 border-success-200 dark:border-success-800">
    <template #header>
      <h3 class="text-xl font-bold text-surface-900 dark:text-surface-50">
        {{ $t("helpCenter.stillNeedHelp") }}
      </h3>
    </template>

    <div class="space-y-4">
      <!-- Support Availability -->
      <p class="text-sm text-surface-600 dark:text-surface-400">
        {{ $t("helpCenter.supportAvailability") }}
      </p>

      <!-- Buttons -->
      <div class="space-y-3">
        <!-- Email Support Button -->
        <button
          class="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-primary-600 hover:bg-primary-700 text-white font-medium transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
          @click="handleEmailSupport"
        >
          <Icon name="solar:letter-line-duotone" class="text-lg" aria-hidden="true" />
          <span>{{ $t("helpCenter.emailSupport") }}</span>
        </button>

        <!-- Chat Support Button -->
        <button
          class="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 text-surface-900 dark:text-surface-50 hover:bg-surface-50 dark:hover:bg-surface-800 font-medium transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
          @click="handleChatSupport"
        >
          <Icon name="solar:chat-round-dots-line-duotone" class="text-lg" aria-hidden="true" />
          <span>{{ $t("helpCenter.chatSupport") }}</span>
        </button>
      </div>
    </div>
  </LqCard>
</template>
