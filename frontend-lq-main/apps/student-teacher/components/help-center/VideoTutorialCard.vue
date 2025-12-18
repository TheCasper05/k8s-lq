<script setup lang="ts">
  import type { VideoTutorial } from "~/composables/help-center/useHelpCenterData";

  interface Props {
    video: VideoTutorial;
  }

  const props = defineProps<Props>();

  const emit = defineEmits<{
    click: [videoId: string];
  }>();

  const handleClick = () => {
    emit("click", props.video.id);
  };
</script>

<template>
  <div
    class="video-tutorial-card flex items-center gap-4 p-4 rounded-lg bg-surface-50 dark:bg-surface-800/50 hover:bg-surface-100 dark:hover:bg-surface-800 cursor-pointer transition-colors duration-200"
    role="button"
    tabindex="0"
    :aria-label="video.title"
    @click="handleClick"
    @keydown.enter="handleClick"
    @keydown.space.prevent="handleClick"
  >
    <!-- Thumbnail -->
    <div class="flex-shrink-0 relative w-32 h-20 rounded-lg bg-surface-900 dark:bg-surface-800 overflow-hidden">
      <!-- Play Icon (centered) -->
      <div class="absolute inset-0 flex items-center justify-center">
        <div
          class="w-12 h-12 rounded-full bg-primary-600/90 flex items-center justify-center hover:bg-primary-700/90 transition-colors"
        >
          <Icon name="solar:play-circle-bold" class="text-2xl text-white ml-0.5" aria-hidden="true" />
        </div>
      </div>

      <!-- Duration (bottom-right) -->
      <div
        class="absolute bottom-2 right-2 px-2 py-1 rounded bg-black/70 backdrop-blur-sm text-white text-xs font-medium"
      >
        {{ video.duration }}
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 min-w-0">
      <!-- Title -->
      <h4 class="text-base font-bold text-surface-900 dark:text-surface-50 mb-2 line-clamp-1">
        {{ video.title }}
      </h4>

      <!-- Description -->
      <p class="text-sm text-surface-600 dark:text-surface-400 line-clamp-2">
        {{ video.description }}
      </p>
    </div>
  </div>
</template>
