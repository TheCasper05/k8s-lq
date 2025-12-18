<script setup lang="ts">
  interface Props {
    visible: boolean;
    title: string;
    shareUrl: string;
    lessonTitle: string;
  }

  const emit = defineEmits<{
    (e: "update:visible", value: boolean): void;
    (e: "copy" | "sendToStudents" | "shareWhatsapp" | "shareFacebook" | "shareCommunity"): void;
  }>();

  const props = defineProps<Props>();

  const dialogVisible = computed({
    get: () => props.visible,
    set: (value) => emit("update:visible", value),
  });

  const { t } = useI18n();

  const shareOptions = computed(() => [
    {
      id: "sendToStudents",
      event: "sendToStudents" as const,
      buttonClass: "hover:bg-primary-50 dark:hover:bg-primary-950/40",
      iconName: "lucide:users",
      iconWrapperClass: "w-10 h-10 rounded-lg bg-primary-100 flex items-center justify-center",
      iconClass: "text-primary-700 text-xl",
      title: t("teacher.scenarios.detail.share.sendToStudents.title") || "Send to Students",
      subtitle: t("teacher.scenarios.detail.share.sendToStudents.subtitle") || "Share with your classes",
      hasSubtitle: true,
    },
    {
      id: "shareWhatsapp",
      event: "shareWhatsapp" as const,
      buttonClass: "hover:bg-emerald-50 dark:hover:bg-emerald-900/20",
      iconName: "mdi:whatsapp",
      iconWrapperClass: "size-10 rounded-lg bg-green-400 flex items-center justify-center",
      iconClass: "text-white text-xl",
      title: t("teacher.scenarios.detail.share.whatsapp") || "WhatsApp",
      subtitle: "",
      hasSubtitle: false,
    },
    {
      id: "shareFacebook",
      event: "shareFacebook" as const,
      buttonClass: "hover:bg-blue-50 dark:hover:bg-blue-900/20",
      iconName: "mdi:facebook",
      iconWrapperClass: "size-10 rounded-lg bg-blue-600 flex items-center justify-center",
      iconClass: "text-white text-xl",
      title: t("teacher.scenarios.detail.share.facebook") || "Facebook",
      subtitle: "",
      hasSubtitle: false,
    },
    {
      id: "shareCommunity",
      event: "shareCommunity" as const,
      buttonClass: "hover:bg-primary-50 dark:hover:bg-primary-900/20",
      iconName: "solar:share-line-duotone",
      iconWrapperClass: "w-10 h-10 rounded-lg bg-primary-100 flex items-center justify-center",
      iconClass: "text-primary-700 text-xl",
      title: t("teacher.scenarios.detail.share.community.title") || "LingoQuesto Community",
      subtitle: t("teacher.scenarios.detail.share.community.subtitle") || "Earn +400 tokens when 3 teachers view",
      hasSubtitle: true,
    },
  ]);

  const handleCopy = () => {
    emit("copy");
  };
</script>

<template>
  <Dialog
    v-model:visible="dialogVisible"
    modal
    :header="title"
    class="w-full max-w-sm md:max-w-lg"
    @update:visible="emit('update:visible', $event)"
  >
    <div class="space-y-4 pt-1 pb-2">
      <p class="text-sm font-regular dark:text-surface-0">
        {{ lessonTitle }}
      </p>

      <div class="relative">
        <InputText
          :value="shareUrl"
          readonly
          class="w-full text-xs sm:text-sm !rounded-xl !border-surface-100 dark:!border-surface-700 focus:!border-violet-500 pr-24 !py-6 !h-12"
        />
        <Button
          :label="t('common.actions.copy')"
          size="small"
          class="!absolute right-1 top-1 bottom-1 !px-3 !text-xs !rounded-lg !bg-violet-500 !border-violet-500 !text-white hover:!bg-violet-600 hover:!border-violet-600"
          @click="handleCopy"
        />
      </div>

      <div class="relative flex items-center justify-center my-2">
        <span class="px-3 text-xs text-surface-400 bg-surface-0 dark:bg-surface-900 z-10">
          {{ t("teacher.scenarios.detail.share.orVia") || "or share via" }}
        </span>
        <div class="absolute inset-x-0 h-px bg-surface-200 dark:bg-surface-700" />
      </div>

      <div class="space-y-2">
        <button
          v-for="option in shareOptions"
          :key="option.id"
          type="button"
          class="w-full flex items-center justify-between px-4 py-3 rounded-xl border border-surface-100 dark:border-surface-700 bg-surface-0 dark:bg-surface-900 transition-colors"
          :class="option.buttonClass"
          @click="emit(option.event)"
        >
          <div class="flex items-center gap-3">
            <div :class="option.iconWrapperClass">
              <Icon :name="option.iconName" :class="option.iconClass" />
            </div>

            <div v-if="option.hasSubtitle" class="text-left">
              <p class="text-sm font-semibold text-surface-900 dark:text-surface-0">
                {{ option.title }}
              </p>
              <p class="text-xs text-surface-500 dark:text-surface-400">
                {{ option.subtitle }}
              </p>
            </div>

            <p v-else class="text-sm font-semibold text-surface-900 dark:text-surface-0">
              {{ option.title }}
            </p>
          </div>

          <Icon v-if="option.id === 'sendToStudents'" name="solar:alt-arrow-right-linear" class="text-surface-300" />
        </button>
      </div>
    </div>
  </Dialog>
</template>
