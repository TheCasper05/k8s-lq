<script setup lang="ts">
  import { computed } from "vue";
  import AvatarGroup from "primevue/avatargroup";
  import Avatar from "primevue/avatar";

  interface AvatarItem {
    id: string;
    src?: string;
    initials?: string;
    label?: string;
  }

  interface LqAvatarGroupProps {
    /**
     * Array of avatar items to display
     */
    items: AvatarItem[];
    /**
     * Maximum number of avatars to display before showing "+N"
     * @default 3
     */
    maxDisplay?: number;
    /**
     * Size of the avatars
     * @default "md"
     */
    size?: "sm" | "md" | "lg" | "xl" | "2xl" | "large";
    /**
     * Custom class for individual avatars
     */
    avatarClass?: string;
  }

  const props = withDefaults(defineProps<LqAvatarGroupProps>(), {
    maxDisplay: 4,
    size: "md",
    avatarClass: undefined,
  });

  const displayedItems = computed(() => props.items.slice(0, props.maxDisplay));
  const remainingCount = computed(() => Math.max(0, props.items.length - props.maxDisplay));

  // Map size to PrimeVue size
  const avatarSize = computed(() => {
    if (props.size === "large" || props.size === "lg" || props.size === "md") {
      return "large";
    }
    return undefined;
  });

  const sizeClasses = computed(() => {
    const sizes = {
      "sm": "!size-8",
      "md": "!size-10",
      "lg": "!size-10",
      "xl": "!size-12",
      "2xl": "!size-16",
      "large": "!size-10",
    };
    return sizes[props.size] || sizes.large;
  });

  const getDisplayLabel = (item: AvatarItem) => {
    return item.label || item.initials;
  };
</script>

<template>
  <AvatarGroup>
    <Avatar
      v-for="item in displayedItems"
      :key="item.id"
      :image="item.src || undefined"
      :label="!item.src ? getDisplayLabel(item) : undefined"
      shape="circle"
      :size="avatarSize"
      :class="[sizeClasses, avatarClass]"
    />
    <Avatar
      v-if="remainingCount > 0"
      :label="`+${remainingCount}`"
      shape="circle"
      :size="avatarSize"
      :class="[
        sizeClasses,
        'bg-surface-200 dark:bg-surface-700 text-surface-600 dark:text-surface-400 !text-sm font-semibold',
      ]"
    />
  </AvatarGroup>
</template>
