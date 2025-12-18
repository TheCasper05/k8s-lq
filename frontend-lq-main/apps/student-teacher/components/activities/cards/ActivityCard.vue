<script setup lang="ts">
  import type { Activity } from "~/types/activities";
  import ContentCard from "~/components/shared/ContentCard.vue";
  import CEFRBadge from "~/components/shared/CEFRBadge.vue";

  interface Props {
    activity: Activity;
  }

  interface TopActionConfig {
    id: string;
    icon: string;
    class: string;
    onClick: (event: MouseEvent) => void;
  }

  interface Emits {
    detail: [id: string];
    edit: [activity: Activity];
    delete: [id: string];
    toggleFavorite: [id: string];
    share: [activity: Activity];
    assign: [activity: Activity];
    archive: [id: string];
  }

  const props = defineProps<Props>();
  const emit = defineEmits<Emits>();

  const { t } = useI18n();

  const menu = ref();

  const menuItems = computed(() => [
    {
      label: t("common.actions.view"),
      icon: "solar:eye-line-duotone",
      class: "text-primary-500",
      command: () => emit("detail", props.activity.id),
    },
    {
      label: t("common.actions.assign"),
      icon: "solar:user-plus-line-duotone",
      class: "text-blue-500",
      command: () => emit("assign", props.activity),
    },
    {
      label: t("common.actions.edit"),
      icon: "solar:pen-new-square-line-duotone",
      class: "text-emerald-500",
      command: () => emit("edit", props.activity),
    },
    {
      separator: true,
    },
    {
      label: t("common.actions.delete"),
      icon: "lucide:trash-2",
      class: "text-red-500",
      command: () => emit("delete", props.activity.id),
    },
    {
      label: t("common.actions.archive"),
      icon: "solar:archive-down-minimlistic-line-duotone",
      class: "text-surface-500",
      command: () => emit("archive", props.activity.id),
    },
  ]);

  const toggleMenu = (event: Event) => {
    menu.value?.toggle(event);
  };

  const topActions = computed<TopActionConfig[]>(() => {
    const baseButtonClass =
      "w-9 h-9 rounded-xl bg-white/90 dark:bg-surface-800/90 backdrop-blur-sm shadow-sm flex items-center justify-center transition-colors hover:bg-white dark:hover:bg-surface-700";

    const favoriteClass = props.activity.isFavorite
      ? `${baseButtonClass} text-amber-500`
      : `${baseButtonClass} text-surface-600 dark:text-surface-300 hover:text-amber-500 dark:hover:text-amber-400`;

    return [
      {
        id: "share",
        icon: "solar:share-line-duotone",
        class: `${baseButtonClass} text-surface-600 dark:text-surface-300 hover:text-primary-600 dark:hover:text-primary-400`,
        onClick: () => emit("share", props.activity),
      },
      {
        id: "favorite",
        icon: props.activity.isFavorite ? "solar:star-bold-duotone" : "solar:star-line-duotone",
        class: favoriteClass,
        onClick: () => emit("toggleFavorite", props.activity.id),
      },
      {
        id: "menu",
        icon: "ant-design:more-outlined",
        class: `${baseButtonClass} text-surface-600 dark:text-surface-300 hover:text-primary-600 dark:hover:text-primary-400`,
        onClick: (event: MouseEvent) => toggleMenu(event),
      },
    ];
  });
</script>

<template>
  <ContentCard
    :cover-image="activity.coverImage"
    :cover-alt="activity.title"
    :top-actions="topActions"
    @click="$emit('detail', activity.id)"
  >
    <!-- CEFR Badge -->
    <template #cover-overlay>
      <div class="absolute bottom-3 left-3">
        <CEFRBadge :level="activity.level" size="md" no-color />
      </div>
    </template>

    <!-- Title -->
    <template #title>
      <h3 class="text-lg font-bold text-surface-900 dark:text-surface-0 mb-3 leading-tight line-clamp-2">
        {{ activity.title }}
      </h3>
    </template>

    <!-- Badges -->
    <template #badges>
      <div class="flex items-center gap-2 mb-4 flex-wrap">
        <!-- AI Role Badge -->
        <div
          class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-gradient-to-r from-purple-50 to-violet-50 dark:from-purple-900/20 dark:to-violet-900/20 border border-purple-200 dark:border-purple-700/50"
        >
          <Icon name="lucide:bot-message-square" class="text-purple-600 dark:text-purple-400 text-sm" />
          <span class="text-xs font-semibold text-purple-700 dark:text-purple-300">AI:</span>
          <span class="text-xs font-medium text-purple-900 dark:text-purple-100">{{ activity.aiAssistantRole }}</span>
        </div>

        <!-- Student Role Badge -->
        <div
          class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 border border-blue-200 dark:border-blue-700/50"
        >
          <Icon name="solar:user-circle-line-duotone" class="text-blue-600 dark:text-blue-400 text-sm" />
          <span class="text-xs font-semibold text-blue-700 dark:text-blue-300">Student:</span>
          <span class="text-xs font-medium text-blue-900 dark:text-blue-100">{{ activity.studentRole }}</span>
        </div>
      </div>
    </template>

    <!-- Footer -->
    <template #footer>
      <div class="flex items-center justify-between">
        <!-- Classes Count -->
        <div class="flex items-center gap-2 text-surface-500 dark:text-surface-400">
          <Icon name="solar:users-group-rounded-linear" class="text-lg" />
          <span class="text-sm font-medium">
            {{ activity.assignedClasses }} {{ t("teacher.dashboard.stats.classrooms") }}
          </span>
        </div>

        <!-- Assign Button -->
        <Button
          unstyled
          class="!px-4 !py-1.5 !font-semibold rounded-full border border-surface-300 dark:border-surface-600 bg-transparent text-surface-700 dark:text-surface-200 transition-all duration-200 hover:bg-surface-100 dark:hover:bg-surface-800 hover:border-primary-500 dark:hover:border-primary-400 hover:border-[1.5px] flex items-center gap-2"
          @click.stop="$emit('assign', activity)"
        >
          <Icon name="solar:user-plus-broken" class="text-primary-600 dark:text-primary-400 text-lg" />
          <span>{{ t("teacher.scenarios.assign") }}</span>
        </Button>
      </div>
    </template>

    <!-- Context Menu -->
    <template #menu>
      <Menu ref="menu" :model="menuItems" popup class="!rounded-xl !shadow-xl !border-0 !p-1.5">
        <template #item="{ item, props: propsItems }">
          <a
            v-bind="propsItems.action"
            class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-surface-100 dark:hover:bg-surface-800 transition-colors"
          >
            <Icon :name="item.icon as string" :class="item.class" class="text-lg" />
            <span class="font-medium">{{ item.label }}</span>
          </a>
        </template>
      </Menu>
    </template>
  </ContentCard>
</template>
