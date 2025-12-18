<script setup lang="ts">
  import Badge from "primevue/badge";
  import Ripple from "primevue/ripple";

  const vRipple = Ripple;

  defineOptions({
    name: "SettingsButton",
  });

  interface Props {
    /**
     * Badge count
     * @default 0
     */
    count?: number;
    /**
     * Icon name
     * @default 'solar:settings-linear'
     */
    icon?: string;
  }

  withDefaults(defineProps<Props>(), {
    count: 0,
    icon: "solar:settings-linear",
  });

  const emit = defineEmits<{
    click: [event: Event];
  }>();

  const handleClick = (event: Event) => {
    emit("click", event);
  };
</script>

<template>
  <div class="relative">
    <button
      v-ripple
      type="button"
      class="flex size-10 items-center justify-center rounded-lg bg-surface-100 text-surface-600 transition-colors hover:bg-surface-200 focus:outline-none dark:bg-surface-800 dark:text-surface-400 dark:hover:bg-surface-700"
      aria-label="Settings"
      @click="handleClick"
    >
      <slot name="icon">
        <span class="size-5">⚙️</span>
      </slot>
    </button>
    <Badge
      v-if="count > 0"
      :value="count > 99 ? '99+' : count.toString()"
      class="absolute right-0 top-0"
      style="font-size: 0.625rem; min-width: 1rem; height: 1rem; line-height: 1rem"
    />
  </div>
</template>
