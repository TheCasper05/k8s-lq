<script setup lang="ts">
  import { computed } from "vue";
  import Avatar from "primevue/avatar";

  interface LqAvatarProps {
    /**
     * Image source URL
     */
    src?: string;
    /**
     * Alt text for the image
     */
    alt?: string;
    /**
     * Size of the avatar
     */
    size?: "sm" | "md" | "lg" | "xl" | "2xl" | "large";
    /**
     * Initials to display when no image is provided
     */
    initials?: string;
    /**
     * Label for PrimeVue Avatar (alternative to initials)
     */
    label?: string;
    /**
     * Enable edit button overlay
     */
    editable?: boolean;
    /**
     * Shape of the avatar
     */
    shape?: "circle" | "square";
    /**
     * Custom class for the avatar container
     */
    avatarClass?: string;
    /**
     * Test ID for automated testing
     */
    testId?: string;
  }

  const props = withDefaults(defineProps<LqAvatarProps>(), {
    src: undefined,
    alt: undefined,
    size: "large",
    initials: undefined,
    label: undefined,
    editable: false,
    shape: "square",
    avatarClass: undefined,
    testId: undefined,
  });

  const computedTestId = computed(() => {
    return props.testId || "lq-avatar";
  });

  const emit = defineEmits<{
    edit: [];
  }>();

  // Map custom sizes to PrimeVue size or custom classes
  const avatarSize = computed(() => {
    if (props.size === "large" || props.size === "lg") {
      return "large";
    }
    return undefined; // Let custom classes handle it
  });

  const sizeClasses = computed(() => {
    const sizes = {
      "sm": "!size-8",
      "md": "!size-10",
      "lg": "!size-10",
      "xl": "!size-12",
      "2xl": "!size-16",
      "large": "!size-10", // Default size matching AssignedStudentsTable
    };
    return sizes[props.size] || sizes.large;
  });

  // PT configuration - dynamic border radius based on shape
  const avatarPT = computed(() => {
    const borderRadius = props.shape === "circle" ? "!rounded-full" : "!rounded-lg";
    const imageBorderRadius = props.shape === "circle" ? "rounded-full" : "rounded-lg";
    return {
      root: {
        class: `${sizeClasses.value} ${borderRadius}`,
      },
      image: {
        class: `object-cover w-full h-full ${imageBorderRadius}`,
      },
    };
  });

  // Classes for initials/label avatar (no image) - dynamic border radius
  const labelAvatarClass = computed(() => {
    const borderRadius = props.shape === "circle" ? "!rounded-full" : "!rounded-lg";
    return `${sizeClasses.value} ${borderRadius} !bg-surface-100 dark:!bg-surface-800 !text-surface-600 dark:!text-surface-200 !text-base`;
  });

  const handleEdit = () => {
    emit("edit");
  };

  const displayLabel = computed(() => {
    if (props.label) return props.label;
    if (props.initials) return props.initials;
    return undefined;
  });
</script>

<template>
  <div class="relative inline-block" :data-testid="computedTestId">
    <!-- Avatar with image -->
    <Avatar
      v-if="src"
      :image="src"
      :alt="alt || 'Avatar'"
      :size="avatarSize"
      :shape="shape"
      :class="avatarClass"
      :pt="avatarPT"
      role="img"
      :aria-label="alt || 'User avatar'"
    />

    <!-- Avatar with initials/label (no image) -->
    <Avatar
      v-else
      :label="displayLabel"
      :size="avatarSize"
      :shape="shape"
      :class="[labelAvatarClass, avatarClass]"
      role="img"
      :aria-label="`Avatar with initials ${displayLabel}`"
    />

    <!-- Edit button overlay -->
    <button
      v-if="editable"
      type="button"
      class="absolute bottom-0 right-0 w-8 h-8 rounded-full bg-primary-600 hover:bg-primary-700 text-white flex items-center justify-center shadow-lg transition-colors border-2 border-surface-0 dark:border-surface-900"
      :data-testid="`${computedTestId}-edit-button`"
      aria-label="Edit avatar"
      @click="handleEdit"
    >
      <Icon name="pi:camera" class="text-sm" aria-hidden="true" />
    </button>
  </div>
</template>
