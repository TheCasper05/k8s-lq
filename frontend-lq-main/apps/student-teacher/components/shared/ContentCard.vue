<script setup lang="ts">
  import { computed } from "vue";

  interface TopAction {
    id: string;
    icon: string;
    class: string;
    onClick: (event: MouseEvent) => void;
  }

  interface Props {
    /**
     * Cover image URL
     */
    coverImage?: string;
    /**
     * Alt text for cover image
     */
    coverAlt?: string;
    /**
     * Show default icon when no cover image
     */
    showDefaultIcon?: boolean;
    /**
     * Default icon name (when no cover image)
     */
    defaultIcon?: string;
    /**
     * Top right action buttons
     */
    topActions?: TopAction[];
    /**
     * Enable hover effects (scale, shadow, translate)
     */
    hoverable?: boolean;
  }

  const props = withDefaults(defineProps<Props>(), {
    coverImage: undefined,
    coverAlt: "",
    showDefaultIcon: false,
    defaultIcon: "solar:book-line-duotone",
    topActions: () => [],
    hoverable: true,
  });

  const emit = defineEmits<{
    click: [];
  }>();

  const cardClasses = computed(() => {
    const base =
      "group flex flex-col h-full rounded-2xl bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 overflow-hidden cursor-pointer";
    const hover = props.hoverable ? "transition-all duration-300 hover:shadow-xl hover:-translate-y-1" : "";
    return [base, hover].filter(Boolean).join(" ");
  });

  const handleClick = () => {
    emit("click");
  };
</script>

<template>
  <div :class="cardClasses" @click="handleClick">
    <!-- Cover Image Area -->
    <div class="relative h-56 shrink-0 overflow-hidden bg-surface-100 dark:bg-surface-800">
      <!-- Image -->
      <img
        v-if="coverImage"
        :src="coverImage"
        :alt="coverAlt"
        class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
      />
      <!-- Default Icon (when no image) -->
      <div
        v-else-if="showDefaultIcon"
        class="w-full h-full bg-gradient-to-br from-primary-100 to-primary-200 dark:from-primary-900 dark:to-primary-800 flex items-center justify-center transition-transform duration-500 group-hover:scale-110"
      >
        <Icon :name="defaultIcon" class="text-6xl text-primary-600 dark:text-primary-400" />
      </div>

      <!-- Gradient Overlay -->
      <div class="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent" />

      <!-- Top Right Actions -->
      <div v-if="topActions.length > 0" class="absolute top-3 right-3 flex items-center gap-2">
        <button
          v-for="action in topActions"
          :key="action.id"
          :class="action.class"
          @click.stop="action.onClick($event as MouseEvent)"
        >
          <Icon :name="action.icon" class="text-xl" />
        </button>
      </div>

      <!-- Cover Overlay Slot (for badges, etc.) -->
      <slot name="cover-overlay" />
    </div>

    <!-- Content Body -->
    <div class="flex flex-col flex-1 p-5">
      <!-- Title Slot -->
      <slot name="title" />

      <!-- Badges/Tags Slot -->
      <slot name="badges" />

      <!-- Description/Content Slot -->
      <slot name="content" />

      <!-- Footer Actions -->
      <div v-if="$slots.footer" class="mt-auto pt-4 border-t border-surface-100 dark:border-surface-800/50">
        <slot name="footer" />
      </div>
    </div>

    <!-- Context Menu Slot -->
    <slot name="menu" />
  </div>
</template>
