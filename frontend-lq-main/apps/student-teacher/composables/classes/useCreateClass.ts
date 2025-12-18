import { ref, computed } from "vue";
import type { Class } from "./types";

export interface CreateClassFormData {
  // Step 1: Class Info
  coverImage: File | null;
  coverImagePreview: string | null;
  name: string;
  level: string | null;
  language: string | null;
  languageCode: string | null;
  description: string;
  schedule: string;

  // Step 2: Teachers
  selectedTeachers: string[]; // Array of teacher IDs

  // Step 3: Students
  selectedStudents: string[]; // Array of student IDs
}

export interface CreateClassErrors {
  name?: string;
  level?: string;
  language?: string;
}

/**
 * Composable for managing the "Create Class" modal
 */
export const useCreateClass = () => {
  const showModal = ref(false);
  const activeStep = ref<"1" | "2" | "3">("1"); // "1": Class Info, "2": Teachers, "3": Students

  const formData = ref<CreateClassFormData>({
    coverImage: null,
    coverImagePreview: null,
    name: "",
    level: null,
    language: null,
    languageCode: null,
    description: "",
    schedule: "",
    selectedTeachers: [],
    selectedStudents: [],
  });

  const errors = ref<CreateClassErrors>({});
  const loading = ref(false);
  const error = ref<string | null>(null);

  const resetForm = () => {
    formData.value = {
      coverImage: null,
      coverImagePreview: null,
      name: "",
      level: null,
      language: null,
      languageCode: null,
      description: "",
      schedule: "",
      selectedTeachers: [],
      selectedStudents: [],
    };
    errors.value = {};
    error.value = null;
  };

  const openModal = () => {
    showModal.value = true;
    activeStep.value = "1";
    resetForm();
  };

  const closeModal = () => {
    showModal.value = false;
    activeStep.value = "1";
    resetForm();
  };

  const validateStep1 = (): boolean => {
    errors.value = {};
    let isValid = true;

    if (!formData.value.name.trim()) {
      errors.value.name = "classes.createModal.classNameRequired";
      isValid = false;
    }

    if (!formData.value.level) {
      errors.value.level = "classes.createModal.levelRequired";
      isValid = false;
    }

    if (!formData.value.language) {
      errors.value.language = "classes.createModal.languageRequired";
      isValid = false;
    }

    return isValid;
  };

  const validateStep2 = (): boolean => {
    // Step 2 is optional, no validation needed
    return true;
  };

  const validateStep3 = (): boolean => {
    // Step 3 is optional, no validation needed
    return true;
  };

  const canProceedToNextStep = computed(() => {
    if (activeStep.value === "1") {
      return validateStep1();
    }
    if (activeStep.value === "2") {
      return validateStep2();
    }
    return validateStep3();
  });

  const nextStep = () => {
    if (activeStep.value === "1" && !validateStep1()) {
      return;
    }
    if (activeStep.value === "2" && !validateStep2()) {
      return;
    }
    if (activeStep.value === "1") {
      activeStep.value = "2";
    } else if (activeStep.value === "2") {
      activeStep.value = "3";
    }
  };

  const previousStep = () => {
    if (activeStep.value === "2") {
      activeStep.value = "1";
    } else if (activeStep.value === "3") {
      activeStep.value = "2";
    }
  };

  const goToStep = (step: "1" | "2" | "3") => {
    // Validate before allowing navigation
    if (step === "2" && !validateStep1()) {
      return;
    }
    if (step === "3" && (!validateStep1() || !validateStep2())) {
      return;
    }
    activeStep.value = step;
  };

  const setCoverImage = (file: File | null) => {
    formData.value.coverImage = file;
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        formData.value.coverImagePreview = e.target?.result as string;
      };
      reader.readAsDataURL(file);
    } else {
      formData.value.coverImagePreview = null;
    }
  };

  const createClass = async (): Promise<{ success: true; class: Class } | { success: false; error: string }> => {
    // Validate all steps
    if (!validateStep1() || !validateStep2() || !validateStep3()) {
      return { success: false, error: "Please complete all required fields" };
    }

    // Set loading state and clear previous errors
    loading.value = true;
    error.value = null;

    try {
      // Simulate API call with delay (1-2 seconds)
      await new Promise((resolve) => setTimeout(resolve, 1500));

      // Simulate possibility of error (~10% chance for testing)
      const shouldFail = Math.random() < 0.1;
      if (shouldFail) {
        throw new Error("Failed to create class. Please try again.");
      }

      // Create Class object from formData
      const now = new Date().toISOString();
      const studentCount = formData.value.selectedStudents.length;

      const newClass: Class = {
        id: `class-${Date.now()}`,
        name: formData.value.name,
        level: formData.value.level || "A1",
        language: formData.value.language || "English",
        languageCode: formData.value.languageCode || "us",
        description: formData.value.description || null,
        schedule: formData.value.schedule || null,
        coverImage: formData.value.coverImagePreview || null,
        students: studentCount,
        avgProgress: 0,
        status: studentCount > 0 ? "active" : "no-students",
        ownerId: "owner1",
        ownerName: "Current User",
        ownerEmail: "user@example.com",
        createdAt: now,
        updatedAt: now,
      };

      loading.value = false;
      return { success: true, class: newClass };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "An unexpected error occurred";
      error.value = errorMessage;
      loading.value = false;
      return { success: false, error: errorMessage };
    }
  };

  return {
    showModal,
    activeStep,
    formData,
    errors,
    loading,
    error,
    canProceedToNextStep,
    openModal,
    closeModal,
    nextStep,
    previousStep,
    goToStep,
    setCoverImage,
    createClass,
    validateStep1,
    validateStep2,
    validateStep3,
  };
};
