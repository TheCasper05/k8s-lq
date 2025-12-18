import { ref } from "vue";

/**
 * Composable for managing the "Add Assignment" modal
 */
export const useAddAssignment = () => {
  const showModal = ref(false);
  const activeTab = ref<"modules" | "scenarios">("modules");
  const selectedItems = ref<string[]>([]); // Array of module/scenario IDs

  const openModal = () => {
    showModal.value = true;
    activeTab.value = "modules";
    selectedItems.value = [];
  };

  const closeModal = () => {
    showModal.value = false;
    activeTab.value = "modules";
    selectedItems.value = [];
  };

  const setActiveTab = (tab: "modules" | "scenarios") => {
    activeTab.value = tab;
  };

  const toggleItemSelection = (itemId: string, type: "module" | "scenario") => {
    const prefixedId = `${type}-${itemId}`;
    const index = selectedItems.value.indexOf(prefixedId);
    if (index > -1) {
      selectedItems.value.splice(index, 1);
    } else {
      selectedItems.value.push(prefixedId);
    }
  };

  const isItemSelected = (itemId: string, type: "module" | "scenario") => {
    const prefixedId = `${type}-${itemId}`;
    return selectedItems.value.includes(prefixedId);
  };

  const createAssignments = () => {
    // TODO: Implement actual create logic when backend is ready
    closeModal();
  };

  return {
    showModal,
    activeTab,
    selectedItems,
    openModal,
    closeModal,
    setActiveTab,
    toggleItemSelection,
    isItemSelected,
    createAssignments,
  };
};
