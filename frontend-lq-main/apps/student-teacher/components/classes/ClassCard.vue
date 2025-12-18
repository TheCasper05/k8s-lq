<script setup lang="ts">
  import type { Class } from "~/composables/classes/types";
  import { useClassColors } from "~/composables/classes/useClassColors";
  import ContentCard from "~/components/shared/ContentCard.vue";
  import CEFRBadge from "~/components/shared/CEFRBadge.vue";

  interface Props {
    classItem: Class;
  }

  interface TopActionConfig {
    id: string;
    icon: string;
    class: string;
    onClick: (event: MouseEvent) => void;
  }

  interface Emits {
    edit: [classId: string];
    duplicate: [classId: string];
    favorite: [classId: string];
    archive: [classId: string];
    delete: [classId: string];
    click: [classId: string];
  }

  const props = defineProps<Props>();
  const emit = defineEmits<Emits>();

  const { t } = useI18n();
  const { getStatusSeverity, getProgressSeverity } = useClassColors();
  const menu = ref();

  const menuItems = computed(() => [
    {
      label: t("common.actions.view"),
      icon: "solar:eye-line-duotone",
      class: "text-primary-500",
      command: () => emit("click", props.classItem.id),
    },
    {
      label: t("common.actions.edit"),
      icon: "solar:pen-new-square-line-duotone",
      class: "text-emerald-500",
      command: () => emit("edit", props.classItem.id),
    },
    {
      label: t("common.actions.duplicate"),
      icon: "solar:copy-line-duotone",
      class: "text-blue-500",
      command: () => emit("duplicate", props.classItem.id),
    },
    {
      separator: true,
    },
    {
      label: t("common.actions.archive"),
      icon: "solar:archive-down-minimlistic-line-duotone",
      class: "text-surface-500",
      command: () => emit("archive", props.classItem.id),
    },
    {
      label: t("common.actions.delete"),
      icon: "lucide:trash-2",
      class: "text-red-500",
      command: () => emit("delete", props.classItem.id),
    },
  ]);

  const toggleMenu = (event: Event) => {
    menu.value?.toggle(event);
  };

  const topActions = computed<TopActionConfig[]>(() => {
    const baseButtonClass =
      "w-9 h-9 rounded-xl bg-white/90 dark:bg-surface-800/90 backdrop-blur-sm shadow-sm flex items-center justify-center transition-colors hover:bg-white dark:hover:bg-surface-700";

    const favoriteClass = props.classItem.isFavorite
      ? `${baseButtonClass} text-amber-500`
      : `${baseButtonClass} text-surface-600 dark:text-surface-300 hover:text-amber-500 dark:hover:text-amber-400`;

    return [
      {
        id: "favorite",
        icon: props.classItem.isFavorite ? "solar:star-bold-duotone" : "solar:star-line-duotone",
        class: favoriteClass,
        onClick: () => emit("favorite", props.classItem.id),
      },
      {
        id: "menu",
        icon: "ant-design:more-outlined",
        class: `${baseButtonClass} text-surface-600 dark:text-surface-300 hover:text-primary-600 dark:hover:text-primary-400`,
        onClick: (event: MouseEvent) => toggleMenu(event),
      },
    ];
  });

  const getProgressDotClass = (progress: number) => {
    const severity = getProgressSeverity(progress);
    if (severity === "danger") return "bg-danger-500";
    if (severity === "warn") return "bg-warning-500";
    return "bg-success-500";
  };

  const getStatusColorClass = (status: string) => {
    const severity = getStatusSeverity(status);
    if (severity === "success") {
      return "bg-success-100 dark:bg-success-900/30 text-success-700 dark:text-success-400";
    } else if (severity === "danger") {
      return "bg-danger-100 dark:bg-danger-900/30 text-danger-700 dark:text-danger-400";
    }
    return "bg-surface-100 dark:bg-surface-800 text-surface-700 dark:text-surface-300";
  };

  const getStatusLabel = (status: string) => {
    if (status === "active") return "classes.active";
    if (status === "no-students") return "classes.noStudents";
    return "classes.inactive";
  };
</script>

<template>
  <ContentCard
    :cover-image="classItem.coverImage || undefined"
    :cover-alt="classItem.name"
    :show-default-icon="!classItem.coverImage"
    default-icon="solar:book-line-duotone"
    :top-actions="topActions"
    @click="$emit('click', classItem.id)"
  >
    <!-- CEFR Badge -->
    <template #cover-overlay>
      <div class="absolute bottom-3 left-3">
        <CEFRBadge :level="classItem.level as any" size="md" no-color />
      </div>
    </template>

    <!-- Title -->
    <template #title>
      <h3 class="text-lg font-bold text-surface-900 dark:text-surface-0 mb-3 leading-tight line-clamp-2">
        {{ classItem.name }}
      </h3>
    </template>

    <!-- Badges -->
    <template #badges>
      <div class="flex items-center gap-2 mb-4 flex-wrap">
        <!-- Status Badge -->
        <div
          :class="getStatusColorClass(classItem.status)"
          class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg border"
        >
          <span class="text-xs font-semibold">{{ $t(getStatusLabel(classItem.status)) }}</span>
        </div>

        <!-- Language Badge -->
        <div
          class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-surface-100 dark:bg-surface-800 border border-surface-200 dark:border-surface-700"
        >
          <img
            :src="`https://flagcdn.com/w20/${classItem.languageCode.toLowerCase()}.png`"
            :alt="classItem.language"
            class="w-4 h-3 object-cover rounded"
          />
          <span class="text-xs font-medium text-surface-900 dark:text-surface-100">{{ classItem.language }}</span>
        </div>
      </div>
    </template>

    <!-- Content -->
    <template #content>
      <div
        v-if="classItem.schedule"
        class="flex items-center gap-2 text-sm text-surface-600 dark:text-surface-400 bg-surface-100 dark:bg-surface-800 rounded-lg px-3 py-2 mb-4"
      >
        <Icon name="solar:calendar-line-duotone" class="text-lg" />
        <span>{{ classItem.schedule }}</span>
      </div>
    </template>

    <!-- Footer -->
    <template #footer>
      <div class="flex items-center justify-between">
        <!-- Students Count with Progress -->
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-2 text-surface-500 dark:text-surface-400">
            <Icon name="solar:users-group-rounded-linear" class="text-lg" />
            <span class="text-sm font-medium">{{ classItem.students }}</span>
          </div>
          <div v-if="classItem.students > 0" class="flex items-center gap-1.5">
            <span :class="getProgressDotClass(classItem.avgProgress)" class="w-2 h-2 rounded-full" />
            <span class="text-sm font-medium text-surface-600 dark:text-surface-400">{{ classItem.avgProgress }}%</span>
          </div>
        </div>

        <!-- Edit Button -->
        <Button
          unstyled
          class="!px-4 !py-1.5 !font-semibold rounded-full border border-surface-300 dark:border-surface-600 bg-transparent text-surface-700 dark:text-surface-200 transition-all duration-200 hover:bg-surface-100 dark:hover:bg-surface-800 hover:border-primary-500 dark:hover:border-primary-400 hover:border-[1.5px] flex items-center gap-2"
          @click.stop="$emit('edit', classItem.id)"
        >
          <Icon name="solar:pen-new-square-broken" class="text-primary-600 dark:text-primary-400 text-lg" />
          <span>{{ t("common.actions.edit") }}</span>
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
