<script setup lang="ts">
  import { LqBanner } from "@lq/ui";
  import lqPersonWithGlasses from "~/assets/images/lq-person-with-glasses.png";

  defineProps<{
    title?: string;
    subtitle?: string;
  }>();
</script>

<template>
  <LqBanner :title="title || $t('profile.title')" :description="subtitle || $t('profile.subtitle')" rounded="xl">
    <template #icon>
      <div class="size-16 rounded-full flex items-center justify-center">
        <Avatar
          unstyled
          pt:root="size-16 rounded-full flex items-center justify-center"
          :image="lqPersonWithGlasses"
          shape="circle"
          size="large"
        />
      </div>
    </template>
  </LqBanner>
</template>
