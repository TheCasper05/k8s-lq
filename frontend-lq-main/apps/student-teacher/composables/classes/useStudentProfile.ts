import { ref } from "vue";
import type { Student } from "~/composables/students/types";

// Global state (singleton) for student profile modal
const showModal = ref(false);
const studentData = ref<Student | null>(null);

/**
 * Composable for managing the "Student Profile" modal
 * This is a global state composable (singleton pattern) to ensure
 * the modal and the trigger component share the same state
 */
export const useStudentProfile = () => {
  const openModal = (student?: Student) => {
    showModal.value = true;
    if (student) {
      studentData.value = { ...student };
    }
  };

  const closeModal = () => {
    showModal.value = false;
    studentData.value = null;
  };

  return {
    showModal,
    studentData,
    openModal,
    closeModal,
  };
};
