import { ref } from "vue";
import { loadClassesFromStorage, saveClassesToStorage } from "./useClasses";

/**
 * Composable for managing the "Add Class Students" modal
 */
export const useAddClassStudents = () => {
  const showModal = ref(false);
  const activeTab = ref(0); // 0: Invitation Code, 1: Search Students
  const invitationCode = ref("");
  const inviteLink = ref("");
  const selectedStudents = ref<string[]>([]); // Array of student IDs
  const searchQuery = ref("");
  const currentClassId = ref<string | null>(null);

  const openModal = (classId?: string) => {
    showModal.value = true;
    activeTab.value = 0;
    invitationCode.value = "";
    selectedStudents.value = [];
    searchQuery.value = "";
    currentClassId.value = classId || null;
    // TODO: Fetch invite link from API when backend is ready
    if (classId) {
      inviteLink.value = `https://app-es.lingquest.com/invite/ABC123XYZ`;
    }
  };

  const closeModal = () => {
    showModal.value = false;
    activeTab.value = 0;
    invitationCode.value = "";
    selectedStudents.value = [];
    searchQuery.value = "";
    inviteLink.value = "";
    currentClassId.value = null;
  };

  const setActiveTab = (tab: number) => {
    activeTab.value = tab;
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
    if (!currentClassId.value || selectedStudents.value.length === 0) {
      closeModal();
      return;
    }

    try {
      const storedClasses = loadClassesFromStorage();
      const classItem = storedClasses?.find((c) => c.id === currentClassId.value);

      if (classItem) {
        const currentStudentIds = classItem.studentIds || [];
        // Add only new students (avoid duplicates)
        const newStudentIds = selectedStudents.value.filter((id) => !currentStudentIds.includes(id));
        const updatedStudentIds = [...currentStudentIds, ...newStudentIds];
        const updatedClass = {
          ...classItem,
          studentIds: updatedStudentIds,
          students: updatedStudentIds.length,
          updatedAt: new Date().toISOString(),
        };

        // Update in storage
        if (storedClasses) {
          const updatedClasses = storedClasses.map((c) => (c.id === currentClassId.value ? updatedClass : c));
          saveClassesToStorage(updatedClasses);
        }
      }
    } catch (err) {
      // Error handling: silently fail or implement proper error notification
      console.error("Error adding students to class:", err);
    }

    closeModal();
  };

  return {
    showModal,
    activeTab,
    invitationCode,
    inviteLink,
    selectedStudents,
    searchQuery,
    openModal,
    closeModal,
    setActiveTab,
    toggleStudentSelection,
    isStudentSelected,
    addStudents,
  };
};
