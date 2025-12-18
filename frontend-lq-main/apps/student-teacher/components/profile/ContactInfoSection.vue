<script setup lang="ts">
  import { useAuthStore } from "@lq/stores";
  import { computed } from "vue";
  import { SUPPORTED_LOCALES } from "@lq/i18n/config";

  export interface ContactInfo {
    email: string;
    phone?: string;
    location?: string;
    institution?: string;
    memberSince?: string;
    learningLanguage?: string;
  }

  export interface ContactInfoSectionProps {
    user: ContactInfo;
    editable?: boolean;
  }

  const props = withDefaults(defineProps<ContactInfoSectionProps>(), {
    editable: false,
  });
  defineEmits<{
    "update:user": [updates: Partial<ContactInfo>];
  }>();

  const authStore = useAuthStore();

  // Determinar si el usuario es profesor o admin institucional
  const isTeacherOrAdmin = computed(() => {
    const role = authStore.userProfile?.primaryRole || authStore.userProfileComplete?.primaryRole;
    return role === "ADMIN_INSTITUCIONAL" || role === "TEACHER";
  });

  // Texto dinámico según el rol
  const languageLabel = computed(() => {
    return isTeacherOrAdmin.value ? "profile.languageTeach" : "profile.languageInterest";
  });

  // Obtener el nombre legible del idioma
  const languageDisplay = computed(() => {
    if (!props.user?.learningLanguage) return null;

    const locale = SUPPORTED_LOCALES.find((l) => l.code === props.user.learningLanguage);
    return locale || null;
  });

  // Lista de items de contacto
  const contactItems = computed(() => [
    {
      id: "email",
      icon: "solar:letter-line-duotone",
      label: "profile.email",
      value: props.user?.email,
      type: "text" as const,
    },
    {
      id: "language",
      icon: "solar:global-line-duotone",
      label: languageLabel.value,
      value: languageDisplay.value,
      type: "language" as const,
    },
    {
      id: "institution",
      icon: "solar:buildings-line-duotone",
      label: "profile.institution",
      value: props.user?.institution || null,
      fallback: "profile.institutionNotSpecified",
      type: "text" as const,
    },
    {
      id: "memberSince",
      icon: "solar:calendar-line-duotone",
      label: "profile.memberSince",
      value: props.user?.memberSince,
      type: "text" as const,
    },
  ]);
</script>

<template>
  <div class="space-y-6">
    <h3 class="font-bold text-lg text-surface-900 dark:text-surface-100 mb-4">{{ $t("profile.contactInfo") }}</h3>

    <!-- Contact Items Loop -->
    <div v-for="item in contactItems" :key="item.id" class="flex items-start gap-4">
      <div
        class="w-10 h-10 rounded-xl bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center flex-shrink-0 text-primary-600 dark:text-primary-400"
      >
        <Icon :name="item.icon" class="text-xl" />
      </div>
      <div class="flex-1">
        <p class="text-xs text-surface-500 dark:text-surface-400 font-medium mb-1">
          {{ $t(item.label) }}
        </p>

        <!-- Language type with flag -->
        <div v-if="item.type === 'language' && item.value" class="flex items-center gap-2">
          <Icon :name="item.value.flag" class="text-lg" />
          <p class="text-sm text-surface-900 dark:text-surface-100">{{ item.value.name }}</p>
        </div>

        <!-- Text type -->
        <p
          v-else-if="item.type === 'text'"
          class="text-sm text-surface-900 dark:text-surface-100"
          :class="{ 'break-all': item.id === 'email' }"
        >
          {{ item.value || (item.fallback ? $t(item.fallback) : "-") }}
        </p>

        <!-- Empty state -->
        <p v-else class="text-sm text-surface-500 dark:text-surface-400">-</p>
      </div>
    </div>
  </div>
</template>
