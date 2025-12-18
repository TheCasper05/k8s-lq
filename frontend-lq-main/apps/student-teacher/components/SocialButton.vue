<script setup lang="ts">
  interface Props {
    provider: "google" | "microsoft";
    label?: string;
    variant?: "full" | "compact";
  }

  const props = withDefaults(defineProps<Props>(), {
    variant: "full",
    label: "",
  });

  const { login, loading } = useSocialAuth();

  const providerStyles = {
    google: {
      name: "Google",
      icon: "meteor-icons:google",
      border: "border-surface-300",
      bg: "bg-white",
      hover: "hover:bg-surface-50",
    },
    microsoft: {
      name: "Microsoft",
      icon: "mdi:microsoft",
      border: "border-surface-300",
      bg: "bg-white",
      hover: "hover:bg-surface-50",
    },
  };

  const handleClick = () => login(props.provider);
</script>

<template>
  <Button
    v-if="variant === 'full'"
    :class="[
      'w-full justify-center gap-2 sm:gap-3 !border !border-gray-200 transition-all duration-200 !rounded-xl !py-2.5 sm:!py-3 !font-medium !text-sm sm:!text-base !text-gray-700 bg-gray-50 hover:bg-gray-100',
      providerStyles[provider].bg,
      providerStyles[provider].hover,
      'dark:border-surface-600 dark:bg-surface-800 dark:hover:bg-surface-700 dark:!text-surface-200',
    ]"
    :label="label"
    outlined
    :disabled="loading"
    @click="handleClick"
  >
    <template #icon>
      <Icon :name="providerStyles[provider].icon" class="text-lg" />
    </template>
  </Button>

  <Button v-else outlined severity="secondary" class="w-full" :disabled="loading" @click="handleClick">
    <div class="flex items-center justify-center gap-2">
      <Icon :name="providerStyles[provider].icon" size="20" />
      <span class="text-sm font-medium">{{ providerStyles[provider].name }}</span>
    </div>
  </Button>
</template>
