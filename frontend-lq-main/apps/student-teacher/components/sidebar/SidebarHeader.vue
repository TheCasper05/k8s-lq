<script setup lang="ts">
  interface Props {
    logoSrc?: string;
    logoAlt?: string;
    showLockButton?: boolean;
    showCloseButton?: boolean;
    isLocked?: boolean;
    lockTooltip?: string;
  }

  withDefaults(defineProps<Props>(), {
    logoSrc: undefined,
    logoAlt: "Logo",
    showLockButton: true,
    showCloseButton: false,
    isLocked: false,
    lockTooltip: "Bloquear selección de menú",
  });

  defineEmits<{
    "toggle-lock": [];
    "close": [];
  }>();
</script>

<template>
  <div class="flex shrink-0 items-center justify-between px-6 pt-4 pb-2">
    <span class="inline-flex items-center gap-3">
      <slot name="logo">
        <img v-if="logoSrc" :src="logoSrc" :alt="logoAlt" class="size-auto" />
      </slot>
    </span>
    <!-- Close button for mobile/tablet -->
    <span v-if="showCloseButton">
      <Button
        v-tooltip.left="'Cerrar'"
        type="button"
        text
        rounded
        class="!h-10 !w-10 !rounded-xl !transition-all !duration-200 !outline-none !ring-0 !border-0 !p-0 !bg-surface-200/50 dark:!bg-surface-700/50 hover:!bg-surface-200 dark:hover:!bg-surface-700"
        @click="$emit('close')"
      >
        <template #icon>
          <Icon name="solar:close-circle-linear" class="size-5 text-surface-700 dark:text-surface-200" />
        </template>
      </Button>
    </span>
    <!-- Lock button for desktop -->
    <span v-else-if="showLockButton">
      <Button
        v-tooltip.left="lockTooltip"
        type="button"
        text
        rounded
        :class="[
          '!h-10 !w-10 !rounded-xl !transition-all !duration-200 !outline-none !ring-0 !border-0 !p-0',
          isLocked
            ? '!bg-primary-100 dark:!bg-primary-900/30 hover:!bg-primary-200 dark:hover:!bg-primary-900/50'
            : '!bg-surface-200/50 dark:!bg-surface-700/50 hover:!bg-surface-200 dark:hover:!bg-surface-700',
        ]"
        @click="$emit('toggle-lock')"
      >
        <template #icon>
          <Icon
            :name="isLocked ? 'solar:lock-bold' : 'solar:lock-unlocked-linear'"
            :class="[
              'size-5',
              isLocked ? 'text-primary-600 dark:text-primary-400' : 'text-surface-700 dark:text-surface-200',
            ]"
          />
        </template>
      </Button>
    </span>
  </div>
</template>
