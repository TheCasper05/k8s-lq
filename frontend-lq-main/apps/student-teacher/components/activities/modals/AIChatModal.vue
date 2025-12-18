<script setup lang="ts">
  import Dialog from "primevue/dialog";
  import Button from "primevue/button";
  import InputText from "primevue/inputtext";
  import type { ChatMessage } from "~/types/activities";

  interface Props {
    visible: boolean;
  }

  interface Emits {
    "update:visible": [value: boolean];
    "create": [];
  }

  const props = defineProps<Props>();
  const emit = defineEmits<Emits>();

  const { t } = useI18n();

  const messages = ref<ChatMessage[]>([]);
  const userInput = ref("");
  const isTyping = ref(false);

  const dialogVisible = computed({
    get: () => props.visible,
    set: (value) => emit("update:visible", value),
  });

  const suggestions = computed(() => t("teacher.scenarios.chatModal.suggestions"));

  const aiResponses = [
    "I'd be happy to help you create that activity! What CEFR level are your students?",
    "Great choice! I can help you design an engaging scenario. What specific skills do you want to focus on?",
    "That sounds interesting! Let me help you create a comprehensive activity for that topic.",
    "Perfect! I'll help you build that. Should we make it more conversational or task-based?",
  ];

  watch(
    () => props.visible,
    (newVal) => {
      if (newVal) {
        messages.value = [];
        userInput.value = "";
      }
    },
  );

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
  };

  const sendMessage = async () => {
    if (!userInput.value.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: userInput.value,
      timestamp: new Date(),
    };

    messages.value.push(userMessage);
    userInput.value = "";

    await nextTick();

    // Simulate AI response
    isTyping.value = true;
    await new Promise((resolve) => setTimeout(resolve, 1500));

    const aiMessage: ChatMessage = {
      id: (Date.now() + 1).toString(),
      role: "assistant",
      content: aiResponses[Math.floor(Math.random() * aiResponses.length)],
      timestamp: new Date(),
    };

    messages.value.push(aiMessage);
    isTyping.value = false;
  };

  const sendSuggestion = (suggestion: string) => {
    userInput.value = suggestion;
    sendMessage();
  };

  const createFromChat = () => {
    emit("create");
    emit("update:visible", false);
  };
</script>

<template>
  <Dialog v-model:visible="dialogVisible" modal dismissable-mask class="w-full max-w-4xl h-[80vh]">
    <template #header>
      <div class="flex items-center gap-3">
        <div
          class="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500 to-pink-500 flex items-center justify-center"
        >
          <Icon name="solar:stars-line-duotone" class="text-white text-xl" />
        </div>
        <div>
          <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-0">
            {{ t("teacher.scenarios.chatModal.title") }}
          </h3>
          <p class="text-sm text-surface-600 dark:text-surface-400">{{ t("teacher.scenarios.chatModal.subtitle") }}</p>
        </div>
      </div>
    </template>

    <div class="flex flex-col h-full">
      <!-- Messages -->
      <div class="flex-1 overflow-y-auto space-y-4 mb-4">
        <div
          v-for="message in messages"
          :key="message.id"
          class="flex"
          :class="[message.role === 'user' ? 'justify-end' : 'justify-start']"
        >
          <div
            class="max-w-[80%] rounded-lg px-4 py-3"
            :class="[
              message.role === 'user'
                ? 'bg-primary-600 text-white'
                : 'bg-surface-100 dark:bg-surface-800 text-surface-900 dark:text-surface-0',
            ]"
          >
            <p class="text-sm whitespace-pre-wrap">{{ message.content }}</p>
            <span class="text-xs opacity-70 mt-1 block">
              {{ formatTime(message.timestamp) }}
            </span>
          </div>
        </div>

        <!-- Typing Indicator -->
        <div v-if="isTyping" class="flex justify-start">
          <div class="bg-surface-100 dark:bg-surface-800 rounded-lg px-4 py-3">
            <div class="flex gap-1">
              <span class="w-2 h-2 bg-surface-400 rounded-full animate-bounce" style="animation-delay: 0ms" />
              <span class="w-2 h-2 bg-surface-400 rounded-full animate-bounce" style="animation-delay: 150ms" />
              <span class="w-2 h-2 bg-surface-400 rounded-full animate-bounce" style="animation-delay: 300ms" />
            </div>
          </div>
        </div>
      </div>

      <!-- Suggestions -->
      <div v-if="!messages.length" class="mb-4">
        <p class="text-sm font-medium text-surface-900 dark:text-surface-0 mb-2">
          {{ t("teacher.scenarios.chatModal.tryAsking") }}
        </p>
        <div class="flex flex-wrap gap-2">
          <Button
            v-for="suggestion in suggestions"
            :key="suggestion"
            :label="suggestion"
            size="small"
            outlined
            @click="sendSuggestion(suggestion)"
          />
        </div>
      </div>

      <!-- Input -->
      <div class="flex gap-2">
        <InputText
          v-model="userInput"
          :placeholder="t('teacher.scenarios.chatModal.placeholder')"
          class="flex-1"
          @keyup.enter="sendMessage"
        />
        <Button :disabled="!userInput.trim() || isTyping" @click="sendMessage">
          <template #icon>
            <Icon name="solar:plain-2-linear" />
          </template>
        </Button>
      </div>
    </div>

    <template #footer>
      <Button :label="t('teacher.scenarios.chatModal.create')" :disabled="messages.length < 2" @click="createFromChat">
        <template #icon>
          <Icon name="solar:add-circle-linear" />
        </template>
      </Button>
    </template>
  </Dialog>
</template>
