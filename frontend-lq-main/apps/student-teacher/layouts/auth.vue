<script setup lang="ts">
  import AuthInfo from "~/components/AuthInfo.vue";
  import LanguageSelector from "~/components/LanguageSelector.vue";
  import { ThemeToggle } from "@lq/ui";

  import logoLqGrouped from "~/assets/images/logo-lq-grouped.png";
  import logoLqCollapsed from "~/assets/images/logo-lq-collapsed.png";

  interface Props {
    infoHeading?: string;
    infoSubheading?: string;
    illustrationSrc?: string;
  }

  const props = withDefaults(defineProps<Props>(), {
    infoHeading: "Practice English with your AI Tutor!",
    infoSubheading: "Your learning companion is ready to help you master English in a fun way",
    illustrationSrc: "/images/auth-illustration.svg",
  });

  const infoProps = computed(() => ({
    heading: props.infoHeading,
    subheading: props.infoSubheading,
    illustrationSrc: props.illustrationSrc,
  }));

  const route = useRoute();
  const isRegister = computed(() => route.path.includes("/register"));

  const { fetchCountries } = useCountries();

  // Prefetch countries for register flow
  onMounted(() => {
    fetchCountries();
  });
</script>

<template>
  <div
    class="min-h-screen bg-gradient-to-br from-[#F5F3FF] via-[#FAF8FF] to-[#F0EDFF] dark:from-surface-950 dark:via-surface-900 dark:to-surface-950"
  >
    <!-- Top Right Controls -->
    <div class="absolute top-3 right-3 sm:top-4 sm:right-4 lg:top-6 lg:right-6 z-10 flex items-center gap-2 sm:gap-3">
      <!-- Dark/Light Mode Toggle -->
      <ThemeToggle variant="auth" />

      <!-- Language Selector -->
      <LanguageSelector />
    </div>

    <!-- Main Content - Two Column Layout -->
    <div class="flex min-h-screen">
      <!-- Left Column - Auth Forms -->
      <div class="w-full xl:w-2/5 flex items-center justify-center p-4 sm:p-6 lg:p-8">
        <!-- Logo -->
        <!-- Logo (Login / Top) -->
        <Transition
          enter-active-class="transition-opacity duration-500 delay-200 ease-in-out"
          enter-from-class="opacity-0"
          enter-to-class="opacity-100"
          leave-active-class="transition-opacity duration-500 ease-in-out delay-100"
          leave-from-class="opacity-100"
          leave-to-class="opacity-0"
        >
          <div v-if="!isRegister" class="absolute top-3 left-4 sm:top-4 sm:left-6 lg:top-6 lg:left-8 z-20">
            <NuxtLink to="/">
              <img :src="logoLqGrouped" alt="LingoQuesto" class="w-auto h-12 sm:h-16 lg:h-20" />
            </NuxtLink>
          </div>
        </Transition>

        <!-- Logo (Register / Bottom) -->
        <Transition
          enter-active-class="transition-opacity duration-500 delay-200 ease-in-out"
          enter-from-class="opacity-0"
          enter-to-class="opacity-100"
          leave-active-class="transition-opacity duration-500 ease-in-out delay-100"
          leave-from-class="opacity-100"
          leave-to-class="opacity-0"
        >
          <div v-if="isRegister" class="absolute bottom-3 left-4 sm:bottom-4 sm:left-6 lg:bottom-6 lg:left-8 z-20">
            <NuxtLink to="/">
              <img :src="logoLqCollapsed" alt="LingoQuesto" class="w-auto h-10 sm:h-11 lg:h-12" />
            </NuxtLink>
          </div>
        </Transition>

        <!-- Form Content Slot -->
        <div class="w-full">
          <slot />
        </div>
      </div>

      <!-- Right Column - Informational (Hidden on mobile) -->
      <div class="hidden xl:flex xl:w-3/5 relative overflow-hidden items-center justify-center">
        <!-- Background Decorative Elements - Stars -->
        <div class="absolute top-16 right-32 text-yellow-300 text-3xl opacity-60">✨</div>
        <div class="absolute top-24 right-16 text-yellow-200 text-2xl opacity-50">✨</div>
        <div class="absolute top-48 left-24 text-yellow-300 text-2xl opacity-60">⭐</div>
        <div class="absolute bottom-32 right-24 text-yellow-200 text-3xl opacity-50">✨</div>
        <div class="absolute bottom-48 left-16 text-yellow-300 text-2xl opacity-60">⭐</div>
        <div class="absolute top-32 left-1/3 text-yellow-200 text-xl opacity-40">✨</div>
        <div class="absolute bottom-24 right-1/3 text-yellow-300 text-xl opacity-50">⭐</div>

        <!-- Info Component -->
        <AuthInfo v-bind="infoProps" />
      </div>
    </div>
  </div>
</template>
