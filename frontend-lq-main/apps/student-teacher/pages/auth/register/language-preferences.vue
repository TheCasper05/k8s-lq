<script setup lang="ts">
  import { ref } from "vue";
  import { useField, useForm } from "vee-validate";
  import { toTypedSchema } from "@vee-validate/zod";
  import * as z from "zod";
  import { useOnboardingStore } from "@lq/stores";
  import { AccountType, AUTH_ROUTES } from "@lq/types";

  // Configure auth layout props for language preferences
  definePageMeta({
    layout: "auth",
    infoHeading: "Your personalized learning experience",
    infoSubheading: "Get tailored content and recommendations based on your language goals and location.",
  });

  const { t: $t } = useI18n();
  const router = useRouter();
  const onboardingStore = useOnboardingStore();

  // Form state
  const nativeLanguage = ref("");
  const languageToLearn = ref("");
  const country = ref("");

  // Validation schema (reactive)
  const schema = computed(() =>
    toTypedSchema(
      z.object({
        nativeLanguage: z.string().min(1, $t("auth.nativeLanguageRequired")),
        languageToLearn: z.string().min(1, $t("auth.languageToLearnRequired")),
        country: z.string().min(1, $t("auth.countryRequired")),
      }),
    ),
  );

  // Vee-validate setup
  const { handleSubmit: veeHandleSubmit } = useForm({
    validationSchema: schema,
  });

  const { value: nativeLanguageValue, errorMessage: nativeLanguageError } = useField<string>("nativeLanguage");
  const { value: languageToLearnValue, errorMessage: languageToLearnError } = useField<string>("languageToLearn");
  const { value: countryValue, errorMessage: countryError } = useField<string>("country");

  // Sync refs with vee-validate
  watch(nativeLanguage, (val) => {
    nativeLanguageValue.value = val;
  });

  watch(languageToLearn, (val) => {
    languageToLearnValue.value = val;
  });

  watch(country, (val) => {
    countryValue.value = val;
  });

  watch(nativeLanguageValue, (val) => {
    nativeLanguage.value = val || "";
  });

  watch(languageToLearnValue, (val) => {
    languageToLearn.value = val || "";
  });

  watch(countryValue, (val) => {
    country.value = val || "";
  });

  const validateNativeLanguage = () => {
    nativeLanguageValue.value = nativeLanguage.value;
  };

  const validateLanguageToLearn = () => {
    languageToLearnValue.value = languageToLearn.value;
  };

  const validateCountry = () => {
    countryValue.value = country.value;
  };

  // Mock data for dropdowns
  const languages = [
    { value: "en", label: "English" },
    { value: "es", label: "Español" },
    { value: "fr", label: "Français" },
    { value: "de", label: "Deutsch" },
    { value: "it", label: "Italiano" },
    { value: "pt", label: "Português" },
    { value: "zh", label: "中文" },
    { value: "ja", label: "日本語" },
    { value: "ar", label: "العربية" },
    { value: "ru", label: "Русский" },
  ];

  const { countries } = useCountries();

  // Dynamic label based on account type
  const languageFieldLabel = computed(() => {
    if (onboardingStore.accountType === AccountType.TEACHER) {
      return $t("auth.languageToTeach");
    }
    return $t("auth.languageToLearn");
  });

  const handleSubmit = veeHandleSubmit(() => {
    if (!nativeLanguage.value || !languageToLearn.value || !country.value) {
      return;
    }

    // Store language preferences in onboarding store
    onboardingStore.setLanguagePreferences({
      nativeLanguage: nativeLanguage.value,
      languageToLearn: languageToLearn.value,
      country: country.value,
    });

    // Navigate to personal info step
    router.push(AUTH_ROUTES.REGISTER_PERSONAL_INFO);
  });

  const handleBack = () => {
    // Determine where to go back based on flow type
    const previousStep = onboardingStore.getPreviousStep(AUTH_ROUTES.REGISTER_LANGUAGE_PREFS);
    router.push(previousStep);
  };
</script>

<template>
  <div class="w-full max-w-md mx-auto relative px-4 sm:px-0">
    <!-- Main Content - No card wrapper -->
    <div class="space-y-4 sm:space-y-5 lg:space-y-6">
      <!-- Header with Icon -->
      <div class="flex items-center gap-2 sm:gap-3">
        <Icon
          name="noto:globe-showing-europe-africa"
          :size="24"
          class="sm:text-[28px] lg:text-[32px] text-purple-600 dark:text-purple-400"
        />
        <h1 class="text-base sm:text-lg lg:text-xl font-bold dark:text-white leading-tight">
          {{ $t("auth.languagePreferencesTitle") }}
        </h1>
      </div>

      <form class="space-y-4 sm:space-y-5 lg:space-y-6" @submit.prevent="handleSubmit">
        <!-- Native Language Field -->
        <div>
          <label for="nativeLanguage" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
            {{ $t("auth.nativeLanguage") }}
          </label>
          <Select
            id="nativeLanguage"
            v-model="nativeLanguage"
            :options="languages"
            option-label="label"
            option-value="value"
            :placeholder="$t('auth.nativeLanguage')"
            class="w-full"
            :invalid="!!nativeLanguageError"
            @blur="validateNativeLanguage"
          />
          <Message v-if="nativeLanguageError" severity="error" :closable="false" size="small" class="mt-1 block">
            {{ nativeLanguageError }}
          </Message>
        </div>

        <!-- Language to Learn/Teach Field -->
        <div>
          <label for="languageToLearn" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
            {{ languageFieldLabel }}
          </label>
          <Select
            id="languageToLearn"
            v-model="languageToLearn"
            :options="languages"
            option-label="label"
            option-value="value"
            :placeholder="languageFieldLabel"
            class="w-full"
            :invalid="!!languageToLearnError"
            @blur="validateLanguageToLearn"
          />
          <Message v-if="languageToLearnError" severity="error" :closable="false" size="small" class="mt-1 block">
            {{ languageToLearnError }}
          </Message>
        </div>

        <!-- Country Field -->
        <div>
          <label for="country" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
            {{ $t("auth.country") }}
          </label>
          <Select
            id="country"
            v-model="country"
            :options="countries"
            option-label="label"
            option-value="value"
            :placeholder="$t('auth.country')"
            class="w-full"
            :invalid="!!countryError"
            @blur="validateCountry"
          />
          <Message v-if="countryError" severity="error" :closable="false" size="small" class="mt-1 block">
            {{ countryError }}
          </Message>
        </div>

        <!-- Action Buttons -->
        <div class="flex justify-between items-center pt-2 sm:pt-3 lg:pt-4">
          <Button text severity="secondary" :label="$t('auth.back')" class="text-sm sm:text-base" @click="handleBack">
            <template #icon>
              <Icon name="solar:arrow-left-linear" :size="18" class="sm:text-xl" />
            </template>
          </Button>
          <Button severity="help" :label="$t('auth.next')" @click="handleSubmit" />
        </div>
      </form>
    </div>
  </div>
</template>
