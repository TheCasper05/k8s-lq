<script setup lang="ts">
  import { ref, onMounted, computed } from "vue";
  import { useAuthStore } from "@lq/stores";
  import { AUTH_ROUTES } from "@lq/types";
  import { useAppToast } from "~/composables/useAppToast";
  import AuthCard from "~/components/AuthCard.vue";

  definePageMeta({
    layout: "auth",
  });

  const { t: $t } = useI18n();
  const authStore = useAuthStore();
  const router = useRouter();
  const route = useRoute();
  const toast = useAppToast();

  const isLoading = ref(false);
  const verificationStatus = ref<"pending" | "success" | "error" | "waiting">("waiting");

  // Get email from query params or from authStore
  const email = computed(() => {
    const queryEmail = route.query.email as string;
    return queryEmail || authStore.userAuth?.email || "";
  });

  // Check if there's a verification key in the URL
  const verificationKey = computed(() => {
    const paramKey = route.params.key ? String(route.params.key) : undefined;
    const queryKey = route.query.key ? String(route.query.key) : undefined;
    const key = paramKey ?? queryKey;
    return key ? decodeURIComponent(key) : undefined;
  });

  async function verifyEmailWithKey(key: string) {
    isLoading.value = true;
    verificationStatus.value = "pending";

    try {
      const result = await authStore.verifyEmail(key);

      if (result.success) {
        verificationStatus.value = "success";

        toast.success({
          summaryKey: "common.success",
          detailKey: "auth.emailVerified",
        });

        // Redirect to login after showing success message
        setTimeout(() => {
          router.push(AUTH_ROUTES.LOGIN);
        }, 3000);
      }
    } catch (error) {
      console.error("Email verification error:", error);
      verificationStatus.value = "error";

      toast.error({
        summaryKey: "common.error",
        detail: error instanceof Error ? error.message : $t("auth.verificationError"),
      });
    } finally {
      isLoading.value = false;
    }
  }

  async function handleResend() {
    if (!email.value) return;

    isLoading.value = true;

    try {
      await authStore.resendEmailVerification();

      toast.success({
        summaryKey: "common.success",
        detailKey: "auth.verificationEmailResent",
      });
    } catch (error) {
      console.error("Resend verification email error:", error);

      // Check if it's a 409 conflict error (email already verified or rate limited)
      const isConflictError = (error as Error & { isConflict?: boolean })?.isConflict === true;

      if (isConflictError) {
        toast.info({
          summaryKey: "common.info",
          detail: error instanceof Error ? error.message : $t("auth.verificationEmailAlreadySent"),
        });

        // Redirect to login after a short delay
        setTimeout(() => {
          router.push(AUTH_ROUTES.LOGIN);
        }, 2000);
      } else {
        toast.error({
          summaryKey: "common.error",
          detail: error instanceof Error ? error.message : $t("auth.verificationError"),
        });
      }
    } finally {
      isLoading.value = false;
    }
  }

  onMounted(async () => {
    // If there's a verification key in the URL, verify it automatically
    if (verificationKey.value) {
      await verifyEmailWithKey(verificationKey.value);
    }
  });
</script>

<template>
  <AuthCard
    :title-key="verificationStatus === 'success' ? 'auth.emailVerifiedTitle' : 'auth.checkEmailTitle'"
    subtitle-key=""
    show-stepper
    :step-icon="verificationStatus === 'success' ? 'solar:check-circle-linear' : 'solar:letter-line-duotone'"
  >
    <div class="text-center space-y-4 sm:space-y-5 lg:space-y-6">
      <!-- Pending State (Verifying) -->
      <div v-if="verificationStatus === 'pending'" class="py-3 sm:py-4">
        <div class="mb-4 sm:mb-5 lg:mb-6">
          <Icon
            name="solar:refresh-circle-line-duotone"
            class="size-24 sm:size-28 lg:size-32 text-purple-600 dark:text-purple-400 animate-spin"
          />
        </div>
        <p class="text-surface-700 dark:text-surface-300">
          {{ $t("auth.verifyingEmail") }}
        </p>
      </div>

      <!-- Success State (Email Verified) -->
      <div v-else-if="verificationStatus === 'success'" class="py-3 sm:py-4">
        <div class="flex justify-center mb-4 sm:mb-5 lg:mb-6">
          <Icon
            name="solar:check-circle-line-duotone"
            class="size-24 sm:size-28 lg:size-32 text-green-600 dark:text-green-400"
          />
        </div>
        <p class="text-surface-700 dark:text-surface-300 mb-4">
          {{ $t("auth.emailVerifiedMessage") }}
        </p>
        <p class="text-sm text-surface-600 dark:text-surface-400">
          {{ $t("auth.redirectingToLogin") }}
        </p>
      </div>

      <!-- Error State (Verification Failed) -->
      <div v-else-if="verificationStatus === 'error'" class="py-3 sm:py-4">
        <div class="flex justify-center mb-4 sm:mb-5 lg:mb-6">
          <Icon name="solar:close-circle-linear" class="size-24 sm:size-28 lg:size-32 text-red-600 dark:text-red-400" />
        </div>
        <p class="text-surface-700 dark:text-surface-300 mb-6">
          {{ $t("auth.verificationFailedMessage") }}
        </p>

        <!-- Resend link -->
        <div
          class="bg-surface-50 dark:bg-surface-800 rounded-lg p-3 sm:p-4 text-surface-600 dark:text-surface-300 mb-4 sm:mb-5 lg:mb-6"
        >
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

      <!-- Waiting State (Default - Just Registered) -->
      <div v-else>
        <!-- Email sent message -->
        <div v-if="email" class="text-surface-600 dark:text-surface-300">
          <p>{{ $t("auth.verificationEmailSent") }}</p>
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

        <div class="flex flex-col gap-2 sm:gap-3 my-2">
          <!-- Info message -->
          <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-3 sm:p-4 text-surface-700 dark:text-surface-300">
            <p class="text-xs sm:text-sm">
              {{ $t("auth.clickLinkInEmail") }}
            </p>
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
    </div>
  </AuthCard>
</template>
