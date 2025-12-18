<script setup lang="ts">
  import { computed } from "vue";
  import { useChatSupport, type MenuType } from "@lq/composables";

  interface Props {
    variant: MenuType;
    logoSrc?: string;
    logoAlt?: string;
    title?: string;
    subtitle?: string;
    tooltip?: string;
  }

  const props = withDefaults(defineProps<Props>(), {
    logoSrc: undefined,
    logoAlt: "Support",
    title: "Support",
    subtitle: "Online",
    tooltip: "Support Chat",
  });

  const { toggleChat, isChatOpen } = useChatSupport();

  const isIconOnly = computed(() => props.variant === "icon-only");
</script>

<template>
  <div :class="['flex', isIconOnly ? 'justify-center' : '']">
    <button
      v-tooltip.right="tooltip"
      :class="[
        'relative group flex items-center justify-center rounded-xl transition-all duration-300',
        isIconOnly ? 'w-10 h-10' : 'w-full py-3 px-4 gap-3',
        isChatOpen
          ? 'bg-transparent'
          : 'bg-surface-100 dark:bg-surface-800 hover:bg-surface-200 dark:hover:bg-surface-700',
      ]"
      @click="toggleChat"
    >
      <!-- Icon Container -->
      <div class="relative w-8 h-8 flex-shrink-0 bg-primary-500 rounded-xl flex items-center justify-center text-white">
        <img
          v-if="logoSrc"
          :src="logoSrc"
          :alt="logoAlt"
          class="w-5 h-5 object-contain transition-transform duration-300 group-hover:scale-110"
        />
        <!-- Online Indicator -->
        <span class="absolute -top-1 -right-1 flex h-3 w-3">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
          <span
            class="relative inline-flex rounded-full h-3 w-3 bg-green-500 border-2 border-surface-100 dark:border-surface-800"
          />
        </span>
      </div>

      <!-- Label for expanded state -->
      <div v-if="!isIconOnly" class="flex flex-col items-start text-left">
        <span class="text-sm font-semibold text-surface-900 dark:text-surface-50">{{ title }}</span>
        <span class="text-xs text-green-600 dark:text-green-400 font-medium">{{ subtitle }}</span>
      </div>
    </button>
  </div>
</template>
