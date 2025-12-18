<script setup lang="ts">
  import type { Activity } from "~/types/activities";

  interface Props {
    activity: Activity;
  }

  interface Emits {
    detail: [id: string];
    assign: [activity: Activity];
    edit: [activity: Activity];
    delete: [id: string];
    archive: [id: string];
    share: [activity: Activity];
    toggleFavorite: [id: string];
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

  const quickActions = computed(() => [
    {
      id: "share",
      icon: "solar:share-line-duotone",
      class:
        "size-8 rounded-lg flex items-center justify-center text-surface-400 hover:text-primary-600 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors",
      title: t("common.actions.share"),
      onClick: () => emit("share", props.activity),
    },
    {
      id: "favorite",
      icon: props.activity.isFavorite ? "solar:star-bold" : "solar:star-linear",
      class:
        "size-8 rounded-lg flex items-center justify-center transition-colors " +
        (props.activity.isFavorite
          ? "text-amber-500 bg-amber-50 dark:bg-amber-900/10"
          : "text-surface-400 hover:text-amber-500 hover:bg-amber-50 dark:hover:bg-amber-900/20"),
      title: t("teacher.scenarios.addToFavorites"),
      onClick: () => emit("toggleFavorite", props.activity.id),
    },
  ]);
</script>

<template>
  <div class="flex items-center justify-end gap-1">
    <!-- Quick Actions: Share & Favorite -->
    <Button
      v-for="action in quickActions"
      :key="action.id"
      unstyled
      :class="action.class"
      :title="action.title"
      @click="action.onClick()"
    >
      <Icon :name="action.icon" class="text-lg" />
    </Button>

    <!-- Menu Button -->
    <Button
      unstyled
      class="size-8 rounded-lg flex items-center justify-center text-surface-400 hover:text-primary-600 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors"
      :title="t('common.actions.more') || 'Más opciones'"
      @click="toggleMenu"
    >
      <Icon name="ant-design:more-outlined" class="text-lg" />
    </Button>

    <!-- Context Menu -->
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
  </div>
</template>
