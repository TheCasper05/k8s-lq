import { ref, watch } from "vue";
import { useAuthStore } from "@lq/stores";
import { useAppToast } from "./useAppToast";

export interface LocalProfile {
  id: string;
  publicId: string;
  primaryRole: string;
  firstName: string;
  lastName: string;
  email: string;
  avatar?: string;
  phone: string;
  birthday: string | null;
  location: string;
  timezone: string;
  isActive: boolean;
  institution: string;
  memberSince: string;
  nativeLanguage: string;
  learningLanguages: string[];
  bio: string;
  grade: string;
  classrooms: string[];
  twoFactorEnabled: boolean;
}

/**
 * Composable for managing profile editing state and operations
 */
export const useProfileEditor = () => {
  const authStore = useAuthStore();
  const toast = useAppToast();

  const isEditing = ref(false);
  const showPasswordModal = ref(false);

  /**
   * Creates a local profile object from authStore data
   */
  const createLocalProfile = (): LocalProfile => {
    const userAuth = authStore.userAuth;
    const userProfile = authStore.userProfile;
    const userProfileComplete = authStore.userProfileComplete;

    return {
      id: userAuth?.id || userProfileComplete?.id || "",
      publicId: userProfileComplete?.publicId || "",
      primaryRole: userProfileComplete?.primaryRole || userProfile?.primaryRole || "",
      firstName: userProfileComplete?.firstName || userProfile?.firstName || "",
      lastName: userProfileComplete?.lastName || userProfile?.lastName || "",
      email: userAuth?.email || userProfileComplete?.user?.email || "",
      avatar: userProfile?.photo || userProfileComplete?.photo || undefined,
      phone: userProfileComplete?.phone || "",
      birthday: userProfileComplete?.birthday || null,
      location: userProfileComplete?.country || "",
      timezone: userProfileComplete?.timezone || "",
      isActive: userProfileComplete?.isActive ?? true,
      institution: "",
      memberSince: new Date().toISOString(),
      nativeLanguage: "en", // TODO: Get from user preferences or browser locale
      learningLanguages: userProfileComplete?.languagePreference ? [userProfileComplete.languagePreference] : [],
      bio: "",
      grade: "",
      classrooms: [] as string[],
      twoFactorEnabled: false,
    };
  };

  const localProfile = ref<LocalProfile>(createLocalProfile());

  // Watch for changes in authStore to update localProfile
  watch(
    () => [authStore.userAuth, authStore.userProfile, authStore.userProfileComplete],
    () => {
      if (!isEditing.value) {
        localProfile.value = createLocalProfile();
      }
    },
    { deep: true },
  );

  /**
   * Start editing mode
   */
  const startEditing = () => {
    localProfile.value = createLocalProfile(); // Reset local changes
    isEditing.value = true;
  };

  /**
   * Cancel editing and revert changes
   */
  const cancelEditing = () => {
    localProfile.value = createLocalProfile(); // Revert changes
    isEditing.value = false;
  };

  /**
   * Save profile changes to authStore
   */
  const saveProfile = () => {
    if (authStore.userProfileComplete) {
      authStore.setUserProfileComplete({
        ...authStore.userProfileComplete,
        firstName: localProfile.value.firstName,
        lastName: localProfile.value.lastName,
        phone: localProfile.value.phone || null,
        birthday: localProfile.value.birthday,
        country: localProfile.value.location || null,
        timezone: localProfile.value.timezone,
        // languagePreference is the language to learn/teach, not native language
        languagePreference: localProfile.value.learningLanguages[0] || "en",
      });
    }

    isEditing.value = false;

    toast.profile.updated();
  };

  /**
   * Update local profile with partial data
   */
  const updateLocalProfile = (updates: Partial<LocalProfile>) => {
    localProfile.value = { ...localProfile.value, ...updates };
  };

  /**
   * Open password change modal
   */
  const openPasswordModal = () => {
    showPasswordModal.value = true;
  };

  /**
   * Handle password change submission
   */
  const handlePasswordChange = (data: { currentPassword: string; newPassword: string }) => {
    // TODO: Implement password change logic
    console.warn("Password change submitted:", data);
    toast.auth.passwordUpdated();
  };

  return {
    // State
    localProfile,
    isEditing,
    showPasswordModal,

    // Actions
    startEditing,
    cancelEditing,
    saveProfile,
    updateLocalProfile,
    openPasswordModal,
    handlePasswordChange,
  };
};
