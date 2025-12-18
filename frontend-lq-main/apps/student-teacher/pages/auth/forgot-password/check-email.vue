<script setup lang="ts">
  import { ref, computed } from "vue";
  import AuthCard from "~/components/AuthCard.vue";
  import { AUTH_ROUTES } from "@lq/types";
  import { useAuthNavigation } from "~/composables/useAuthNavigation";

  definePageMeta({
    layout: "auth",
  });

  const route = useRoute();
  const router = useRouter();
  const { handleResendPasswordReset } = useAuthNavigation();
  const isLoading = ref(false);

  const email = computed(() => (route.query.email as string) || "");

  const handleResend = async () => {
    if (!email.value) return;

    isLoading.value = true;
    await handleResendPasswordReset(email.value);
    isLoading.value = false;
  };
</script>

<template>
  <AuthCard title-key="auth.checkEmailTitle" subtitle-key="" show-stepper step-icon="solar:check-circle-linear">
    <div class="text-center space-y-4 sm:space-y-5 lg:space-y-6">
      <!-- Email sent message -->
      <div class="text-surface-600 dark:text-surface-300">
        <p>{{ $t("auth.sentInstructionsTo") }}</p>
        <p class="font-semibold text-surface-900 dark:text-white mt-1">{{ email }}</p>
      </div>

      <!-- Email icon -->
      <div class="flex justify-center my-4 sm:my-5 lg:my-6">
        <div class="relative">
          <Icon
            name="solar:letter-line-duotone"
            class="size-24 sm:size-28 lg:size-32 text-surface-300 dark:text-surface-600"
          />
          <div
            class="size-8 sm:size-9 absolute -top-2 -right-2 rounded-full bg-purple-600 flex items-center justify-center shadow-xl"
          >
            <Icon name="solar:check-circle-linear" class="size-5 sm:size-6 text-white" />
          </div>
        </div>
      </div>

      <!-- Resend link -->
      <div class="bg-surface-50 dark:bg-surface-800 rounded-lg p-3 sm:p-4 text-surface-600 dark:text-surface-300">
        <p class="text-xs sm:text-sm">
          {{ $t("auth.didntReceiveEmail") }}
          <button
            type="button"
            class="text-purple-600 hover:text-purple-700 dark:text-purple-400 dark:hover:text-purple-300 font-medium hover:underline focus:outline-none transition-colors text-xs sm:text-sm"
            :disabled="isLoading"
            @click="handleResend"
          >
            {{ $t("auth.resendLink") }}
          </button>
        </p>
      </div>

      <!-- Back to login button -->
      <Button
        severity="secondary"
        :label="$t('auth.backToLogin')"
        class="w-full h-11 sm:h-12 hover:!bg-primary-50 dark:hover:!bg-primary-900 transition-colors duration-200"
        outlined
        @click="router.push(AUTH_ROUTES.LOGIN)"
      />
    </div>
  </AuthCard>
</template>
