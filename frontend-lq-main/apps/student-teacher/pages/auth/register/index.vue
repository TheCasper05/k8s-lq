<script setup lang="ts">
  import { ref } from "vue";
  import * as z from "zod";
  import { FlowType, AUTH_ROUTES } from "@lq/types";
  import { useAuthStore, useOnboardingStore } from "@lq/stores";
  import AuthCard from "~/components/AuthCard.vue";
  import SocialButton from "~/components/SocialButton.vue";
  import { useAuthForm } from "~/composables/useAuthForm";
  import { useAuthNavigation } from "~/composables/useAuthNavigation";
  import { useAppToast } from "~/composables/useAppToast";

  definePageMeta({
    layout: "auth",
  });

  const { t } = useI18n();
  const authStore = useAuthStore();
  const onboardingStore = useOnboardingStore();
  const router = useRouter();
  const toast = useAppToast();
  const { handlePostRegister } = useAuthNavigation();

  const email = ref("");
  const password = ref("");
  const confirmPassword = ref("");
  const isLoading = ref(false);

  // Auto-lowercase email
  watch(email, (val) => {
    if (val && val !== val.toLowerCase()) {
      email.value = val.toLowerCase();
    }
  });

  const { handleSubmit, fields } = useAuthForm({
    schema: z
      .object({
        email: z.string().min(1, "auth.emailRequired").email("auth.emailInvalid"),
        password: z.string().min(6, "auth.passwordMin"),
        confirmPassword: z.string().min(1, "auth.passwordRequired"),
      })
      .refine((data) => data.password === data.confirmPassword, {
        message: "auth.passwordsMatch",
        path: ["confirmPassword"],
      }),
    fields: { email, password, confirmPassword },
  });

  const handleFormSubmit = handleSubmit(async () => {
    if (email.value) {
      email.value = email.value.toLowerCase();
    }

    if (!email.value || !password.value || !confirmPassword.value) {
      toast.auth.validationError();
      return;
    }

    isLoading.value = true;

    try {
      const result = await authStore.register({
        email: email.value,
        password: password.value,
        password2: confirmPassword.value,
      });

      if (result.success) {
        onboardingStore.setFlowType(FlowType.REGISTER);
        onboardingStore.setRegistrationData({
          email: email.value,
          password: password.value,
          password2: confirmPassword.value,
        });

        await handlePostRegister(result);
      }
    } catch (error: unknown) {
      console.error("Registration error:", error);

      const normalizedError = error as { status?: number; code?: string } | undefined;
      const status = normalizedError?.status;
      const code = normalizedError?.code;

      if (status === 400 && code === "email_taken") {
        // Specific toast for email already exists
        toast.error({
          summaryKey: "common.error",
          detailKey: "auth.emailAlreadyExists",
          life: 5000,
        });

        // Redirect to login after 2 seconds
        setTimeout(() => {
          router.push(AUTH_ROUTES.LOGIN);
        }, 2000);
        return;
      }

      // Generic error
      const errorMessage = error instanceof Error && error.message ? error.message : undefined;
      toast.error({
        summaryKey: "common.error",
        detail: errorMessage || t("auth.registrationError"),
        life: 5000,
      });
    } finally {
      isLoading.value = false;
    }
  });
</script>

<template>
  <AuthCard title-key="auth.createAccount" subtitle-key="" show-stepper>
    <!-- Already have account link -->
    <div class="text-center text-xs sm:text-sm text-purple-300 dark:text-purple-400 mb-4 sm:mb-6">
      <NuxtLink
        :to="AUTH_ROUTES.LOGIN"
        class="font-semibold text-purple-500 dark:text-purple-300 hover:text-purple-600 dark:hover:text-purple-400 transition-colors duration-200 ml-1"
      >
        {{ $t("auth.hasAccount") }}
      </NuxtLink>
    </div>

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

      <!-- Confirm Password Field -->
      <div>
        <label for="confirmPassword" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
          {{ $t("auth.confirmPassword") }}
        </label>
        <Password
          id="confirmPassword"
          v-model="confirmPassword"
          :placeholder="$t('auth.confirmPasswordPlaceholder')"
          toggle-mask
          :feedback="false"
          class="w-full"
          :invalid="!!fields.confirmPassword.error.value"
          :pt="{
            pcInputText: {
              root: {
                class: 'w-full',
              },
            },
          }"
          @blur="fields.confirmPassword.validate"
        />
        <Message
          v-if="fields.confirmPassword.error.value"
          severity="error"
          :closable="false"
          size="small"
          class="mt-1 block"
        >
          {{ $t(fields.confirmPassword.error.value) }}
        </Message>
      </div>

      <!-- Register Button -->
      <div class="pt-2 sm:pt-3 lg:pt-4">
        <Button
          type="submit"
          :label="$t('auth.createAccountButton')"
          :loading="isLoading"
          class="w-full h-11 sm:h-12 bg-gradient-to-r rounded-md transition-colors duration-200 text-white from-secondary-600 to-secondary-500 hover:from-secondary-700 hover:to-secondary-600 border-0 dark:from-secondary-500 dark:to-secondary-400 dark:hover:from-secondary-600 dark:hover:to-secondary-500"
        />
      </div>
    </form>

    <!-- Divider -->
    <div class="relative my-4 sm:my-5 lg:my-6">
      <div class="absolute inset-0 flex items-center">
        <div class="w-full border-t border-gray-200 dark:border-surface-700" />
      </div>
      <div class="relative flex justify-center text-xs sm:text-sm">
        <span class="px-3 sm:px-4 bg-white dark:bg-surface-900 text-gray-500 dark:text-surface-400">
          {{ $t("auth.orContinueWith") }}
        </span>
      </div>
    </div>

    <!-- Social Register Buttons -->
    <div class="grid grid-cols-2 gap-2 sm:gap-3">
      <SocialButton provider="google" variant="compact" />
      <SocialButton provider="microsoft" variant="compact" />
    </div>
  </AuthCard>
</template>
