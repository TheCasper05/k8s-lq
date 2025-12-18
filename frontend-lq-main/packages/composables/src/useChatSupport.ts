import { ref } from "vue";

const isChatOpen = ref(false);

export const useChatSupport = () => {
  const toggleChat = () => {
    isChatOpen.value = !isChatOpen.value;
  };

  const openChat = () => {
    isChatOpen.value = true;
  };

  const closeChat = () => {
    isChatOpen.value = false;
  };

  return {
    isChatOpen,
    toggleChat,
    openChat,
    closeChat,
  };
};
