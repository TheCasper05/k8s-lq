import { ref } from "vue";
import type { Assignment } from "./types";

/**
 * Composable for managing the "Edit Assignment" modal
 */
export const useEditAssignment = () => {
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

  const saveChanges = () => {
    // TODO: Implement actual save logic when backend is ready
    closeModal();
  };

  return {
    showModal,
    assignmentData,
    openModal,
    closeModal,
    saveChanges,
  };
};
