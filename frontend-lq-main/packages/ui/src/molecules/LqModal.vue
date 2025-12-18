<script setup lang="ts">
  import { computed } from "vue";

  interface Props {
    modelValue: boolean;
    title?: string;
    size?: "sm" | "md" | "lg" | "xl";
    closable?: boolean;
    closeOnBackdrop?: boolean;
    /**
     * Test ID for automated testing
     */
    testId?: string;
    /**
     * ARIA label for the modal
     */
    ariaLabel?: string;
  }

  const props = withDefaults(defineProps<Props>(), {
    title: undefined,
    size: "md",
    closable: true,
    closeOnBackdrop: true,
    testId: undefined,
    ariaLabel: undefined,
  });

  const computedTestId = computed(() => {
    return props.testId || "lq-modal";
  });

  const computedAriaLabel = computed(() => {
    return props.ariaLabel || props.title || "Modal dialog";
  });

  const emit = defineEmits<{
    "update:modelValue": [value: boolean];
    "close": [];
  }>();

  const modalClasses = computed(() => {
    const sizes = {
      sm: "max-w-[95vw] sm:max-w-sm",
      md: "max-w-[95vw] sm:max-w-md",
      lg: "max-w-[95vw] sm:max-w-lg",
      xl: "max-w-[95vw] sm:max-w-xl",
    };

    return sizes[props.size];
  });

  const handleClose = () => {
    if (props.closable) {
      emit("update:modelValue", false);
      emit("close");
    }
  };

  const handleBackdropClick = () => {
    if (props.closeOnBackdrop) {
      handleClose();
    }
  };

  const handleEscapeKey = (event: KeyboardEvent) => {
    if (event.key === "Escape" && props.closable) {
      handleClose();
    }
  };
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 overflow-y-auto"
        :data-testid="computedTestId"
        role="dialog"
        aria-modal="true"
        :aria-labelledby="title ? `${computedTestId}-title` : undefined"
        :aria-label="!title ? computedAriaLabel : undefined"
        @click.self="handleBackdropClick"
        @keydown.esc="handleEscapeKey"
      >
        <div class="flex min-h-screen items-center justify-center p-3 sm:p-4">
          <!-- Backdrop -->
          <div
            class="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
            :data-testid="`${computedTestId}-backdrop`"
            aria-hidden="true"
          />

          <!-- Modal -->
          <div
            :class="modalClasses"
            class="relative z-10 w-full rounded-lg bg-white dark:bg-surface-900 shadow-xl transform transition-all"
            :data-testid="`${computedTestId}-content`"
            @click.stop
          >
            <!-- Header -->
            <div
              v-if="title || $slots.header"
              class="flex items-center justify-between border-b border-surface-200 dark:border-surface-700 px-4 sm:px-6 py-3 sm:py-4"
            >
              <slot name="header">
                <h3
                  :id="`${computedTestId}-title`"
                  class="text-base sm:text-lg font-semibold text-surface-900 dark:text-surface-50"
                >
                  {{ title }}
                </h3>
              </slot>
              <button
                v-if="closable"
                type="button"
                class="text-surface-400 dark:text-surface-500 hover:text-surface-500 dark:hover:text-surface-400 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded"
                :data-testid="`${computedTestId}-close-button`"
                aria-label="Close modal"
                @click="handleClose"
              >
                <span class="sr-only">Close</span>
                <svg class="size-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <!-- Body -->
            <div class="px-4 sm:px-6 py-3 sm:py-4">
              <slot />
            </div>

            <!-- Footer -->
            <div
              v-if="$slots.footer"
              class="flex justify-end gap-2 sm:gap-3 border-t border-surface-200 dark:border-surface-700 px-4 sm:px-6 py-3 sm:py-4"
            >
              <slot name="footer" />
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
  .modal-enter-active,
  .modal-leave-active {
    transition: opacity 0.3s ease;
  }

  .modal-enter-from,
  .modal-leave-to {
    opacity: 0;
  }
</style>
