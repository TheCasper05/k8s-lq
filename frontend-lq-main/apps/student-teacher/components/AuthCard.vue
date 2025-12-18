<script setup lang="ts">
  import loginIllustrationAvatarSrc from "~/assets/images/login-illustration-avatar.png";

  interface Props {
    titleKey?: string;
    subtitleKey?: string;
    showStepper?: boolean;
    stepIcon?: string;
    stepIconType?: "icon" | "image";
  }

  withDefaults(defineProps<Props>(), {
    showStepper: true,
    titleKey: "auth.welcomeTitle",
    subtitleKey: "auth.signInSubtitle",
    stepIcon: "",
    stepIconType: "icon",
  });
</script>

<template>
  <div class="w-full max-w-lg mx-auto px-4 sm:px-0">
    <!-- Card Container -->
    <div
      class="bg-white dark:bg-surface-900 rounded-2xl sm:rounded-3xl shadow-md p-5 sm:p-8 lg:p-10 border-2 sm:border-4 border-secondary-200"
    >
      <div v-if="showStepper" class="flex justify-center -mt-16 sm:-mt-20 lg:-mt-24 mb-4 sm:mb-6">
        <div
          class="flex justify-center items-center size-20 sm:size-24 lg:size-28 rounded-full bg-white shadow-lg border border-surface-50"
        >
          <!-- Custom Icon -->
          <div
            v-if="stepIcon && stepIconType === 'icon'"
            class="size-16 sm:size-20 lg:size-24 rounded-full bg-purple-600 flex items-center justify-center shadow-xl"
          >
            <Icon :name="stepIcon" class="size-10 sm:size-12 lg:size-16 text-white" />
          </div>
          <!-- Custom Image -->
          <div
            v-else-if="stepIcon && stepIconType === 'image'"
            class="size-16 sm:size-20 lg:size-24 rounded-full bg-purple-600 flex items-center justify-center shadow-xl overflow-hidden"
          >
            <img :src="stepIcon" alt="Step illustration" class="w-full h-full object-cover" />
          </div>
          <!-- Default Avatar -->
          <Avatar
            v-else
            unstyled
            pt:root="size-16 sm:size-20 lg:size-24 rounded-full bg-purple-600 flex items-center justify-center shadow-xl"
            pt:image="size-10 sm:size-12 lg:size-14 rounded-full"
            :image="loginIllustrationAvatarSrc"
            shape="circle"
            size="large"
          />
        </div>
      </div>
      <!-- Header -->
      <div class="text-center mb-5 sm:mb-6 lg:mb-8">
        <h1 class="text-xl sm:text-2xl font-bold dark:text-white mb-2">
          {{ $t(titleKey) }}
        </h1>
        <p class="text-surface-500 dark:text-surface-400">
          {{ $t(subtitleKey) }}
        </p>
      </div>

      <!-- Content Slot -->
      <slot />
    </div>
  </div>
</template>
