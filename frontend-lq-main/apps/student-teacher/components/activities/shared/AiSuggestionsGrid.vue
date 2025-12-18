<script setup lang="ts">
  interface AiSuggestion {
    id: string;
    title: string;
    description: string;
    icon: string;
    color: string;
  }

  const { visible, title, suggestions } = defineProps<{
    visible: boolean;
    title: string;
    suggestions: AiSuggestion[];
  }>();

  const emit = defineEmits<{
    (e: "apply", suggestion: AiSuggestion): void;
  }>();
</script>

<template>
  <Transition
    enter-active-class="transition-all duration-300 ease-out"
    enter-from-class="opacity-0 -translate-y-2"
    enter-to-class="opacity-100 translate-y-0"
    leave-active-class="transition-all duration-200 ease-in"
    leave-from-class="opacity-100 translate-y-0"
    leave-to-class="opacity-0 -translate-y-1"
  >
    <div v-if="visible" class="w-full mt-6 border-t border-surface-200 dark:border-surface-700 pt-6">
      <div class="flex items-center gap-2 mb-4">
        <Icon name="lucide:sparkles" class="text-violet-500" />
        <h4 class="font-bold text-surface-900 dark:text-surface-0">
          {{ title }}
        </h4>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          v-for="suggestion in suggestions"
          :key="suggestion.id"
          class="p-4 rounded-xl border border-surface-200 dark:border-surface-700 hover:border-violet-500 hover:ring-1 hover:ring-violet-500 hover:bg-violet-50/50 dark:hover:bg-violet-500/10 cursor-pointer transition-all group"
          @click="emit('apply', suggestion)"
        >
          <div class="flex gap-4">
            <div
              class="w-10 h-10 rounded-full flex items-center justify-center shrink-0 transition-transform group-hover:scale-110"
              :class="suggestion.color"
            >
              <Icon :name="suggestion.icon" class="text-xl" />
            </div>
            <div>
              <h5
                class="text-left font-bold text-surface-900 dark:text-surface-0 mb-1 group-hover:text-violet-700 dark:group-hover:text-violet-300"
              >
                {{ suggestion.title }}
              </h5>
              <p class="text-xs text-surface-600 dark:text-surface-400 leading-relaxed">
                {{ suggestion.description }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>
