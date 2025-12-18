<script setup lang="ts">
  import { computed } from "vue";

  defineOptions({
    inheritAttrs: false,
  });

  interface Props {
    title?: string;
    description?: string;
    icon?: string;
    rounded?: "lg" | "xl" | "2xl" | "3xl" | "full";
    showIconBackground?: boolean;
    size?: "sm" | "md" | "lg";
    iconContainerClass?: string;
  }

  const props = withDefaults(defineProps<Props>(), {
    title: "",
    description: "",
    icon: "",
    rounded: "3xl",
    showIconBackground: true,
    size: "md",
    iconContainerClass: "backdrop-blur-sm flex items-center justify-center",
  });

  const roundedClass = computed(() => {
    switch (props.rounded) {
      case "lg":
        return "rounded-lg";
      case "xl":
        return "rounded-xl";
      case "2xl":
        return "rounded-2xl";
      case "full":
        return "rounded-full";
      case "3xl":
      default:
        return "rounded-3xl";
    }
  });

  const sizeClass = computed(() => {
    switch (props.size) {
      case "sm":
        return "px-4 sm:px-5 md:px-6 py-3 sm:py-3.5 min-h-[64px]";
      case "lg":
        return "px-5 sm:px-6 md:px-8 lg:px-10 py-5 sm:py-6 md:py-7 min-h-[112px]";
      case "md":
      default:
        return "px-4 sm:px-6 md:px-8 py-4 sm:py-4.5 md:py-5 min-h-[88px]";
    }
  });
</script>

<template>
  <div
    v-bind="$attrs"
    :class="[
      'relative overflow-hidden bg-gradient-to-r from-primary-600 to-primary-700 shadow-lg',
      roundedClass,
      sizeClass,
    ]"
  >
    <!-- Background Shapes / Decorative Elements (ProfileHeader-inspired) -->
    <!-- Right decorative circles -->
    <div
      class="absolute top-0 right-0 w-64 h-64 bg-white opacity-5 rounded-full translate-x-1/3 -translate-y-1/2 pointer-events-none"
    />
    <div
      class="absolute bottom-0 right-0 w-32 h-32 bg-white opacity-10 rounded-full translate-x-1/4 translate-y-1/4 pointer-events-none"
    />

    <!-- Left decorative shapes around icon -->
    <div
      class="absolute -left-4 top-1/2 h-28 w-28 -translate-y-1/2 rounded-full bg-white/10 blur-xl pointer-events-none"
    />
    <div
      class="absolute -left-16 top-20 size-48 rotate-45 -translate-y-1/2 rounded-full bg-white/15 pointer-events-none opacity-70"
    />

    <div class="relative flex flex-col sm:flex-row items-center justify-between gap-4 sm:gap-6 z-10">
      <div class="flex items-center gap-3 sm:gap-4 md:gap-5 w-full sm:w-auto">
        <!-- Icon / Avatar Slot -->
        <div v-if="icon || $slots.icon" class="flex items-center justify-center shrink-0">
          <!-- With background container (Activities-style) -->
          <div v-if="props.showIconBackground" :class="props.iconContainerClass">
            <slot name="icon">
              <i :class="icon" class="text-white text-3xl" />
            </slot>
          </div>

          <!-- Raw icon/avatar without extra background (ProfileHeader-style) -->
          <slot v-else name="icon">
            <i :class="icon" class="text-white text-3xl" />
          </slot>
        </div>

        <!-- Text Content -->
        <div class="text-white">
          <slot>
            <h2 v-if="title" class="text-lg sm:text-xl md:text-2xl font-bold mb-1">{{ title }}</h2>
            <p v-if="description" class="text-primary-100/90 text-xs sm:text-sm md:text-base opacity-90">
              {{ description }}
            </p>
          </slot>
        </div>
      </div>

      <!-- Optional Action (CTA) -->
      <div v-if="$slots.action" class="w-full sm:w-auto flex justify-center sm:justify-end">
        <slot name="action" />
      </div>
    </div>
  </div>
</template>
