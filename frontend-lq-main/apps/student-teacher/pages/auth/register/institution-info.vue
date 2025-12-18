<script setup lang="ts">
  import { useField, useForm } from "vee-validate";
  import { toTypedSchema } from "@vee-validate/zod";
  import * as z from "zod";
  import { useOnboardingStore } from "@lq/stores";
  import { AUTH_ROUTES } from "@lq/types";
  import { useCompleteOnboarding } from "~/composables/useCompleteOnboarding";

  const { t: $t } = useI18n();
  const router = useRouter();
  const onboardingStore = useOnboardingStore();

  const { completeOnboarding } = useCompleteOnboarding();

  // Configure auth layout props
  definePageMeta({
    layout: "auth",
    infoHeading: "Set up your institution",
    infoSubheading: "Configure your institution to start managing students and teachers",
  });

  // Form state
  const institutionName = ref("");
  const description = ref("");
  const logo = ref<File | null>(null);
  const logoPreview = ref<string | null>(null);
  const logoError = ref("");
  const website = ref("");
  const contactEmail = ref("");
  const address = ref("");
  const city = ref("");
  const country = ref("");
  const isLoading = ref(false);

  // Validation schema (reactive)
  const schema = computed(() =>
    toTypedSchema(
      z.object({
        institutionName: z.string().min(1, $t("auth.institutionNameRequired")),
        description: z.string().min(1, $t("auth.descriptionRequired")),
        website: z.string().min(1, $t("auth.websiteRequired")).url($t("auth.websiteInvalid")),
        contactEmail: z.string().min(1, $t("auth.contactEmailRequired")).email($t("auth.contactEmailInvalid")),
        address: z.string().min(1, $t("auth.addressRequired")),
        city: z.string().min(1, $t("auth.cityRequired")),
        country: z.string().min(1, $t("auth.countryRequired")),
      }),
    ),
  );

  // Vee-validate setup
  const { handleSubmit: veeHandleSubmit } = useForm({
    validationSchema: schema,
  });

  const { value: institutionNameValue, errorMessage: institutionNameError } = useField<string>("institutionName");
  const { value: descriptionValue, errorMessage: descriptionError } = useField<string>("description");
  const { value: websiteValue, errorMessage: websiteError } = useField<string>("website");
  const { value: contactEmailValue, errorMessage: contactEmailError } = useField<string>("contactEmail");
  const { value: addressValue, errorMessage: addressError } = useField<string>("address");
  const { value: cityValue, errorMessage: cityError } = useField<string>("city");
  const { value: countryValue, errorMessage: countryError } = useField<string>("country");

  // Sync refs with vee-validate
  watch(institutionName, (val) => {
    institutionNameValue.value = val;
  });

  watch(description, (val) => {
    descriptionValue.value = val;
  });

  watch(website, (val) => {
    websiteValue.value = val;
  });

  watch(contactEmail, (val) => {
    contactEmailValue.value = val;
  });

  watch(address, (val) => {
    addressValue.value = val;
  });

  watch(city, (val) => {
    cityValue.value = val;
  });

  watch(country, (val) => {
    countryValue.value = val;
  });

  watch(institutionNameValue, (val) => {
    institutionName.value = val || "";
  });

  watch(descriptionValue, (val) => {
    description.value = val || "";
  });

  watch(websiteValue, (val) => {
    website.value = val || "";
  });

  watch(contactEmailValue, (val) => {
    contactEmail.value = val || "";
  });

  watch(addressValue, (val) => {
    address.value = val || "";
  });

  watch(cityValue, (val) => {
    city.value = val || "";
  });

  watch(countryValue, (val) => {
    country.value = val || "";
  });

  const validateInstitutionName = () => {
    institutionNameValue.value = institutionName.value;
  };

  const validateDescription = () => {
    descriptionValue.value = description.value;
  };

  const validateWebsite = () => {
    websiteValue.value = website.value;
  };

  const validateContactEmail = () => {
    contactEmailValue.value = contactEmail.value;
  };

  const validateAddress = () => {
    addressValue.value = address.value;
  };

  const validateCity = () => {
    cityValue.value = city.value;
  };

  const validateCountry = () => {
    countryValue.value = country.value;
  };

  // Countries dropdown
  const { countries } = useCountries();

  const handleFileUpload = (event: Event) => {
    const target = event.target as HTMLInputElement;
    if (target.files && target.files[0]) {
      const file = target.files[0];
      logo.value = file;
      logoError.value = "";

      const reader = new FileReader();
      reader.onload = (e) => {
        logoPreview.value = e.target?.result as string;
      };
      reader.readAsDataURL(file);
    }
  };

  const validateLogo = () => {
    if (!logo.value) {
      logoError.value = $t("auth.logoRequired");
    } else {
      logoError.value = "";
    }
  };

  const handleSubmit = veeHandleSubmit(async () => {
    // Validate logo manually
    validateLogo();

    if (
      !institutionName.value ||
      !description.value ||
      !logo.value ||
      !website.value ||
      !contactEmail.value ||
      !address.value ||
      !city.value ||
      !country.value
    ) {
      return;
    }

    onboardingStore.setInstitutionInfo({
      institutionName: institutionName.value,
      description: description.value,
      logo: logo.value,
      website: website.value,
      contactEmail: contactEmail.value,
      address: address.value,
      city: city.value,
      country: country.value,
    });

    isLoading.value = true;

    try {
      // Get personal info from onboarding store
      const personalInfo = onboardingStore.personalInfo;
      if (!personalInfo) {
        throw new Error("Personal info not found");
      }

      // Complete onboarding with both user profile and institution data
      await completeOnboarding({
        firstName: personalInfo.firstName,
        lastName: personalInfo.lastName,
        birthday: personalInfo.birthday,
        school: personalInfo.school,
        institutionData: {
          name: institutionName.value,
          slug: institutionName.value.toLowerCase().replace(/\s+/g, "-"),
          description: description.value || "",
          website: website.value || "",
          contactEmail: contactEmail.value,
          address: address.value || "",
          city: city.value || "",
          country: country.value || "",
        },
      });
    } catch (error) {
      // Error handling is done in the composable
      console.error("Onboarding completion error:", error);
    } finally {
      isLoading.value = false;
    }
  });

  const handleBack = () => {
    router.push(AUTH_ROUTES.REGISTER_PERSONAL_INFO);
  };
</script>

<template>
  <div class="w-full max-w-md mx-auto relative px-4 sm:px-0">
    <!-- Main Content - No card wrapper -->
    <div class="space-y-4 sm:space-y-5 lg:space-y-6">
      <!-- Header with Icon -->
      <div class="flex items-center gap-2 sm:gap-3">
        <div class="flex items-center justify-center bg-secondary-200 dark:bg-secondary-500 rounded-full p-3 sm:p-4">
          <Icon
            name="solar:buildings-2-linear"
            :size="20"
            class="sm:text-2xl text-secondary-600 dark:text-secondary-200"
          />
        </div>
        <h1 class="text-base sm:text-lg lg:text-xl font-bold dark:text-white leading-tight">
          {{ $t("auth.institutionInfoTitle") }}
        </h1>
      </div>

      <form class="space-y-4 sm:space-y-5 lg:space-y-6" @submit.prevent="handleSubmit">
        <!-- Institution Name Field -->
        <div>
          <label for="institutionName" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
            {{ $t("auth.institutionName") }}
          </label>
          <InputText
            id="institutionName"
            v-model="institutionName"
            type="text"
            :placeholder="$t('auth.institutionNamePlaceholder')"
            class="w-full"
            :invalid="!!institutionNameError"
            @blur="validateInstitutionName"
          />
          <Message v-if="institutionNameError" severity="error" :closable="false" size="small" class="mt-1 block">
            {{ institutionNameError }}
          </Message>
        </div>

        <!-- Description Field -->
        <div>
          <label for="description" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
            {{ $t("auth.description") }}
          </label>
          <Textarea
            id="description"
            v-model="description"
            :placeholder="$t('auth.descriptionPlaceholder')"
            rows="3"
            class="w-full"
            :invalid="!!descriptionError"
            @blur="validateDescription"
          />
          <Message v-if="descriptionError" severity="error" :closable="false" size="small" class="mt-1 block">
            {{ descriptionError }}
          </Message>
        </div>

        <!-- Institution Logo Upload -->
        <div>
          <label for="logo" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
            {{ $t("auth.institutionLogo") }}
          </label>

          <!-- Preview and Upload Area -->
          <div v-if="logoPreview" class="space-y-3">
            <!-- Image Preview -->
            <div class="flex items-center gap-4 p-4 border border-gray-300 dark:border-surface-600 rounded-xl">
              <img :src="logoPreview" alt="Logo preview" class="w-20 h-20 object-cover rounded-lg" />
              <div class="flex-1">
                <p class="text-sm font-medium text-surface-700 dark:text-surface-300">{{ logo?.name }}</p>
                <p class="text-xs text-gray-500 dark:text-surface-400">{{ (logo!.size / 1024).toFixed(2) }} KB</p>
              </div>
              <label
                for="logo"
                class="px-4 py-2 text-sm font-medium text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 cursor-pointer"
              >
                {{ $t("auth.changeLogo") }}
              </label>
            </div>
            <input id="logo" type="file" accept="image/*" class="hidden" @change="handleFileUpload" />
          </div>

          <!-- Upload Area (shown when no preview) -->
          <label
            v-else
            for="logo"
            :class="[
              'w-full border-2 border-dashed rounded-xl p-8 text-center hover:border-purple-400 dark:hover:border-purple-500 transition-colors cursor-pointer flex flex-col items-center gap-2',
              logoError ? 'border-red-500 dark:border-red-400' : 'border-gray-300 dark:border-surface-600',
            ]"
            @click="validateLogo"
          >
            <input id="logo" type="file" accept="image/*" class="hidden" @change="handleFileUpload" />
            <Icon name="solar:upload-linear" size="32" class="text-gray-400 dark:text-surface-500" />
            <span class="text-sm text-gray-600 dark:text-surface-400">
              {{ $t("auth.uploadLogo") }}
            </span>
          </label>

          <Message v-if="logoError" severity="error" :closable="false" size="small" class="mt-1 block">
            {{ logoError }}
          </Message>
        </div>

        <!-- Website and Contact Email (Grid 2 columns) -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
          <!-- Website -->
          <div>
            <label for="website" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
              {{ $t("auth.website") }}
            </label>
            <InputText
              id="website"
              v-model="website"
              type="url"
              :placeholder="$t('auth.websitePlaceholder')"
              class="w-full"
              :invalid="!!websiteError"
              @blur="validateWebsite"
            />
            <Message v-if="websiteError" severity="error" :closable="false" size="small" class="mt-1 block">
              {{ websiteError }}
            </Message>
          </div>

          <!-- Contact Email -->
          <div>
            <label for="contactEmail" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
              {{ $t("auth.contactEmail") }}
            </label>
            <InputText
              id="contactEmail"
              v-model="contactEmail"
              type="email"
              :placeholder="$t('auth.contactEmailPlaceholder')"
              class="w-full"
              :invalid="!!contactEmailError"
              @blur="validateContactEmail"
            />
            <Message v-if="contactEmailError" severity="error" :closable="false" size="small" class="mt-1 block">
              {{ contactEmailError }}
            </Message>
          </div>
        </div>

        <!-- Address Field -->
        <div>
          <label for="address" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
            {{ $t("auth.address") }}
          </label>
          <InputText
            id="address"
            v-model="address"
            type="text"
            :placeholder="$t('auth.addressPlaceholder')"
            class="w-full"
            :invalid="!!addressError"
            @blur="validateAddress"
          />
          <Message v-if="addressError" severity="error" :closable="false" size="small" class="mt-1 block">
            {{ addressError }}
          </Message>
        </div>

        <!-- City and Country (Grid 2 columns) -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
          <!-- City -->
          <div>
            <label for="city" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
              {{ $t("auth.city") }}
            </label>
            <InputText
              id="city"
              v-model="city"
              type="text"
              :placeholder="$t('auth.cityPlaceholder')"
              class="w-full"
              :invalid="!!cityError"
              @blur="validateCity"
            />
            <Message v-if="cityError" severity="error" :closable="false" size="small" class="mt-1 block">
              {{ cityError }}
            </Message>
          </div>

          <!-- Country -->
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
        </div>

        <!-- Action Buttons -->
        <div class="flex justify-between items-center pt-2 sm:pt-3 lg:pt-4">
          <Button text severity="secondary" :label="$t('auth.back')" class="text-sm sm:text-base" @click="handleBack">
            <template #icon>
              <Icon name="solar:arrow-left-linear" :size="18" class="sm:text-xl" />
            </template>
          </Button>
          <Button type="submit" :label="$t('auth.finish')" severity="help" :loading="isLoading" />
        </div>
      </form>
    </div>
  </div>
</template>
