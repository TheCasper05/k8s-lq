<script setup lang="ts">
  import type { Class } from "~/composables/classes/types";
  import ClassListItem from "./ClassListItem.vue";

  defineProps<{
    classes: Class[];
  }>();

  const emit = defineEmits<{
    edit: [classId: string];
    duplicate: [classId: string];
    favorite: [classId: string];
    archive: [classId: string];
    delete: [classId: string];
    click: [classId: string];
  }>();

  type ActionType = "edit" | "duplicate" | "favorite" | "archive" | "delete" | "click";

  const handleAction = (action: ActionType, classId: string) => {
    switch (action) {
      case "edit":
        emit("edit", classId);
        break;
      case "duplicate":
        emit("duplicate", classId);
        break;
      case "favorite":
        emit("favorite", classId);
        break;
      case "archive":
        emit("archive", classId);
        break;
      case "delete":
        emit("delete", classId);
        break;
      case "click":
        emit("click", classId);
        break;
    }
  };
</script>

<template>
  <div v-if="classes.length > 0" class="flex flex-col gap-4">
    <ClassListItem
      v-for="classItem in classes"
      :key="classItem.id"
      :class-item="classItem"
      @edit="handleAction('edit', $event)"
      @duplicate="handleAction('duplicate', $event)"
      @favorite="handleAction('favorite', $event)"
      @archive="handleAction('archive', $event)"
      @delete="handleAction('delete', $event)"
      @click="handleAction('click', $event)"
    />
  </div>
  <div v-else class="flex flex-col items-center justify-center py-12 text-center">
    <Icon name="solar:book-line-duotone" class="text-6xl text-surface-300 dark:text-surface-700 mb-4" />
    <p class="text-lg font-semibold text-surface-600 dark:text-surface-400 mb-2">
      {{ $t("classes.noClassesFound") }}
    </p>
    <p class="text-sm text-surface-500 dark:text-surface-500">
      {{ $t("classes.noClassesDescription") }}
    </p>
  </div>
</template>
