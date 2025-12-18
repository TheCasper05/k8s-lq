<script setup lang="ts">
  import Avatar from "primevue/avatar";

  interface Props {
    sender: "user" | "bot";
    text: string;
    timestamp: Date;
    botAvatarSrc?: string;
    botName?: string;
    userAvatarSrc?: string;
    isFirstMessage?: boolean;
    isLastBotMessage?: boolean;
  }

  withDefaults(defineProps<Props>(), {
    botAvatarSrc: undefined,
    botName: "Bot",
    userAvatarSrc: undefined,
    isFirstMessage: false,
    isLastBotMessage: false,
  });

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };
</script>

<template>
  <!-- Bot Message -->
  <div v-if="sender === 'bot'" class="flex gap-3">
    <Avatar
      :image="botAvatarSrc"
      :aria-label="botName"
      shape="square"
      class="!w-8 !h-8 !rounded-xl !backdrop-blur-sm flex-shrink-0 overflow-hidden"
    >
      <template v-if="botAvatarSrc" #default>
        <img :src="botAvatarSrc" :alt="botName" class="w-full h-full object-cover scale-x-[-1]" />
      </template>
    </Avatar>
    <div class="flex flex-col gap-2 max-w-[85%]">
      <div
        class="bg-white dark:bg-surface-800 p-3 rounded-2xl rounded-tl-none shadow-sm text-sm text-surface-700 dark:text-surface-200"
      >
        {{ text }}
        <slot v-if="isFirstMessage" name="guide-content" />
      </div>
      <slot v-if="isLastBotMessage" name="quick-actions" />
      <span class="text-[10px] text-surface-400 pl-1">{{ formatTime(timestamp) }}</span>
    </div>
  </div>

  <!-- User Message -->
  <div v-else class="flex flex-col items-end gap-1">
    <div class="flex items-end gap-2 flex-row-reverse">
      <Avatar
        :image="userAvatarSrc"
        aria-label="User"
        shape="circle"
        class="size-10 dark:!bg-surface-700 overflow-hidden"
      >
        <template v-if="!userAvatarSrc" #default>
          <span class="text-xs font-medium text-surface-600 dark:text-surface-300">U</span>
        </template>
      </Avatar>
      <div class="bg-primary-500 text-white p-3 rounded-2xl rounded-tr-none shadow-sm text-sm">
        {{ text }}
      </div>
    </div>
    <span class="text-[10px] text-surface-400 pr-1">{{ formatTime(timestamp) }}</span>
  </div>
</template>
