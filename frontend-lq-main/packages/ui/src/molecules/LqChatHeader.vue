<script setup lang="ts">
  import Button from "primevue/button";

  interface Props {
    logoSrc?: string;
    logoAlt?: string;
    title?: string;
    subtitle?: string;
    isOnline?: boolean;
  }

  withDefaults(defineProps<Props>(), {
    logoSrc: undefined,
    logoAlt: "Logo",
    title: "Support",
    subtitle: "online",
    isOnline: true,
  });

  const emit = defineEmits<{
    refresh: [];
    minimize: [];
    close: [];
  }>();

  const headerActions = [
    { icon: "solar:refresh-circle-linear", action: "refresh" as const, handler: () => emit("refresh") },
    { icon: "solar:minimize-square-3-linear", action: "minimize" as const, handler: () => emit("minimize") },
    { icon: "solar:close-circle-linear", action: "close" as const, handler: () => emit("close") },
  ];
</script>

<template>
  <div class="bg-primary-700 border-b border-primary-600 p-4 flex items-center justify-between shrink-0">
    <div class="flex items-center gap-3">
      <div class="relative">
        <div class="size-10 bg-primary-500 rounded-xl border-2 border-white flex items-center justify-center shadow-sm">
          <img v-if="logoSrc" :src="logoSrc" :alt="logoAlt" class="size-7 object-contain" />
        </div>
        <span
          v-if="isOnline"
          class="absolute -top-1 -right-1 size-3 bg-green-400 border-2 border-primary-700 rounded-full"
        />
      </div>
      <div>
        <h3 class="font-bold text-lg leading-tight text-white">{{ title }}</h3>
        <p class="text-xs text-primary-100">{{ subtitle }}</p>
      </div>
    </div>
    <div class="flex items-center gap-1">
      <Button
        v-for="{ icon, action, handler } in headerActions"
        :key="action"
        text
        rounded
        class="!p-2 !text-primary-100 hover:!text-white hover:!bg-white/10 !size-10 !flex !items-center !justify-center"
        @click="handler"
      >
        <template #icon>
          <Icon :name="icon" class="size-10" />
        </template>
      </Button>
    </div>
  </div>
</template>
