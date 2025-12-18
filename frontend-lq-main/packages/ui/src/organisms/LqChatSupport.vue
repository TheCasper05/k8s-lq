<script setup lang="ts">
  import { useChatSupport } from "@lq/composables";
  import { ref, nextTick, watch } from "vue";
  import LqChatHeader from "../molecules/LqChatHeader.vue";
  import LqChatMessage from "../molecules/LqChatMessage.vue";
  import LqChatQuickActions from "../molecules/LqChatQuickActions.vue";
  import LqChatTypingIndicator from "../molecules/LqChatTypingIndicator.vue";
  import LqChatInput from "../molecules/LqChatInput.vue";

  export interface ChatTranslations {
    title?: string;
    subtitle?: string;
    welcomeMessage?: string;
    placeholder?: string;
    disclaimer?: string;
    botResponseSimulated?: string;
    tooltips?: {
      refresh?: string;
      minimize?: string;
      close?: string;
    };
  }

  interface Props {
    logoSrc?: string;
    logoAlt?: string;
    botAvatarSrc?: string;
    botName?: string;
    userAvatarSrc?: string;
    quickActions?: string[];
    translations?: ChatTranslations;
  }

  const props = withDefaults(defineProps<Props>(), {
    logoSrc: undefined,
    logoAlt: "Logo",
    botAvatarSrc: undefined,
    botName: "Bot",
    userAvatarSrc: undefined,
    quickActions: () => [],
    translations: () => ({
      title: "Support",
      subtitle: "online",
      welcomeMessage: "Hi there! 👋 How can I help you today?",
      placeholder: "Type your question...",
      disclaimer: "AI can make mistakes. Check important info.",
      botResponseSimulated: "Thanks for your message! This is a simulated response for the mockup.",
      tooltips: {
        refresh: "Refresh chat",
        minimize: "Minimize chat",
        close: "Close chat",
      },
    }),
  });

  const { isChatOpen, openChat, closeChat } = useChatSupport();
  const isMinimized = ref(false);

  const handleMinimize = () => {
    isMinimized.value = true;
    closeChat();
  };

  const handleClose = () => {
    isMinimized.value = false;
    closeChat();
  };

  const handleOpenFromMinimized = () => {
    isMinimized.value = false;
    openChat();
  };

  interface Message {
    id: number;
    text: string;
    sender: "user" | "bot";
    timestamp: Date;
    type?: "text" | "guide"; // Expandable for different message types
  }

  const messages = ref<Message[]>([
    {
      id: 1,
      text: props.translations.welcomeMessage || "Hi there! 👋 How can I help you today?",
      sender: "bot",
      timestamp: new Date(),
    },
  ]);

  const inputValue = ref("");
  const messagesContainer = ref<HTMLElement | null>(null);
  const isTyping = ref(false);

  const scrollToBottom = async () => {
    await nextTick();
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  };

  const sendMessage = async () => {
    if (!inputValue.value.trim()) return;

    const text = inputValue.value;
    inputValue.value = "";

    // Add user message
    messages.value.push({
      id: Date.now(),
      text,
      sender: "user",
      timestamp: new Date(),
    });

    await scrollToBottom();

    // Simulate bot response
    isTyping.value = true;
    setTimeout(async () => {
      isTyping.value = false;
      messages.value.push({
        id: Date.now() + 1,
        text:
          props.translations.botResponseSimulated ||
          "Thanks for your message! This is a simulated response for the mockup.",
        sender: "bot",
        timestamp: new Date(),
      });
      await scrollToBottom();
    }, 1500);
  };

  const handleQuickAction = (action: string) => {
    inputValue.value = action;
    sendMessage();
  };

  // Watch for chat opening to scroll to bottom
  watch(isChatOpen, (newVal) => {
    if (newVal) {
      scrollToBottom();
    }
  });
</script>

<template>
  <Transition
    enter-active-class="transition-all duration-300 ease-out"
    enter-from-class="opacity-0 scale-95 translate-y-4"
    enter-to-class="opacity-100 scale-100 translate-y-0"
    leave-active-class="transition-all duration-200 ease-in"
    leave-from-class="opacity-100 scale-100 translate-y-0"
    leave-to-class="opacity-0 scale-95 translate-y-4"
  >
    <button
      v-if="!isChatOpen && isMinimized"
      class="fixed bottom-6 right-6 z-50 flex items-center justify-center rounded-xl bg-surface-100 dark:bg-surface-800 p-3 shadow-lg hover:bg-surface-200 dark:hover:bg-surface-700 transition-colors duration-300"
      @click="handleOpenFromMinimized"
    >
      <div class="relative w-8 h-8 flex-shrink-0 bg-primary-500 rounded-xl flex items-center justify-center text-white">
        <img v-if="logoSrc" :src="logoSrc" :alt="logoAlt" class="w-5 h-5 object-contain" />
        <span class="absolute -top-1 -right-1 flex h-3 w-3">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
          <span
            class="relative inline-flex rounded-full h-3 w-3 bg-green-500 border-2 border-surface-100 dark:border-surface-800"
          />
        </span>
      </div>
    </button>
  </Transition>

  <Transition
    enter-active-class="transition-all duration-300 ease-out"
    enter-from-class="opacity-0 scale-95 translate-y-4"
    enter-to-class="opacity-100 scale-100 translate-y-0"
    leave-active-class="transition-all duration-200 ease-in"
    leave-from-class="opacity-100 scale-100 translate-y-0"
    leave-to-class="opacity-0 scale-95 translate-y-4"
  >
    <div
      v-if="isChatOpen"
      class="fixed bottom-0 right-0 sm:bottom-6 sm:right-6 z-50 w-full h-full sm:h-auto sm:w-[400px] flex flex-col bg-surface-50 dark:bg-surface-900 shadow-xl overflow-hidden font-sans shadow-3xl origin-bottom-right rounded-t-2xl sm:rounded-2xl"
    >
      <!-- Header -->
      <LqChatHeader
        :logo-src="logoSrc"
        :logo-alt="logoAlt"
        :title="translations.title"
        :subtitle="translations.subtitle"
        is-online
        @refresh="() => {}"
        @minimize="handleMinimize"
        @close="handleClose"
      />

      <!-- Chat Area -->
      <div
        ref="messagesContainer"
        class="flex-1 bg-surface-50 dark:bg-surface-950 p-4 overflow-y-auto sm:max-h-[500px] sm:min-h-[400px] flex flex-col gap-4 [&::-webkit-scrollbar]:w-1 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-surface-200 dark:[&::-webkit-scrollbar-thumb]:bg-surface-700 [&::-webkit-scrollbar-thumb]:rounded-full"
      >
        <template v-for="(msg, index) in messages" :key="msg.id">
          <LqChatMessage
            :sender="msg.sender"
            :text="msg.text"
            :timestamp="msg.timestamp"
            :bot-avatar-src="botAvatarSrc"
            :bot-name="botName"
            :user-avatar-src="userAvatarSrc"
            :is-first-message="index === 0"
            :is-last-bot-message="msg.sender === 'bot' && index === messages.length - 1 && !isTyping"
          >
            <template v-if="index === 0" #guide-content>
              <slot name="guide-content" />
            </template>
            <template
              v-if="msg.sender === 'bot' && index === messages.length - 1 && !isTyping && quickActions.length > 0"
              #quick-actions
            >
              <LqChatQuickActions :actions="quickActions" @action="handleQuickAction">
                <template #secondary-actions>
                  <slot name="secondary-actions" />
                </template>
              </LqChatQuickActions>
            </template>
          </LqChatMessage>
        </template>

        <!-- Typing Indicator -->
        <LqChatTypingIndicator v-if="isTyping" :bot-avatar-src="botAvatarSrc" :bot-name="botName" />
      </div>

      <!-- Input Area -->
      <LqChatInput
        v-model="inputValue"
        :placeholder="translations.placeholder"
        :disclaimer="translations.disclaimer"
        @send="sendMessage"
        @attach="() => {}"
      />
    </div>
  </Transition>
</template>
