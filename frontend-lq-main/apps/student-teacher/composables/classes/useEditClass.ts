import { ref } from "vue";
import { SUPPORTED_LOCALES } from "@lq/i18n/config";
import type { Class } from "./types";

/**
 * Generate a random invitation code (8 characters alphanumeric)
 */
const generateInvitationCode = (): string => {
  const characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  let code = "";
  for (let i = 0; i < 8; i++) {
    code += characters.charAt(Math.floor(Math.random() * characters.length));
  }
  return code;
};

/**
 * Composable for managing the "Edit Class" modal
 */
export const useEditClass = () => {
  const showModal = ref(false);
  const showAddTeacher = ref(false);
  const showAddStudents = ref(false);
  const addStudentsMethod = ref<"invitation-code" | "search" | null>(null);
  const teacherEmail = ref("");
  const classData = ref<Class | null>(null);
  const invitationCode = ref(generateInvitationCode());

  const openModal = (classItem?: Class) => {
    showModal.value = true;
    showAddTeacher.value = false;
    showAddStudents.value = false;
    addStudentsMethod.value = null;
    teacherEmail.value = "";
    if (classItem) {
      classData.value = { ...classItem };
    }
  };

  const closeModal = (clearData = true) => {
    showModal.value = false;
    showAddTeacher.value = false;
    showAddStudents.value = false;
    addStudentsMethod.value = null;
    teacherEmail.value = "";
    if (clearData) {
      classData.value = null;
    }
  };

  const toggleAddTeacher = () => {
    showAddTeacher.value = !showAddTeacher.value;
    if (showAddTeacher.value) {
      showAddStudents.value = false;
    }
  };

  const toggleAddStudents = () => {
    showAddStudents.value = !showAddStudents.value;
    if (showAddStudents.value) {
      showAddTeacher.value = false;
    } else {
      addStudentsMethod.value = null;
    }
  };

  const setAddStudentsMethod = (method: "invitation-code" | "search" | null) => {
    addStudentsMethod.value = method;
  };

  const closeAddStudents = () => {
    showAddStudents.value = false;
    addStudentsMethod.value = null;
  };

  const regenerateInvitationCode = () => {
    invitationCode.value = generateInvitationCode();
  };

  const cancelAddTeacher = () => {
    teacherEmail.value = "";
    showAddTeacher.value = false;
  };

  const addTeacher = (_email: string) => {
    // This will be handled by the component that uses this composable
    // The actual logic is in useClassTeachers
    teacherEmail.value = "";
    showAddTeacher.value = false;
  };

  const saveChanges = (updatedData?: {
    name?: string;
    level?: string;
    description?: string;
    languageCode?: string;
    coverImage?: string | null;
  }): Class | null => {
    // Mock mode: Update classData locally
    if (classData.value && updatedData) {
      // Get language name from code
      const languageName = updatedData.languageCode
        ? getLanguageNameFromCode(updatedData.languageCode)
        : classData.value.language;

      classData.value = {
        ...classData.value,
        name: updatedData.name ?? classData.value.name,
        level: updatedData.level ?? classData.value.level,
        description: updatedData.description ?? classData.value.description,
        languageCode: updatedData.languageCode ?? classData.value.languageCode,
        language: languageName ?? classData.value.language,
        coverImage: updatedData.coverImage ?? classData.value.coverImage,
        updatedAt: new Date().toISOString(),
      };
    }
    // TODO: Implement actual save logic when backend is ready
    // In real implementation, this would call a GraphQL mutation
    // Don't clear classData here - let the parent component handle it after save-complete
    closeModal(false);
    return classData.value;
  };

  // Helper function to get language name from code
  const getLanguageNameFromCode = (code: string): string => {
    // First try to find in SUPPORTED_LOCALES
    const locale = SUPPORTED_LOCALES.find((l) => l.code === code.toLowerCase());
    if (locale) {
      return locale.name;
    }

    // Fallback mapping for codes that might be used in mock data (e.g., "us" for English)
    const languageMap: Record<string, string> = {
      us: "English",
      en: "English",
      es: "Español",
      fr: "Français",
      de: "Deutsch",
      it: "Italiano",
      pt: "Português",
      jp: "Japanese",
      cn: "中文",
      ru: "Russian",
      ar: "العربية",
    };
    return languageMap[code.toLowerCase()] || code;
  };

  return {
    showModal,
    showAddTeacher,
    showAddStudents,
    addStudentsMethod,
    teacherEmail,
    classData,
    invitationCode,
    openModal,
    closeModal,
    toggleAddTeacher,
    toggleAddStudents,
    setAddStudentsMethod,
    closeAddStudents,
    cancelAddTeacher,
    addTeacher,
    saveChanges,
    regenerateInvitationCode,
  };
};
