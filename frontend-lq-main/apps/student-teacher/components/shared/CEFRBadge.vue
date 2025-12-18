<script setup lang="ts">
  import { computed } from "vue";
  import Badge from "primevue/badge";
  import type { CEFRLevel } from "~/types/activities";

  interface Props {
    level: CEFRLevel;
    size?: "sm" | "md" | "lg";
    noColor?: boolean;
    text?: string;
  }

  const props = withDefaults(defineProps<Props>(), {
    size: "md",
    noColor: false,
    text: "",
  });

  const badgeValue = computed(() => {
    if (props.text?.length) return `${props.text} ${props.level}`;
    return props.level;
  });

  const badgeSeverity = computed(() => {
    if (props.noColor) return "secondary";

    const severityMap: Record<CEFRLevel, "info" | "success" | "warn" | "danger" | "secondary" | "contrast"> = {
      A1: "info",
      A2: "info",
      B1: "success",
      B2: "warn",
      C1: "warn",
      C2: "danger",
    };
    return severityMap[props.level];
  });

  const badgeClass = computed(() => {
    const sizeClasses = {
      sm: "px-2 py-0.5 text-[10px]",
      md: "px-2.5 py-1 text-xs",
      lg: "px-3 py-1.5 text-sm",
    };
    return sizeClasses[props.size];
  });
</script>

<template>
  <Badge :value="badgeValue" :severity="badgeSeverity" :class="badgeClass" class="font-semibold! uppercase!" />
</template>
