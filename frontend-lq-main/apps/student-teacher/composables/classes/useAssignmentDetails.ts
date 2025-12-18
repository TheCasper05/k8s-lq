import { ref } from "vue";
import type { Assignment } from "./types";

/**
 * Composable for managing the "Assignment Details" modal
 */
export const useAssignmentDetails = () => {
  const showModal = ref(false);
  const assignmentData = ref<Assignment | null>(null);

  const openModal = (assignment?: Assignment) => {
    showModal.value = true;
    if (assignment) {
      assignmentData.value = { ...assignment };
    }
  };

  const closeModal = () => {
    showModal.value = false;
    assignmentData.value = null;
  };

  const viewPractice = () => {
    // TODO: Navigate to practice view
    closeModal();
  };

  return {
    showModal,
    assignmentData,
    openModal,
    closeModal,
    viewPractice,
  };
};
