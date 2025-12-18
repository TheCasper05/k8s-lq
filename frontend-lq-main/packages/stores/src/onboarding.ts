import { defineStore } from "pinia";
import { ref, computed } from "vue";

import type { LanguagePreferences, PersonalInfo, InstitutionInfo } from "./types";
import { FlowType, AccountType, type RegisterFormData, AUTH_ROUTES, ROLE_DASHBOARD_ROUTES } from "@lq/types";

export interface OnboardingState {
  flowType: FlowType;
  accountType: AccountType | null;
  registrationData: RegisterFormData | null;
  languagePreferences: LanguagePreferences | null;
  personalInfo: PersonalInfo | null;
  institutionInfo: InstitutionInfo | null;
  emailVerificationRequired: boolean;
}

/**
 * Onboarding store
 * Manages registration and onboarding flow state
 */
export const useOnboardingStore = defineStore("onboarding", () => {
  const flowType = ref<FlowType>(FlowType.REGISTER);
  const accountType = ref<AccountType | null>(null);
  const registrationData = ref<RegisterFormData | null>(null);
  const languagePreferences = ref<LanguagePreferences | null>(null);
  const personalInfo = ref<PersonalInfo | null>(null);
  const institutionInfo = ref<InstitutionInfo | null>(null);
  const emailVerificationRequired = ref<boolean>(false);

  const isInvitationFlow = computed(() => flowType.value === FlowType.INVITATION);

  const needsLanguagePreferences = computed(() => {
    return (
      accountType.value === AccountType.STUDENT || accountType.value === AccountType.TEACHER || isInvitationFlow.value
    );
  });

  const needsInstitutionInfo = computed(() => accountType.value === AccountType.ADMIN_INSTITUCIONAL);

  function setFlowType(type: FlowType) {
    flowType.value = type;
  }

  function setAccountType(type: AccountType) {
    accountType.value = type;
  }

  function setRegistrationData(data: RegisterFormData) {
    registrationData.value = data;
  }

  function setLanguagePreferences(data: LanguagePreferences) {
    languagePreferences.value = data;
  }

  function setPersonalInfo(data: PersonalInfo) {
    personalInfo.value = data;
  }

  function setInstitutionInfo(data: InstitutionInfo) {
    institutionInfo.value = data;
  }

  function setEmailVerificationRequired(required: boolean) {
    emailVerificationRequired.value = required;
  }

  function getNextStep(): string {
    // For invitation flow, skip account type selection
    if (isInvitationFlow.value) {
      if (needsLanguagePreferences.value && !languagePreferences.value) {
        return AUTH_ROUTES.REGISTER_LANGUAGE_PREFS;
      }
      if (!personalInfo.value) {
        return AUTH_ROUTES.REGISTER_PERSONAL_INFO;
      }
      if (needsInstitutionInfo.value && !institutionInfo.value) {
        return AUTH_ROUTES.REGISTER_INSTITUTION_INFO;
      }
      // Return dashboard based on account type if available
      return accountType.value ? ROLE_DASHBOARD_ROUTES[accountType.value] : "/dashboard";
    }

    // Regular flow
    if (!accountType.value) {
      return AUTH_ROUTES.REGISTER_ACCOUNT_TYPE;
    }

    if (needsLanguagePreferences.value && !languagePreferences.value) {
      return AUTH_ROUTES.REGISTER_LANGUAGE_PREFS;
    }

    if (!personalInfo.value) {
      return AUTH_ROUTES.REGISTER_PERSONAL_INFO;
    }

    if (needsInstitutionInfo.value && !institutionInfo.value) {
      return AUTH_ROUTES.REGISTER_INSTITUTION_INFO;
    }

    // Return dashboard based on account type
    return accountType.value ? ROLE_DASHBOARD_ROUTES[accountType.value] : "/dashboard";
  }

  function getPreviousStep(currentPath: string): string {
    // Determine previous step based on current path and flow type
    if (currentPath === AUTH_ROUTES.REGISTER_ACCOUNT_TYPE) {
      return flowType.value === FlowType.LOGIN ? AUTH_ROUTES.LOGIN : AUTH_ROUTES.REGISTER;
    }

    if (currentPath === AUTH_ROUTES.REGISTER_LANGUAGE_PREFS) {
      // For invitation flow, go back to wherever they came from
      if (isInvitationFlow.value) {
        return AUTH_ROUTES.REGISTER;
      }
      return AUTH_ROUTES.REGISTER_ACCOUNT_TYPE;
    }

    if (currentPath === AUTH_ROUTES.REGISTER_PERSONAL_INFO) {
      // For invitation flow, check if they need language preferences
      if (isInvitationFlow.value && needsLanguagePreferences.value) {
        return AUTH_ROUTES.REGISTER_LANGUAGE_PREFS;
      }
      if (needsLanguagePreferences.value) {
        return AUTH_ROUTES.REGISTER_LANGUAGE_PREFS;
      }
      return AUTH_ROUTES.REGISTER_ACCOUNT_TYPE;
    }

    if (currentPath === AUTH_ROUTES.REGISTER_INSTITUTION_INFO) {
      return AUTH_ROUTES.REGISTER_PERSONAL_INFO;
    }

    return AUTH_ROUTES.REGISTER;
  }

  function clearOnboarding() {
    flowType.value = FlowType.REGISTER;
    accountType.value = null;
    registrationData.value = null;
    languagePreferences.value = null;
    personalInfo.value = null;
    institutionInfo.value = null;
    emailVerificationRequired.value = false;
  }

  return {
    flowType,
    accountType,
    registrationData,
    languagePreferences,
    personalInfo,
    institutionInfo,
    emailVerificationRequired,

    isInvitationFlow,
    needsLanguagePreferences,
    needsInstitutionInfo,

    setFlowType,
    setAccountType,
    setRegistrationData,
    setLanguagePreferences,
    setPersonalInfo,
    setInstitutionInfo,
    setEmailVerificationRequired,
    getNextStep,
    getPreviousStep,
    clearOnboarding,
  };
});
