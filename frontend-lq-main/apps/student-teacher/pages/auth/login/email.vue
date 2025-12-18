<script setup lang="ts">
  import { ref } from "vue";
  import { useAuthStore } from "@lq/stores";
  import * as z from "zod";
  import AuthCard from "~/components/AuthCard.vue";
  import { useAuthForm } from "~/composables/useAuthForm";
  import { useAuthNavigation } from "~/composables/useAuthNavigation";
  import { useAppToast } from "~/composables/useAppToast";
  import { AUTH_ROUTES } from "@lq/types";

  definePageMeta({
    layout: "auth",
  });

  const authStore = useAuthStore();
  const toast = useAppToast();
  const { t } = useI18n();
  const { handlePostLogin } = useAuthNavigation();
  const config = useRuntimeConfig();
  const BYPASS_ONBOARDING = config.public.bypassOnboarding;

  const { t: $t } = useI18n();

  const email = ref("");
  const password = ref("");
  const rememberMe = ref(false);

  // Auto-lowercase email
  watch(email, (val) => {
    if (val && val !== val.toLowerCase()) {
      email.value = val.toLowerCase();
    }
  });

  const { handleSubmit, fields } = useAuthForm({
    schema: z.object({
      email: z.string().min(1, "auth.emailRequired").email("auth.emailInvalid"),
      password: z.string().min(1, "auth.passwordRequired"),
    }),
    fields: { email, password },
  });

  const handleFormSubmit = handleSubmit(async () => {
    if (email.value) {
      email.value = email.value.toLowerCase();
    }

    if (!email.value || !password.value) {
      toast.auth.validationError();
      return;
    }

    try {
      // In bypass mode, skip login API and go directly to post-login navigation
      if (BYPASS_ONBOARDING) {
        await handlePostLogin({ success: true });
        return;
      }

      const result = await authStore.login(email.value, password.value);
      await handlePostLogin(result);
    } catch (error: unknown) {
      console.error("Login failed:", error);

      const normalizedError = error as { status?: number; code?: string } | undefined;
      const status = normalizedError?.status;
      const code = normalizedError?.code;

      if (status === 401 && code === "invalid_credentials") {
        toast.auth.loginError(t("auth.invalidCredentials"));
        return;
      }

      const errorMessage = error instanceof Error && error.message ? error.message : undefined;
      toast.auth.loginError(errorMessage);
    }
  });
</script>

<template>
  <AuthCard>
    <form class="space-y-4 sm:space-y-5 lg:space-y-6" @submit.prevent="handleFormSubmit">
      <!-- Email Field -->
      <div>
        <label for="email" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
          {{ $t("auth.email") }}
        </label>
        <InputText
          id="email"
          v-model="email"
          type="email"
          :placeholder="$t('auth.emailPlaceholder')"
          class="w-full"
          :invalid="!!fields.email.error.value"
          @blur="fields.email.validate"
        />
        <Message v-if="fields.email.error.value" severity="error" :closable="false" size="small" class="mt-1 block">
          {{ $t(fields.email.error.value) }}
        </Message>
      </div>

      <!-- Password Field -->
      <div>
        <label for="password" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
          {{ $t("auth.password") }}
        </label>
        <Password
          id="password"
          v-model="password"
          :placeholder="$t('auth.passwordPlaceholder')"
          toggle-mask
          :feedback="false"
          class="w-full"
          :invalid="!!fields.password.error.value"
          :pt="{
            pcInputText: {
              root: {
                class: 'w-full',
              },
            },
          }"
          @blur="fields.password.validate"
        />
        <Message v-if="fields.password.error.value" severity="error" :closable="false" size="small" class="mt-1 block">
          {{ $t(fields.password.error.value) }}
        </Message>
      </div>

      <!-- Remember Me & Forgot Password -->
      <div class="flex items-center justify-between pt-1 sm:pt-2">
        <div class="flex items-center">
          <Checkbox v-model="rememberMe" input-id="remember" binary />
          <label for="remember" class="ml-2 text-xs sm:text-sm text-surface-700 dark:text-surface-300 cursor-pointer">
            {{ $t("auth.rememberMe") }}
          </label>
        </div>
        <NuxtLink
          :to="AUTH_ROUTES.FORGOT_PASSWORD"
          class="text-xs sm:text-sm font-medium text-purple-600 hover:text-purple-700 dark:text-purple-400 dark:hover:text-purple-300 transition-colors"
        >
          {{ $t("auth.forgotPassword") }}
        </NuxtLink>
      </div>

      <!-- Sign In Button -->
      <div class="pt-2 sm:pt-3 lg:pt-4">
        <Button
          type="submit"
          :label="$t('auth.loginButton')"
          class="w-full h-11 sm:h-12 bg-gradient-to-r rounded-md transition-colors duration-200 text-white from-secondary-600 to-secondary-500 hover:from-secondary-700 hover:to-secondary-600 border-0 dark:from-secondary-500 dark:to-secondary-400 dark:hover:from-secondary-600 dark:hover:to-secondary-500"
          :loading="authStore.loading"
        />
      </div>

      <!-- Back to Login Options -->
      <div class="text-center pt-4 sm:pt-5 lg:pt-6">
        <NuxtLink
          :to="AUTH_ROUTES.LOGIN"
          class="text-xs sm:text-sm text-surface-600 hover:text-surface-700 dark:text-surface-400 dark:hover:text-surface-300 transition-colors inline-flex items-center gap-2"
        >
          <Icon name="solar:alt-arrow-left-linear" :size="16" class="sm:text-base" />
          {{ $t("auth.backToLoginOptions") }}
        </NuxtLink>
      </div>
    </form>
  </AuthCard>
</template>
