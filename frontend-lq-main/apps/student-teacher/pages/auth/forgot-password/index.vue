<script setup lang="ts">
  import { ref } from "vue";
  import { useField, useForm } from "vee-validate";
  import { toTypedSchema } from "@vee-validate/zod";
  import * as z from "zod";
  import AuthCard from "~/components/AuthCard.vue";
  import { AUTH_ROUTES } from "@lq/types";
  import { useAuthNavigation } from "~/composables/useAuthNavigation";

  definePageMeta({
    layout: "auth",
  });

  const { t: $t } = useI18n();
  const { handleForgotPassword } = useAuthNavigation();

  // Form state
  const email = ref("");
  const isLoading = ref(false);

  // Validation schema (reactive)
  const schema = computed(() =>
    toTypedSchema(
      z.object({
        email: z.string().min(1, $t("auth.emailRequired")).email($t("auth.emailInvalid")),
      }),
    ),
  );

  // Vee-validate setup
  const { handleSubmit: veeHandleSubmit } = useForm({
    validationSchema: schema,
    initialValues: {
      email: "",
    },
  });

  const { value: emailValue, errorMessage: emailError } = useField<string>("email");

  // Sync refs with vee-validate
  watch(email, (val) => {
    emailValue.value = val;
  });

  watch(emailValue, (val) => {
    email.value = val || "";
  });

  const validateEmail = () => {
    emailValue.value = email.value;
  };

  const handleSubmit = veeHandleSubmit(async () => {
    if (!email.value) return;

    isLoading.value = true;
    await handleForgotPassword(email.value);
    isLoading.value = false;
  });
</script>

<template>
  <AuthCard
    title-key="auth.forgotPasswordTitle"
    subtitle-key="auth.forgotPasswordSubtitle"
    show-stepper
    step-icon="solar:letter-line-duotone"
  >
    <form class="space-y-4 sm:space-y-5" @submit.prevent="handleSubmit">
      <!-- Email Field -->
      <div>
        <label for="email" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
          {{ $t("auth.emailLabel") }}
        </label>
        <InputText
          id="email"
          v-model="email"
          type="email"
          placeholder="your@email.com"
          class="w-full"
          :class="{ 'p-invalid': emailError }"
          @blur="validateEmail"
        />
        <Message v-if="emailError" severity="error" :closable="false" size="small" class="mt-1 block">
          {{ emailError }}
        </Message>
      </div>

      <!-- Send Reset Link Button -->
      <Button
        type="submit"
        :label="$t('auth.sendResetLink')"
        class="w-full h-11 sm:h-12 bg-gradient-to-r rounded-md transition-colors duration-200 text-white from-secondary-600 to-secondary-500 hover:from-secondary-700 hover:to-secondary-600 border-0 dark:from-secondary-500 dark:to-secondary-400 dark:hover:from-secondary-600 dark:hover:to-secondary-500"
        :loading="isLoading"
      />

      <!-- Back to Login -->
      <div class="text-center pt-4 sm:pt-5 lg:pt-6">
        <NuxtLink
          :to="AUTH_ROUTES.LOGIN_EMAIL"
          class="text-xs sm:text-sm text-surface-600 hover:text-surface-700 dark:text-surface-400 dark:hover:text-surface-300 transition-colors inline-flex items-center gap-2"
        >
          <Icon name="solar:alt-arrow-left-linear" :size="16" class="sm:text-base" />
          {{ $t("auth.backToLogin") }}
        </NuxtLink>
      </div>
    </form>
  </AuthCard>
</template>
