import { useAuthStore, useOnboardingStore } from "@lq/stores";
import { useMutation, CREATE_USER_PROFILE, CREATE_INSTITUTION, provideApolloClient } from "@lq/graphql";
import { AccountType } from "@lq/types";
import { useToast } from "primevue/usetoast";
import type { ApolloClient, NormalizedCacheObject } from "@apollo/client/core";

export interface CompleteOnboardingOptions {
  /** First name of the user */
  firstName: string;
  /** Last name of the user */
  lastName: string;
  /** Birthday as a Date object or null */
  birthday: Date | null;
  /** Optional school name (for students/teachers) */
  school?: string;
  /** Optional institution data (only for INSTITUTIONAL account type) */
  institutionData?: {
    name: string;
    slug: string;
    description: string;
    website: string;
    contactEmail: string;
    address: string;
    city: string;
    country: string;
  };
}

/**
 * Composable to complete the onboarding process for all account types
 *
 * This composable centralizes the logic for:
 * - Creating the user profile (CREATE_USER_PROFILE)
 * - Creating the institution (CREATE_INSTITUTION) if account type is INSTITUTIONAL
 * - Clearing the onboarding store
 * - Showing success/error toasts
 * - Navigating to the dashboard
 *
 * @returns {Function} completeOnboarding - Function to complete the onboarding process
 */
export const useCompleteOnboarding = () => {
  const authStore = useAuthStore();
  const onboardingStore = useOnboardingStore();
  const toast = useToast();
  const { t: $t } = useI18n(); // Auto-imported in Nuxt
  const { $apollo } = useNuxtApp();

  // Provide Apollo Client context to ensure mutations work
  provideApolloClient($apollo as ApolloClient<NormalizedCacheObject>);

  const { mutate: createUserProfileMutation } = useMutation(CREATE_USER_PROFILE);
  const { mutate: createInstitutionMutation } = useMutation(CREATE_INSTITUTION);

  // Call useAuthNavigation at the top level, not inside async function
  const { redirectToRoleDashboard } = useAuthNavigation();

  /**
   * Completes the onboarding process by creating user profile and optionally institution
   */
  const completeOnboarding = async (options: CompleteOnboardingOptions) => {
    const { firstName, lastName, birthday, institutionData } = options;

    // Save account type before clearing onboarding store
    const accountType = onboardingStore.accountType;
    const isInstitutional = accountType === AccountType.ADMIN_INSTITUCIONAL;

    try {
      const profileInput = [
        {
          user: authStore.userId,
          primaryRole: accountType,
          firstName,
          lastName,
          birthday: birthday ? birthday.toISOString().split("T")[0] : null,
          languagePreference: onboardingStore.languagePreferences?.nativeLanguage || "en",
          timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC",
        },
      ];

      const userProfileResult = await createUserProfileMutation({ input: profileInput });

      // Save complete user profile to auth store
      if (userProfileResult?.data?.createUserProfiles?.objects?.[0]) {
        const createdProfile = userProfileResult.data.createUserProfiles.objects[0];
        authStore.setUserProfileComplete(createdProfile);
      }

      if (isInstitutional && institutionData) {
        const institutionInput = [
          {
            name: institutionData.name,
            slug: institutionData.slug,
            description: institutionData.description,
            website: institutionData.website,
            contactEmail: institutionData.contactEmail,
            address: institutionData.address,
            city: institutionData.city,
            country: institutionData.country,
          },
        ];

        const institutionResult = await createInstitutionMutation({ input: institutionInput });

        // Save institution to auth store
        if (institutionResult?.data?.createInstitutions?.objects?.[0]) {
          const createdInstitution = institutionResult.data.createInstitutions.objects[0];
          authStore.setInstitution(createdInstitution);
        }
      }

      // Mark onboarding as completed for all account types
      authStore.markOnboardingCompleted();

      onboardingStore.clearOnboarding();

      // Redirect to role-specific dashboard
      await redirectToRoleDashboard();

      toast.add({
        severity: "success",
        summary: isInstitutional
          ? $t("auth.welcomeInstitution", { name: institutionData?.name || firstName })
          : $t("auth.welcomeToast"),
        detail: isInstitutional ? $t("auth.institutionSetupSuccess") : $t("auth.welcomeDetail", { name: firstName }),
        life: 5000,
      });

      return { success: true };
    } catch (error) {
      console.error("Onboarding completion error:", error);

      toast.add({
        severity: "error",
        summary: $t("common.error"),
        detail: error instanceof Error ? error.message : $t("auth.somethingWentWrong"),
        life: 5000,
      });

      throw error;
    }
  };

  return {
    completeOnboarding,
  };
};
