<script setup lang="ts">
  import { ref, onMounted } from "vue";
  import type { Class } from "~/composables/classes/types";
  import { useClassColors } from "~/composables/classes/useClassColors";
  import { useClassStudents } from "~/composables/classes/useClassStudents";
  import { SUPPORTED_LOCALES } from "@lq/i18n/config";
  import { LqAvatarGroup } from "@lq/ui";
  import ClassActionsMenu from "./ClassActionsMenu.vue";
  import CEFRBadge from "~/components/shared/CEFRBadge.vue";

  const props = defineProps<{
    classItem: Class;
  }>();

  const emit = defineEmits<{
    edit: [classId: string];
    duplicate: [classId: string];
    favorite: [classId: string];
    archive: [classId: string];
    delete: [classId: string];
    click: [classId: string];
  }>();

  const { getStatusSeverity, getProgressSeverity } = useClassColors();
  // Create a local instance of the composable for this component
  const { students, fetchClassStudents } = useClassStudents();
  const menuRef = ref<InstanceType<typeof ClassActionsMenu>>();
  const isMenuOpen = ref(false);

  // LqAvatarGroup handles the display limit internally

  const getStatusColorClass = (status: string) => {
    const severity = getStatusSeverity(status);
    if (severity === "success") {
      return "bg-success-50 dark:bg-success-900/20 text-success-700 dark:text-success-400 border border-success-200 dark:border-success-800";
    } else if (severity === "danger") {
      return "bg-danger-50 dark:bg-danger-900/20 text-danger-700 dark:text-danger-400 border border-danger-200 dark:border-danger-800";
    }
    return "bg-surface-100 dark:bg-surface-800 text-surface-700 dark:text-surface-300";
  };

  const getProgressDotClass = (progress: number) => {
    const severity = getProgressSeverity(progress);
    if (severity === "danger") {
      return "bg-danger-500";
    } else if (severity === "warn") {
      return "bg-warning-500";
    }
    return "bg-success-500";
  };

  const getStatusLabel = (status: string) => {
    if (status === "active") return "classes.active";
    if (status === "no-students") return "classes.noStudents";
    return "classes.inactive";
  };

  const getLanguageFlag = (languageCode: string): string => {
    const locale = SUPPORTED_LOCALES.find((l) => l.code === languageCode.toLowerCase());
    return locale?.flag || "flag:us-4x3";
  };

  const getInitials = (firstName: string, lastName: string) => {
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
  };

  const handleItemClick = (event: MouseEvent) => {
    // Don't navigate if clicking on the menu or menu button
    const target = event.target as HTMLElement;
    if (target.closest(".p-menu") || target.closest("[data-menu-button]")) {
      return;
    }
    emit("click", props.classItem.id);
  };

  onMounted(() => {
    if (props.classItem.students > 0 && props.classItem.status === "active") {
      fetchClassStudents(props.classItem.id);
    }
  });
</script>

<template>
  <div
    :class="[
      'group bg-surface-0 dark:bg-surface-900 rounded-lg border border-surface-200 dark:border-surface-700 p-3 md:p-4 transition-all duration-200 flex flex-col sm:flex-row gap-3 md:gap-4 cursor-pointer hover:shadow-lg',
      isMenuOpen ? 'shadow-lg' : '',
    ]"
    @click="handleItemClick"
  >
    <!-- Thumbnail Image with Level Badge -->
    <div class="relative w-full sm:w-28 h-40 sm:h-28 flex-shrink-0 overflow-hidden rounded-lg">
      <img
        v-if="classItem.coverImage"
        :src="classItem.coverImage"
        :alt="classItem.name"
        class="w-full h-full object-cover"
      />
      <div
        v-else
        class="w-full h-full bg-gradient-to-br from-primary-100 to-primary-200 dark:from-primary-900 dark:to-primary-800 flex items-center justify-center"
      >
        <Icon name="solar:book-line-duotone" class="text-2xl text-primary-600 dark:text-primary-400" />
      </div>

      <!-- Level Badge - Absolute positioned in top-left corner -->
      <div class="absolute top-2 left-2">
        <CEFRBadge :level="classItem.level as any" size="sm" no-color />
      </div>
    </div>

    <!-- Content - 3 Rows -->
    <div class="flex-1 flex flex-col gap-2 min-w-0">
      <!-- Row 1: Title and Menu -->
      <div class="flex items-start justify-between gap-4">
        <h3 class="font-semibold text-lg text-surface-900 dark:text-surface-100 line-clamp-1 flex-1">
          {{ classItem.name }}
        </h3>
        <ClassActionsMenu
          ref="menuRef"
          :class-id="classItem.id"
          @edit="emit('edit', $event)"
          @duplicate="emit('duplicate', $event)"
          @favorite="emit('favorite', $event)"
          @archive="emit('archive', $event)"
          @delete="emit('delete', $event)"
          @menu-show="isMenuOpen = true"
          @menu-hide="isMenuOpen = false"
        >
          <template #default="{ toggleMenu }">
            <Button
              unstyled
              class="opacity-0 group-hover:opacity-100 transition-opacity duration-200 rounded-lg p-1 hover:bg-surface-100 dark:hover:bg-surface-800"
              data-menu-button
              @click="toggleMenu"
            >
              <template #icon>
                <Icon name="solar:menu-dots-line-duotone" size="20" class="text-surface-700 dark:text-surface-300" />
              </template>
            </Button>
          </template>
        </ClassActionsMenu>
      </div>

      <!-- Row 2: Calendar icon, Schedule, Flag -->
      <div class="flex items-center gap-2 text-sm text-surface-600 dark:text-surface-400">
        <Icon name="solar:calendar-line-duotone" size="18" />
        <span>{{ classItem.schedule || $t("classes.flexible") }}</span>
        <Icon :name="getLanguageFlag(classItem.languageCode)" class="text-base" />
      </div>

      <!-- Row 3: Users icon, Student count, Badge (dot), Percentage, Status tag -->
      <div class="flex items-center gap-3 flex-wrap">
        <!-- Students -->
        <div class="flex items-center gap-1.5 text-sm text-surface-700 dark:text-surface-300">
          <Icon name="solar:users-group-rounded-line-duotone" size="18" />
          <span class="font-medium">{{ classItem.students }}</span>
        </div>

        <!-- Badge (dot) and Percentage (only show if students > 0) -->
        <div v-if="classItem.students > 0" class="flex items-center gap-1.5">
          <span :class="[getProgressDotClass(classItem.avgProgress), 'w-2 h-2 rounded-full']" />
          <span class="text-sm text-surface-600 dark:text-surface-400 font-medium">
            {{ classItem.avgProgress }}% avg
          </span>
        </div>

        <!-- Status Badge -->
        <div>
          <span :class="getStatusColorClass(classItem.status)" class="rounded-full px-3 py-1 text-xs font-medium">
            {{ $t(getStatusLabel(classItem.status)) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Avatar Group (Right side) -->
    <div v-if="classItem.students > 0 && classItem.status === 'active'" class="flex-shrink-0 flex items-center">
      <LqAvatarGroup
        :items="
          students.map((s) => ({
            id: s.id,
            src: s.photo || undefined,
            initials: getInitials(s.firstName, s.lastName),
          }))
        "
        :max-display="3"
        size="md"
        avatar-class="border-2 border-white dark:border-surface-800"
      />
    </div>
  </div>
</template>
