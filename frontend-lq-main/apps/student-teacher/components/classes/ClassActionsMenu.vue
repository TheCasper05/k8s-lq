<script setup lang="ts">
  import { ref, computed } from "vue";
  import Menu from "primevue/menu";
  import type { MenuItem } from "primevue/menuitem";

  const props = defineProps<{
    classId: string;
  }>();

  const emit = defineEmits<{
    "edit": [classId: string];
    "duplicate": [classId: string];
    "favorite": [classId: string];
    "archive": [classId: string];
    "delete": [classId: string];
    "menu-show": [];
    "menu-hide": [];
  }>();

  const menuRef = ref<InstanceType<typeof Menu>>();
  const isMenuOpen = ref(false);

  const { t: $t } = useI18n();

  const menuItems = computed<MenuItem[]>(() => [
    {
      label: $t("classes.editClass"),
      icon: "solar:pen-line-duotone",
      command: () => {
        emit("edit", props.classId);
      },
      class: "text-surface-700 dark:text-surface-300",
    },
    {
      label: $t("classes.duplicate"),
      icon: "solar:copy-line-duotone",
      command: () => {
        emit("duplicate", props.classId);
      },
      class: "text-surface-700 dark:text-surface-300",
    },
    {
      label: $t("classes.addToFavorites"),
      icon: "solar:star-line-duotone",
      command: () => {
        emit("favorite", props.classId);
      },
      class: "text-surface-700 dark:text-surface-300",
    },
    {
      separator: true,
    },
    {
      label: $t("classes.archive"),
      icon: "solar:archive-line-duotone",
      command: () => {
        emit("archive", props.classId);
      },
      class: "text-surface-700 dark:text-surface-300",
    },
    {
      label: $t("classes.delete"),
      icon: "solar:trash-bin-trash-line-duotone",
      command: () => {
        emit("delete", props.classId);
      },
      class: "text-danger-600 dark:text-danger-400",
    },
  ]);

  const toggleMenu = (event: Event) => {
    event.stopPropagation();
    menuRef.value?.toggle(event);
  };

  const onMenuShow = () => {
    isMenuOpen.value = true;
    emit("menu-show");
  };

  const onMenuHide = () => {
    isMenuOpen.value = false;
    emit("menu-hide");
  };

  // Expose isMenuOpen so parent can use it for styling
  defineExpose({
    isMenuOpen,
  });
</script>

<template>
  <div class="relative">
    <slot :is-open="isMenuOpen" :toggle-menu="toggleMenu">
      <Button unstyled class="bg-surface-0 dark:bg-surface-900 rounded-lg pt-1 px-1" @click="toggleMenu">
        <template #icon>
          <Icon name="solar:menu-dots-line-duotone" size="24" class="text-surface-700 dark:text-surface-300" />
        </template>
      </Button>
    </slot>
    <Menu ref="menuRef" :model="menuItems" popup class="w-48" @show="onMenuShow" @hide="onMenuHide">
      <template #item="{ item, props: menuProps }">
        <a
          v-if="!item.separator"
          v-ripple
          v-bind="menuProps.action"
          :class="[
            'flex items-center gap-3 px-4 py-2 text-left hover:bg-surface-100 dark:hover:bg-surface-800 transition-colors',
            item.class,
          ]"
        >
          <Icon
            v-if="item.icon"
            :name="item.icon"
            :class="[
              item.label === $t('classes.editClass') ? 'text-primary-600 dark:text-primary-400' : '',
              item.label === $t('classes.duplicate') ? 'text-success-600 dark:text-success-400' : '',
              item.label === $t('classes.addToFavorites') ? 'text-warning-600 dark:text-warning-400' : '',
              item.label === $t('classes.archive') ? 'text-surface-600 dark:text-surface-400' : '',
            ]"
          />
          <span>{{ item.label }}</span>
        </a>
      </template>
    </Menu>
  </div>
</template>
