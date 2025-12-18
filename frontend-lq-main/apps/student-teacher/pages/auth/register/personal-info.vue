<script setup lang="ts">
  import { ref } from "vue";
  import * as z from "zod";
  import { useOnboardingStore } from "@lq/stores";
  import { AccountType, AUTH_ROUTES } from "@lq/types";
  import { useCompleteOnboarding } from "~/composables/useCompleteOnboarding";
  import { useAuthForm } from "~/composables/useAuthForm";

  const router = useRouter();
  const onboardingStore = useOnboardingStore();
  const { t } = useI18n();
  const { completeOnboarding } = useCompleteOnboarding();

  definePageMeta({
    layout: "auth",
    infoHeading: "Welcome to your English adventure!",
    infoSubheading: "We are ready to begin this amazing learning journey together",
  });

  const school = ref("");
  const firstName = ref("");
  const lastName = ref("");
  const birthday = ref<Date | null>(null);

  const buttonLabel = computed(() => {
    if (onboardingStore.accountType === AccountType.ADMIN_INSTITUCIONAL) {
      return t("auth.next");
    }
    return t("auth.finish");
  });

  const isLoading = ref(false);

  const { handleSubmit, fields } = useAuthForm({
    schema: z.object({
      firstName: z.string().min(1, "auth.firstNameRequired"),
      lastName: z.string().min(1, "auth.lastNameRequired"),
      birthday: z.date({ message: "auth.birthdayRequired" }).nullable(),
    }),
    fields: { firstName, lastName, birthday },
  });

  const handleFormSubmit = handleSubmit(async () => {
    if (!firstName.value || !lastName.value || !birthday.value) {
      return;
    }

    // Store personal info in onboarding store
    onboardingStore.setPersonalInfo({
      firstName: firstName.value,
      lastName: lastName.value,
      birthday: birthday.value,
      school: school.value,
    });

    if (onboardingStore.accountType === AccountType.ADMIN_INSTITUCIONAL) {
      await router.push(AUTH_ROUTES.REGISTER_INSTITUTION_INFO);
    } else {
      // Student/Teacher/Admin users complete onboarding via GraphQL
      isLoading.value = true;
      try {
        await completeOnboarding({
          firstName: firstName.value,
          lastName: lastName.value,
          birthday: birthday.value,
          school: school.value,
        });
      } catch (error) {
        // Error handling is done in the composable
        console.error("Onboarding completion error:", error);
      } finally {
        isLoading.value = false;
      }
    }
  });

  const handleBack = () => {
    const previousStep = onboardingStore.getPreviousStep(AUTH_ROUTES.REGISTER_PERSONAL_INFO);
    router.push(previousStep);
  };
</script>

<template>
  <div class="w-full max-w-md mx-auto relative px-4 sm:px-0">
    <div class="space-y-4 sm:space-y-6">
      <div class="flex items-center gap-2 sm:gap-3">
        <Icon name="noto:party-popper" :size="24" class="sm:text-[28px] lg:text-[32px]" />
        <h1 class="text-base sm:text-lg lg:text-xl font-bold dark:text-white leading-tight">
          {{ $t("auth.personalInfoTitle") }}
        </h1>
      </div>

      <form class="space-y-4 sm:space-y-6" @submit.prevent="handleFormSubmit">
        <div>
          <label for="school" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
            {{ $t("auth.whichSchool") }}
          </label>
          <InputText
            id="school"
            v-model="school"
            type="text"
            :placeholder="$t('auth.notAssociatedWithSchool')"
            class="w-full"
            disabled
          />
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
          <div>
            <label for="firstName" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
              {{ $t("auth.firstName") }}
            </label>
            <InputText
              id="firstName"
              v-model="firstName"
              type="text"
              placeholder="John"
              class="w-full"
              :invalid="!!fields.firstName.error.value"
              @blur="fields.firstName.validate"
            />
            <Message
              v-if="fields.firstName.error.value"
              severity="error"
              :closable="false"
              size="small"
              class="mt-1 block"
            >
              {{ $t(fields.firstName.error.value) }}
            </Message>
          </div>

          <div>
            <label for="lastName" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
              {{ $t("auth.lastName") }}
            </label>
            <InputText
              id="lastName"
              v-model="lastName"
              type="text"
              placeholder="Doe"
              class="w-full"
              :invalid="!!fields.lastName.error.value"
              @blur="fields.lastName.validate"
            />
            <Message
              v-if="fields.lastName.error.value"
              severity="error"
              :closable="false"
              size="small"
              class="mt-1 block"
            >
              {{ $t(fields.lastName.error.value) }}
            </Message>
          </div>
        </div>

        <div>
          <label for="birthday" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
            {{ $t("auth.birthday") }}
          </label>
          <DatePicker
            id="birthday"
            v-model="birthday"
            :placeholder="$t('auth.birthday')"
            class="w-full"
            :invalid="!!fields.birthday.error.value"
            show-icon
            icon-display="input"
            :pt="{
              pcInputText: {
                root: {
                  class: 'w-full hover:cursor-pointer text-sm sm:text-base',
                },
              },
              panel: {
                class: 'text-sm sm:text-base',
              },
            }"
          />
          <Message
            v-if="fields.birthday.error.value"
            severity="error"
            :closable="false"
            size="small"
            class="mt-1 block"
          >
            {{ $t(fields.birthday.error.value) }}
          </Message>
        </div>

        <div class="flex justify-between items-center pt-2 sm:pt-3 lg:pt-4">
          <Button text severity="secondary" :label="$t('auth.back')" class="text-sm sm:text-base" @click="handleBack">
            <template #icon>
              <Icon name="solar:arrow-left-linear" :size="18" class="sm:text-xl" />
            </template>
          </Button>
          <Button type="submit" severity="help" :label="buttonLabel" :loading="isLoading" />
        </div>
      </form>
    </div>
  </div>
</template>
