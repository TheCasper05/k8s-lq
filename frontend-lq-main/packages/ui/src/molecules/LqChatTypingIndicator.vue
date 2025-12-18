<script setup lang="ts">
  import Avatar from "primevue/avatar";

  interface Props {
    botAvatarSrc?: string;
    botName?: string;
  }

  withDefaults(defineProps<Props>(), {
    botAvatarSrc: undefined,
    botName: "Bot",
  });

  const typingDots = [{ delay: "-0.3s" }, { delay: "-0.15s" }, { delay: "0s" }];
</script>

<template>
  <div class="flex gap-3">
    <Avatar
      :image="botAvatarSrc"
      :aria-label="botName"
      shape="square"
      class="!w-8 !h-8 !rounded-xl flex-shrink-0 shadow-sm overflow-hidden"
    >
      <template v-if="botAvatarSrc" #default>
        <img :src="botAvatarSrc" :alt="botName" class="w-full h-full object-cover scale-x-[-1]" />
      </template>
    </Avatar>
    <div class="bg-white dark:bg-surface-800 p-3 rounded-2xl rounded-tl-none shadow-sm flex items-center gap-1">
      <span
        v-for="(dot, index) in typingDots"
        :key="index"
        class="w-2 h-2 bg-surface-400 rounded-full animate-bounce"
        :style="{ animationDelay: dot.delay }"
      />
    </div>
  </div>
</template>
