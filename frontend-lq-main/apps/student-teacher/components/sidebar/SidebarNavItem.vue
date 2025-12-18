<script setup lang="ts">
  import { computed } from "vue";
  import { useRoute } from "vue-router";

  interface Props {
    to: string;
    icon?: string;
    label?: string;
    badge?: string | number;
    iconOnly?: boolean;
    active?: boolean;
    showActiveBar?: boolean;
  }

  const props = withDefaults(defineProps<Props>(), {
    icon: undefined,
    label: undefined,
    badge: undefined,
    iconOnly: false,
    active: undefined,
    showActiveBar: false,
  });

  const route = useRoute();

  const isActive = computed(() => {
    // If active prop is explicitly set, use it
    if (props.active !== undefined) return props.active;

    // Check if current route matches the link
    if (props.to === "/") {
      return route.path === "/";
    }
    return route.path.startsWith(props.to);
  });

  const iconSize = computed(() => {
    return props.iconOnly ? "size-6" : "mr-2 size-5";
  });

  const linkClasses = computed(() => {
    const base = "flex items-center transition-all duration-200 relative";

    const spacing = props.iconOnly ? "justify-center w-full p-2.5" : "px-5 py-2.5";

    // Si showActiveBar está activo (variante static), usa fondo gris + barra lateral
    // Si no (variantes grouped, simple, icon-only), usa fondo azul completo
    const activeClasses = props.showActiveBar
      ? "bg-surface-200 dark:bg-[#2A2D3A] text-surface-900 dark:text-surface-50 rounded-lg"
      : "bg-primary-500 text-white rounded-lg";

    const inactiveClasses =
      "text-surface-600 dark:text-surface-400 hover:bg-surface-100/50 dark:hover:bg-white/5 hover:rounded-lg";

    return [base, spacing, isActive.value ? activeClasses : inactiveClasses].join(" ");
  });
</script>

<template>
  <NuxtLink :to="to" :class="linkClasses" v-bind="$attrs">
    <!-- Active indicator bar (left side) -->
    <span v-if="isActive && showActiveBar" class="absolute left-0 top-0 bottom-0 w-2.5 bg-primary-500 rounded-l-xl" />
    <Icon v-if="icon" :name="icon" :class="iconSize" />
    <span v-if="label && !iconOnly" class="font-medium">{{ label }}</span>
    <span
      v-if="badge && !iconOnly"
      class="ml-auto flex h-5 min-w-[20px] items-center justify-center rounded-full bg-red-500 px-1.5 text-xs font-bold text-white"
    >
      {{ badge }}
    </span>
    <span
      v-else-if="badge && iconOnly"
      class="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-xs font-bold text-white"
    >
      {{ badge }}
    </span>
  </NuxtLink>
</template>
