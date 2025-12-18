import { ref } from "vue";

export const useActivityModals = () => {
  const quickCreateVisible = ref(false);
  const wizardVisible = ref(false);
  const editVisible = ref(false);
  const editAIVisible = ref(false);
  const assignVisible = ref(false);
  const aiChatVisible = ref(false);

  const openQuickCreate = () => {
    quickCreateVisible.value = true;
  };

  const openWizard = () => {
    quickCreateVisible.value = false;
    wizardVisible.value = true;
  };

  const openEdit = () => {
    editVisible.value = true;
  };

  const openEditAI = () => {
    editAIVisible.value = true;
  };

  const openAssign = () => {
    assignVisible.value = true;
  };

  const openAIChat = () => {
    aiChatVisible.value = true;
  };

  const closeAll = () => {
    quickCreateVisible.value = false;
    wizardVisible.value = false;
    editVisible.value = false;
    editAIVisible.value = false;
    assignVisible.value = false;
    aiChatVisible.value = false;
  };

  return {
    // State
    quickCreateVisible,
    wizardVisible,
    editVisible,
    editAIVisible,
    assignVisible,
    aiChatVisible,

    // Methods
    openQuickCreate,
    openWizard,
    openEdit,
    openEditAI,
    openAssign,
    openAIChat,
    closeAll,
  };
};
