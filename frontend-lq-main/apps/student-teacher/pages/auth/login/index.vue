<script setup lang="ts">
  import { AUTH_ROUTES } from "@lq/types";
  import AuthCard from "~/components/AuthCard.vue";
  import SocialButton from "~/components/SocialButton.vue";

  definePageMeta({
    layout: "auth",
  });
</script>

<template>
  <AuthCard title-key="auth.welcomeTitle" subtitle-key="auth.signInSubtitle" show-stepper>
    <!-- Social Login Buttons -->
    <div class="space-y-2.5 sm:space-y-3 mb-4 sm:mb-6">
      <SocialButton provider="google" :label="$t('auth.continueWithGoogle')" />
      <SocialButton provider="microsoft" :label="$t('auth.continueWithMicrosoft')" />
    </div>

    <!-- Divider -->
    <Divider align="center" type="solid" class="my-3 sm:my-4 lg:my-6">
      <span class="px-2 sm:px-3 text-gray-400 dark:text-surface-400 font-medium text-xs">
        {{ $t("auth.or") }}
      </span>
    </Divider>

    <!-- Email Login Button -->
    <NuxtLink :to="AUTH_ROUTES.LOGIN_EMAIL" class="block mb-4 sm:mb-6">
      <Button
        severity="secondary"
        unstyled
        class="w-full text-purple-600 hover:bg-purple-50 rounded-xl py-2.5 sm:py-3 dark:border-purple-400 dark:text-purple-300 dark:hover:bg-purple-900/20 duration-300"
      >
        <div class="flex items-center justify-center gap-2">
          <Icon name="solar:letter-linear" :size="20" class="sm:text-2xl" />
          <span>{{ $t("auth.continueWithEmail") }}</span>
        </div>
      </Button>
    </NuxtLink>

    <!-- Sign Up Link -->
    <div class="text-center text-xs sm:text-sm text-gray-600 dark:text-surface-400">
      {{ $t("auth.noAccount") }}
      <NuxtLink
        :to="AUTH_ROUTES.REGISTER"
        class="font-semibold text-purple-500 dark:text-purple-300 hover:text-purple-600 dark:hover:text-purple-400 transition-colors duration-200 ml-1"
      >
        {{ $t("auth.signUpFree") }}
      </NuxtLink>
    </div>
  </AuthCard>
</template>
