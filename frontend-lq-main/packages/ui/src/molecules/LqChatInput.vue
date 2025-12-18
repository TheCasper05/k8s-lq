<script setup lang="ts">
  import InputText from "primevue/inputtext";
  import IconField from "primevue/iconfield";
  import InputIcon from "primevue/inputicon";

  interface Props {
    placeholder?: string;
    disclaimer?: string;
    modelValue?: string;
  }

  withDefaults(defineProps<Props>(), {
    placeholder: "Type your question...",
    disclaimer: "AI can make mistakes. Check important info.",
    modelValue: "",
  });

  const emit = defineEmits<{
    "update:modelValue": [value: string];
    "send": [];
    "attach": [];
  }>();

  const handleInput = (event: Event) => {
    const target = event.target as HTMLInputElement;
    emit("update:modelValue", target.value);
  };

  const handleSend = () => {
    emit("send");
  };

  const handleKeydown = (event: KeyboardEvent) => {
    if (event.key === "Enter") {
      handleSend();
    }
  };
</script>

<template>
  <div class="p-4 bg-white dark:bg-surface-900 border-t border-surface-100 dark:border-surface-800 shrink-0">
    <div class="relative flex items-center gap-2">
      <IconField class="flex-1">
        <InputIcon class="cursor-pointer" @click="emit('attach')">
          <Icon
            name="solar:paperclip-linear"
            class="size-5 text-surface-500 dark:text-surface-400 hover:dark:text-surface-300 hover:text-surface-600 duration-200 -mt-0.5"
          />
        </InputIcon>
        <InputText
          :value="modelValue"
          type="text"
          :placeholder="placeholder"
          class="!w-full !py-3 !pl-12 !pr-14 !rounded-full !bg-surface-50 dark:!bg-surface-800 !border-none !text-sm focus:!ring-1 focus:!ring-primary-500 shadow-none"
          @input="handleInput"
          @keydown="handleKeydown"
        />
        <InputIcon class="!right-2 cursor-pointer" @click="handleSend">
          <div
            class="flex size-9 items-center justify-center -mt-2.5 rounded-full bg-surface-200/50 dark:bg-surface-900/50 text-surface-600 dark:text-surface-400 hover:bg-surface-200 dark:hover:bg-surface-900 transition-colors"
          >
            <Icon name="solar:plain-2-linear" />
          </div>
        </InputIcon>
      </IconField>
    </div>
    <div class="text-center mt-2">
      <span class="text-[10px] text-surface-400">{{ disclaimer }}</span>
    </div>
  </div>
</template>
