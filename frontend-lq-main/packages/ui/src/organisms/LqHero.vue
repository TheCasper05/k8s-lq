<script setup lang="ts">
  import { computed } from "vue";
  import LqBanner from "../molecules/LqBanner.vue";

  type HeroVariant = "banner" | "card" | "detailed";
  type HeroLayout = "horizontal" | "vertical" | "three-column";
  type ImageAspect = "square" | "video" | "wide";

  interface Props {
    // Variant
    variant?: HeroVariant;

    // Image
    image?: string;
    imageAspect?: ImageAspect;
    showPlayButton?: boolean;

    // Content
    title?: string;
    subtitle?: string;
    description?: string;

    // Navigation
    showBackButton?: boolean;
    backRoute?: string;

    // Layout
    layout?: HeroLayout;

    // LqBanner props (when variant="banner")
    icon?: string;
    rounded?: "lg" | "xl" | "2xl" | "3xl" | "full";
    showIconBackground?: boolean;
    size?: "sm" | "md" | "lg";
    iconContainerClass?: string;

    // Testing and accessibility
    /**
     * Test ID for automated testing
     */
    testId?: string;
    /**
     * ARIA label for the hero section
     */
    ariaLabel?: string;
  }

  const props = withDefaults(defineProps<Props>(), {
    variant: "banner",
    image: undefined,
    imageAspect: "video",
    showPlayButton: false,
    title: undefined,
    subtitle: undefined,
    description: undefined,
    showBackButton: true,
    backRoute: undefined,
    layout: "horizontal",
    icon: undefined,
    rounded: "3xl",
    showIconBackground: true,
    size: "md",
    iconContainerClass: undefined,
    testId: undefined,
    ariaLabel: undefined,
  });

  const computedTestId = computed(() => {
    return props.testId || `lq-hero-${props.variant}`;
  });

  const computedAriaLabel = computed(() => {
    return props.ariaLabel || props.title || "Hero section";
  });

  const emit = defineEmits<{
    "back": [];
    "image-click": [];
  }>();

  const imageAspectClass = computed(() => {
    switch (props.imageAspect) {
      case "square":
        return "aspect-square";
      case "wide":
        return "aspect-[21/9]";
      case "video":
      default:
        return "aspect-video";
    }
  });

  const handleBack = () => {
    emit("back");
  };

  const handleImageClick = () => {
    emit("image-click");
  };
</script>

<template>
  <!-- Variant: Banner (uses LqBanner) -->
  <LqBanner
    v-if="variant === 'banner'"
    :title="title"
    :description="description"
    :icon="icon"
    :rounded="rounded"
    :show-icon-background="showIconBackground"
    :size="size"
    :icon-container-class="iconContainerClass"
  >
    <template v-if="$slots.icon" #icon>
      <slot name="icon" />
    </template>
    <template v-if="$slots.default">
      <slot />
    </template>
    <template v-if="$slots.action" #action>
      <slot name="action" />
    </template>
  </LqBanner>

  <!-- Variant: Card (Activities Detail style) -->
  <section
    v-else-if="variant === 'card'"
    class="bg-surface-0 dark:bg-surface-900 rounded-3xl border border-surface-200 dark:border-surface-700 shadow-sm p-4 sm:p-5"
    :data-testid="computedTestId"
    :aria-label="computedAriaLabel"
  >
    <div class="flex flex-col lg:flex-row gap-4 sm:gap-6">
      <!-- Thumbnail Image -->
      <div v-if="image || $slots.image" class="shrink-0">
        <slot name="image">
          <div
            :class="[
              'relative w-full h-full lg:w-52 rounded-lg overflow-hidden group cursor-pointer',
              imageAspectClass,
            ]"
            @click="handleImageClick"
          >
            <img
              v-if="image"
              :src="image"
              :alt="title"
              class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            />
            <div
              v-if="showPlayButton"
              class="absolute inset-0 bg-black/20 group-hover:bg-black/40 transition-colors flex items-center justify-center"
            >
              <div
                class="size-14 rounded-full bg-white/90 flex items-center justify-center text-primary-600 shadow-lg transform scale-90 group-hover:scale-110 transition-all"
              >
                <slot name="play-icon">
                  <Icon name="solar:play-circle-linear" class="text-2xl" />
                </slot>
              </div>
            </div>
            <slot name="image-overlay" />
          </div>
        </slot>
      </div>

      <!-- Content -->
      <div class="flex-1 min-w-0 flex flex-col justify-between gap-3 sm:gap-3">
        <!-- Header Section -->
        <div class="space-y-3">
          <!-- Back Button - Mobile: absolute top-left, Desktop: inline -->
          <div class="relative">
            <slot v-if="showBackButton" name="back-button" :on-back="handleBack">
              <button
                type="button"
                class="absolute left-0 top-0 sm:relative flex items-center justify-center w-8 h-8 rounded-lg bg-surface-200 dark:bg-surface-0 text-surface-600 dark:text-surface-900 hover:bg-surface-300 dark:hover:bg-surface-100 transition-colors z-10 focus:outline-none focus:ring-2 focus:ring-primary-500"
                :data-testid="`${computedTestId}-back-button`"
                aria-label="Go back"
                @click="handleBack"
              >
                <Icon name="solar:arrow-left-linear" class="text-sm" aria-hidden="true" />
              </button>
            </slot>

            <div class="flex items-start justify-between gap-2">
              <div class="flex flex-col gap-2 flex-1 min-w-0 text-center lg:text-left pt-10 sm:pt-0">
                <!-- Title -->
                <h1
                  v-if="title || $slots.title"
                  class="text-base sm:text-lg md:text-xl lg:text-2xl font-bold text-surface-900 dark:text-surface-0 leading-snug line-clamp-2 px-10 sm:px-0"
                >
                  <slot name="title">{{ title }}</slot>
                </h1>
              </div>

              <!-- Header Action (e.g., Share button) - Desktop only in top right -->
              <div v-if="$slots['header-action']" class="hidden sm:block flex-shrink-0">
                <slot name="header-action" />
              </div>
            </div>
          </div>

          <!-- Metadata -->
          <div v-if="$slots.metadata" class="flex items-center justify-center lg:justify-start flex-wrap gap-2">
            <slot name="metadata" />
          </div>

          <!-- Header Action (e.g., Share button) - Mobile only below metadata -->
          <div v-if="$slots['header-action']" class="sm:hidden">
            <slot name="header-action" />
          </div>
        </div>

        <!-- Actions Row -->
        <div v-if="$slots.actions" class="flex flex-col sm:flex-row flex-wrap gap-2">
          <slot name="actions" />
        </div>
      </div>
    </div>
  </section>

  <!-- Variant: Detailed (Class Detail style) -->
  <section
    v-else-if="variant === 'detailed'"
    class="bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-3xl p-4 sm:p-5 flex flex-col md:flex-row gap-3 md:gap-0"
    :data-testid="computedTestId"
    :aria-label="computedAriaLabel"
  >
    <!-- Left Section: Image and Info -->
    <div class="flex-1 flex flex-col sm:flex-row gap-3 sm:gap-4">
      <!-- Image Section -->
      <div
        v-if="image || $slots.image"
        class="relative w-24 sm:w-32 md:w-40 lg:w-52 flex-shrink-0 rounded-lg overflow-visible"
      >
        <slot name="image">
          <div class="relative w-24 h-24 sm:w-32 sm:h-32 md:w-40 md:h-40 lg:w-52 lg:h-52 rounded-lg overflow-visible">
            <div class="w-full h-full rounded-lg overflow-hidden">
              <img v-if="image" :src="image" :alt="title" class="w-full h-full object-cover" />
              <div
                v-else
                class="w-full h-full bg-gradient-to-br from-primary-100 to-primary-200 dark:from-primary-900 dark:to-primary-800 flex items-center justify-center"
              >
                <Icon name="solar:book-2-linear" class="text-4xl text-primary-600 dark:text-primary-400" />
              </div>
            </div>

            <!-- Image Overlay (e.g., floating avatars) -->
            <slot name="image-overlay" />
          </div>
        </slot>
      </div>

      <!-- Information Section -->
      <div class="flex-1 flex flex-col gap-2">
        <!-- Navigation Buttons -->
        <div v-if="showBackButton || $slots['navigation-extra']" class="relative flex justify-start gap-2 mb-2">
          <!-- Back Button (customizable) - Mobile: absolute, Desktop: inline -->
          <slot v-if="showBackButton" name="back-button" :on-back="handleBack">
            <button
              type="button"
              class="absolute left-0 top-0 sm:relative flex items-center justify-center w-8 h-8 rounded-lg bg-surface-200 dark:bg-surface-0 text-surface-600 dark:text-surface-900 hover:bg-surface-300 dark:hover:bg-surface-100 transition-colors z-10 focus:outline-none focus:ring-2 focus:ring-primary-500"
              :data-testid="`${computedTestId}-back-button`"
              aria-label="Go back"
              @click="handleBack"
            >
              <Icon name="solar:arrow-left-linear" class="text-sm" aria-hidden="true" />
            </button>
          </slot>

          <!-- Extra Navigation Buttons -->
          <slot name="navigation-extra" />
        </div>

        <!-- Title -->
        <h1
          v-if="title || $slots.title"
          class="text-lg sm:text-xl md:text-2xl lg:text-3xl font-bold text-surface-900 dark:text-surface-100 mb-2 text-center lg:text-left pt-10 sm:pt-0 px-10 sm:px-0"
        >
          <slot name="title">{{ title }}</slot>
        </h1>

        <!-- Metadata -->
        <div v-if="$slots.metadata" class="flex justify-center lg:justify-start">
          <slot name="metadata" />
        </div>

        <!-- Additional Info -->
        <div v-if="$slots.info" class="flex justify-center lg:justify-start">
          <slot name="info" />
        </div>
      </div>
    </div>

    <!-- Right Section: Sidebar -->
    <div v-if="$slots.sidebar" class="w-full sm:w-80 flex-shrink-0 mt-3 sm:mt-0 sm:ml-4">
      <slot name="sidebar" />
    </div>
  </section>
</template>
