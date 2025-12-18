import { ref } from "vue";

/**
 * Composable for managing the "Add Students" modal
 */
export const useAddStudents = () => {
  const showModal = ref(false);
  const activeTab = ref(0); // 0: Invitation Code, 1: Search Students
  const invitationCode = ref("");
  const selectedStudents = ref<string[]>([]); // Array of student IDs

  const openModal = () => {
    showModal.value = true;
    activeTab.value = 0;
    invitationCode.value = "";
    selectedStudents.value = [];
  };

  const closeModal = () => {
    showModal.value = false;
    invitationCode.value = "";
    selectedStudents.value = [];
  };

  const toggleStudentSelection = (studentId: string) => {
    const index = selectedStudents.value.indexOf(studentId);
    if (index > -1) {
      selectedStudents.value.splice(index, 1);
    } else {
      selectedStudents.value.push(studentId);
    }
  };

  const isStudentSelected = (studentId: string) => {
    return selectedStudents.value.includes(studentId);
  };

  const addStudents = () => {
    // TODO: Implement actual add logic when backend is ready
    closeModal();
  };

  return {
    showModal,
    activeTab,
    invitationCode,
    selectedStudents,
    openModal,
    closeModal,
    toggleStudentSelection,
    isStudentSelected,
    addStudents,
  };
};
