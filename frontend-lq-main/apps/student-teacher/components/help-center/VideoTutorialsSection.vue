<script setup lang="ts">
  import { LqCard } from "@lq/ui";
  import type { VideoTutorial } from "~/composables/help-center/useHelpCenterData";
  import VideoTutorialCard from "./VideoTutorialCard.vue";

  interface Props {
    videos: VideoTutorial[];
  }

  defineProps<Props>();

  const handleVideoClick = (_videoId: string) => {
    // TODO: Open video player or navigate to video page
  };

  const handleViewAll = () => {
    // TODO: Navigate to all videos page
  };
</script>

<template>
  <LqCard>
    <template #header>
      <div class="flex items-center justify-between">
        <h3 class="text-xl font-bold text-surface-900 dark:text-surface-50">
          {{ $t("helpCenter.videoTutorials") }}
        </h3>
        <button
          class="flex items-center gap-2 px-4 py-2 rounded-lg border border-success-500 text-success-600 dark:text-success-400 hover:bg-success-50 dark:hover:bg-success-900/20 transition-colors"
          @click="handleViewAll"
        >
          <span class="text-sm font-medium">{{ $t("helpCenter.viewAll") }}</span>
          <Icon name="solar:external-link-line-duotone" class="text-base" aria-hidden="true" />
        </button>
      </div>
    </template>

    <div class="space-y-2">
      <VideoTutorialCard v-for="video in videos" :key="video.id" :video="video" @click="handleVideoClick" />
    </div>
  </LqCard>
</template>
