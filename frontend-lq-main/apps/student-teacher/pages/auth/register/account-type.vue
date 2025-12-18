<script setup lang="ts">
  import { useOnboardingStore } from "@lq/stores";
  import { AccountType, AUTH_ROUTES } from "@lq/types";
  import AccountTypeCard from "~/components/AccountTypeCard.vue";
  import lqPersonWithGlasses from "~/assets/images/lq-person-with-glasses.png";

  const { t: $t } = useI18n();

  definePageMeta({
    layout: "auth",
  });

  const router = useRouter();
  const onboardingStore = useOnboardingStore();

  const selectedAccountType = ref<AccountType | null>(onboardingStore.accountType || null);

  const accountTypes = computed(() => [
    {
      value: AccountType.TEACHER,
      label: $t("auth.accountTypeTeacher"),
      icon: "solar:square-academic-cap-outline",
    },
    {
      value: AccountType.STUDENT,
      label: $t("auth.accountTypeStudent"),
      icon: "solar:notebook-minimalistic-linear",
    },
    {
      value: AccountType.ADMIN_INSTITUCIONAL,
      label: $t("auth.accountTypeInstitution"),
      icon: "solar:user-rounded-linear",
    },
  ]);

  const handleSelectAccountType = (value: AccountType) => {
    selectedAccountType.value = value;
  };

  const _handleContinue = () => {
    if (!selectedAccountType.value) {
      return;
    }

    // Store account type in onboarding store
    onboardingStore.setAccountType(selectedAccountType.value);

    // Navigate based on account type
    if (selectedAccountType.value === AccountType.STUDENT || selectedAccountType.value === AccountType.TEACHER) {
      router.push(AUTH_ROUTES.REGISTER_LANGUAGE_PREFS);
    } else if (selectedAccountType.value === AccountType.ADMIN_INSTITUCIONAL) {
      router.push(AUTH_ROUTES.REGISTER_PERSONAL_INFO);
    }
  };

  const handleBack = () => {
    // Determine where to go back based on flow type
    const previousStep = onboardingStore.getPreviousStep(AUTH_ROUTES.REGISTER_ACCOUNT_TYPE);
    router.push(previousStep);
  };
</script>

<template>
  <div class="w-full max-w-md mx-auto relative px-4 sm:px-0">
    <!-- Main Content - No card wrapper, direct content -->
    <div class="flex flex-col space-y-3 sm:space-y-4 lg:space-y-6">
      <!-- Header with Icon -->
      <div class="flex items-center w-full gap-2 sm:gap-3">
        <Avatar
          unstyled
          pt:root="size-14 sm:size-16 lg:size-20 rounded-full flex items-center justify-center"
          :image="lqPersonWithGlasses"
          shape="circle"
          size="large"
        />
        <h1 class="text-base sm:text-lg lg:text-xl font-bold dark:text-white leading-tight">
          {{ $t("auth.accountTypeTitle") }}
        </h1>
      </div>

      <!-- Account Type Options -->
      <div class="space-y-2 sm:space-y-3">
        <AccountTypeCard
          v-for="type in accountTypes"
          :key="type.value"
          :icon="type.icon"
          :label="type.label"
          :value="type.value"
          :selected="selectedAccountType === type.value"
          @select="handleSelectAccountType"
        />
      </div>

      <!-- Action Buttons -->
      <div class="flex justify-between items-center pt-2 sm:pt-3 lg:pt-4">
        <Button text severity="secondary" :label="$t('auth.back')" class="text-sm sm:text-base" @click="handleBack">
          <template #icon>
            <Icon name="solar:arrow-left-linear" :size="18" class="sm:text-xl" />
          </template>
        </Button>
        <Button v-show="selectedAccountType" severity="help" :label="$t('auth.next')" @click="_handleContinue" />
      </div>
    </div>
  </div>
</template>
