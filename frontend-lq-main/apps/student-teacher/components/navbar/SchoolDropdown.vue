<script setup lang="ts">
  import { ref } from "vue";
  import Ripple from "primevue/ripple";
  import { onClickOutside } from "@vueuse/core";
  import type { MenuItem } from "primevue/menuitem";

  const vRipple = Ripple;

  defineOptions({
    name: "SchoolDropdown",
  });

  interface Props {
    /**
     * Organization/School name to display
     */
    organizationName: string;
    /**
     * Menu items for the dropdown
     */
    menuItems: MenuItem[];
    /**
     * Icon to display
     * @default 'solar:square-academic-cap-linear'
     */
    icon?: string;
    /**
     * Show text label (false for mobile icon-only mode)
     * @default true
     */
    showText?: boolean;
  }

  const props = withDefaults(defineProps<Props>(), {
    icon: "solar:square-academic-cap-linear",
    showText: true,
  });

  const emit = defineEmits<{
    select: [itemId: string];
  }>();

  const menuOpen = ref(false);
  const menuRef = ref();

  const toggleMenu = () => {
    menuOpen.value = !menuOpen.value;
  };

  // Close menu when clicking outside
  onClickOutside(menuRef, () => {
    menuOpen.value = false;
  });

  const handleSelect = (item: MenuItem) => {
    if (item.data?.id) {
      emit("select", item.data.id);
    }
    menuOpen.value = false;
  };
</script>

<template>
  <div ref="menuRef" class="relative">
    <button
      v-ripple
      type="button"
      :class="[
        'flex items-center gap-3 rounded-lg bg-surface-100 p-2 dark:bg-surface-800/20 transition-colors hover:bg-surface-200 dark:hover:bg-surface-700/30 focus:outline-none',
        props.showText ? 'min-w-40 max-w-64 flex-1' : 'w-10 h-10 justify-center shrink-0',
      ]"
      @click="toggleMenu"
    >
      <slot name="icon">
        <Icon
          name="solar:square-academic-cap-linear"
          :class="['size-5 text-surface-500 dark:text-surface-400', props.showText ? 'ml-2' : '']"
        />
      </slot>
      <span v-if="props.showText" class="flex-1 text-left text-base font-medium text-surface-900 dark:text-surface-0">
        {{ organizationName }}
      </span>
      <slot v-if="props.showText" name="arrow-icon">
        <Icon name="solar:alt-arrow-down-linear" class="mr-2 size-4 text-surface-500 dark:text-surface-400" />
      </slot>
    </button>

    <!-- Custom Dropdown Menu -->
    <Transition
      enter-active-class="transition ease-out duration-100"
      enter-from-class="transform opacity-0 scale-95"
      enter-to-class="transform opacity-100 scale-100"
      leave-active-class="transition ease-in duration-75"
      leave-from-class="transform opacity-100 scale-100"
      leave-to-class="transform opacity-0 scale-95"
    >
      <div
        v-if="menuOpen"
        class="absolute left-0 top-full z-50 mt-2 w-64 rounded-xl p-2 shadow-lg ring-1 ring-black/5 dark:ring-white/5 bg-gradient-to-b from-surface-50 to-surface-100 dark:from-surface-800 dark:to-surface-950"
      >
        <ul class="flex flex-col gap-1">
          <li v-for="(item, index) in menuItems" :key="item.id">
            <button
              v-ripple
              type="button"
              :class="[
                'relative flex w-full items-center gap-3 rounded-lg px-5 py-2.5 text-left transition-all duration-200',
                index === 0
                  ? 'bg-surface-200 dark:bg-[#2A2D3A] text-surface-900 dark:text-surface-50'
                  : 'text-surface-600 dark:text-surface-400 hover:bg-surface-100/50 dark:hover:bg-white/5',
              ]"
              @click="handleSelect(item.id)"
            >
              <!-- Active indicator bar (only for first item) -->
              <span v-if="index === 0" class="absolute left-0 top-0 bottom-0 w-2.5 bg-primary-500 rounded-l-xl" />
              <span class="text-sm font-medium">{{ item.label }}</span>
            </button>
          </li>
        </ul>
      </div>
    </Transition>
  </div>
</template>
