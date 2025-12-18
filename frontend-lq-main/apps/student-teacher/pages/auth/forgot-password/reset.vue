<script setup lang="ts">
  import { ref, computed } from "vue";
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
  const route = useRoute();
  const { handleResetPassword } = useAuthNavigation();

  // Extract key from URL params (dynamic route) or query params
  const resetKey = computed(() => (route.params.key as string) || (route.query.key as string));

  // Form state
  const password = ref("");
  const confirmPassword = ref("");
  const isLoading = ref(false);

  // Validation schema (same as register)
  const schema = computed(() =>
    toTypedSchema(
      z
        .object({
          password: z.string().min(6, $t("auth.passwordMin")),
          confirmPassword: z.string().min(1, $t("auth.passwordRequired")),
        })
        .refine((data) => data.password === data.confirmPassword, {
          message: $t("auth.passwordsMatch"),
          path: ["confirmPassword"],
        }),
    ),
  );

  // Vee-validate setup
  const { handleSubmit: veeHandleSubmit } = useForm({
    validationSchema: schema,
  });

  const { value: passwordValue, errorMessage: passwordError } = useField<string>("password");
  const { value: confirmPasswordValue, errorMessage: confirmPasswordError } = useField<string>("confirmPassword");

  // Sync refs with vee-validate
  watch(password, (val) => {
    passwordValue.value = val;
  });

  watch(confirmPassword, (val) => {
    confirmPasswordValue.value = val;
  });

  watch(passwordValue, (val) => {
    password.value = val || "";
  });

  watch(confirmPasswordValue, (val) => {
    confirmPassword.value = val || "";
  });

  const validatePassword = () => {
    passwordValue.value = password.value;
  };

  const validateConfirmPassword = () => {
    confirmPasswordValue.value = confirmPassword.value;
  };

  // Check if key exists on mount
  onMounted(() => {
    if (!resetKey.value) {
      navigateTo(AUTH_ROUTES.FORGOT_PASSWORD);
    }
  });

  const handleSubmit = veeHandleSubmit(async () => {
    if (!password.value || !confirmPassword.value || !resetKey.value) return;

    isLoading.value = true;
    await handleResetPassword(resetKey.value, password.value, confirmPassword.value);
    isLoading.value = false;
  });
</script>

<template>
  <AuthCard
    title-key="auth.resetPasswordTitle"
    subtitle-key="auth.resetPasswordSubtitle"
    show-stepper
    step-icon="solar:lock-password-line-duotone"
  >
    <form class="space-y-4 sm:space-y-5" @submit.prevent="handleSubmit">
      <!-- New Password Field -->
      <div>
        <label for="password" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
          {{ $t("auth.newPassword") }}
        </label>
        <Password
          id="password"
          v-model="password"
          :placeholder="$t('auth.passwordPlaceholder')"
          toggle-mask
          :feedback="false"
          class="w-full"
          :invalid="!!passwordError"
          :pt="{
            pcInputText: {
              root: {
                class: 'w-full',
              },
            },
          }"
          @blur="validatePassword"
        />
        <Message v-if="passwordError" severity="error" :closable="false" size="small" class="mt-1 block">
          {{ passwordError }}
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
          :invalid="!!confirmPasswordError"
          :pt="{
            pcInputText: {
              root: {
                class: 'w-full',
              },
            },
          }"
          @blur="validateConfirmPassword"
        />
        <Message v-if="confirmPasswordError" severity="error" :closable="false" size="small" class="mt-1 block">
          {{ confirmPasswordError }}
        </Message>
      </div>

      <!-- Reset Password Button -->
      <Button
        type="submit"
        :label="$t('auth.resetPassword')"
        class="w-full h-11 sm:h-12 bg-gradient-to-r rounded-md transition-colors duration-200 text-white from-secondary-600 to-secondary-500 hover:from-secondary-700 hover:to-secondary-600 border-0 dark:from-secondary-500 dark:to-secondary-400 dark:hover:from-secondary-600 dark:hover:to-secondary-500"
        :loading="isLoading"
      />
    </form>
  </AuthCard>
</template>
