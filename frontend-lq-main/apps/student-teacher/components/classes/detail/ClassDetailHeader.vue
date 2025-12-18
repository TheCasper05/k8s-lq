<script setup lang="ts">
  import { computed, watch } from "vue";
  import { useRouter } from "vue-router";
  import { useToast } from "primevue/usetoast";
  import { useBreakpoints, breakpointsTailwind } from "@vueuse/core";
  import { LqHero, LqAvatar, LqAvatarGroup } from "@lq/ui";
  import Button from "primevue/button";
  import type { Class } from "~/composables/classes/types";
  import type { Student } from "~/composables/students/types";
  import { useClassTeachers } from "~/composables/classes/useClassTeachers";

  interface Props {
    classDetail: Class | null;
    students?: Student[];
  }

  const props = withDefaults(defineProps<Props>(), {
    students: () => [],
  });

  const _emit = defineEmits<{
    "edit-class": [];
  }>();

  const _router = useRouter();
  const toast = useToast();
  const { t } = useI18n();
  const { teachers, fetchClassTeachers } = useClassTeachers();

  // Responsive variant: card on mobile/tablet, detailed on desktop
  const breakpoints = useBreakpoints(breakpointsTailwind);
  const isDesktop = breakpoints.greater("md"); // >= 768px
  const heroVariant = computed(() => (isDesktop.value ? "detailed" : "card"));

  // LqAvatarGroup handles the display limit internally

  // Get other teachers (excluding owner)
  const otherTeachers = computed(() => teachers.value.filter((t) => !t.isOwner));

  // Load teachers when classDetail changes
  watch(
    () => props.classDetail,
    (newClassDetail) => {
      if (newClassDetail) {
        fetchClassTeachers(newClassDetail);
      }
    },
    { immediate: true },
  );

  const getInitials = (firstName: string, lastName: string) => {
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
  };

  const getInitialsFromName = (name: string) => {
    const names = name.split(" ");
    if (names.length >= 2) {
      return `${names[0].charAt(0)}${names[1].charAt(0)}`.toUpperCase();
    }
    return names[0].charAt(0).toUpperCase();
  };

  const getOwnerInitials = () => {
    if (!props.classDetail?.ownerName) return "T";
    const names = props.classDetail.ownerName.split(" ");
    if (names.length >= 2) {
      return `${names[0].charAt(0)}${names[1].charAt(0)}`.toUpperCase();
    }
    return names[0].charAt(0).toUpperCase();
  };

  const copyStudentInviteLink = async () => {
    // TODO: Get actual invite link from API
    const inviteLink = `https://app.lingoquesto.com/invite/student/${props.classDetail?.id || ""}`;
    try {
      await navigator.clipboard.writeText(inviteLink);
      toast.add({
        severity: "success",
        summary: t("common.copied"),
        detail: t("classes.detail.studentInviteLinkCopied"),
        life: 3000,
      });
    } catch {
      toast.add({
        severity: "error",
        summary: t("common.error"),
        detail: t("classes.detail.failedToCopyInviteLink"),
        life: 3000,
      });
    }
  };

  const copyTeacherInviteLink = async () => {
    // TODO: Get actual invite link from API
    const inviteLink = `https://app.lingoquesto.com/invite/teacher/${props.classDetail?.id || ""}`;
    try {
      await navigator.clipboard.writeText(inviteLink);
      toast.add({
        severity: "success",
        summary: t("common.copied"),
        detail: t("classes.detail.teacherInviteLinkCopied"),
        life: 3000,
      });
    } catch {
      toast.add({
        severity: "error",
        summary: t("common.error"),
        detail: t("classes.detail.failedToCopyInviteLink"),
        life: 3000,
      });
    }
  };

  const handleUDBB = () => {
    // TODO: Implement UDBB functionality
    // UDBB clicked
  };
</script>

<template>
  <LqHero
    v-if="classDetail"
    :variant="heroVariant"
    :image="classDetail.coverImage || ''"
    :title="classDetail.name"
    @back="$router.back()"
  >
    <template #image-overlay>
      <div
        v-if="students.length > 0"
        class="absolute left-1/2 -translate-x-1/2 bottom-0 translate-y-1 z-10 flex justify-center"
      >
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
          avatar-class="border-2 border-white dark:border-surface-800 shadow-md bg-surface-100 dark:bg-surface-600 text-primary-700 dark:text-primary-300 text-xs"
        />
      </div>
    </template>

    <!-- Actions for card variant (mobile) -->
    <template v-if="!isDesktop" #actions>
      <div class="flex flex-col gap-2 w-full">
        <Button
          :label="t('common.actions.edit')"
          severity="secondary"
          outlined
          size="small"
          class="w-full text-xs sm:text-sm"
          @click="$emit('edit-class')"
        >
          <template #icon>
            <Icon name="solar:pen-line-duotone" class="text-base sm:text-lg" />
          </template>
        </Button>
        <Button
          :label="$t('classes.detail.copyStudentInviteLink')"
          severity="secondary"
          outlined
          size="small"
          class="w-full text-xs sm:text-sm"
          @click="copyStudentInviteLink"
        >
          <template #icon>
            <Icon name="solar:copy-line-duotone" class="text-base sm:text-lg" />
          </template>
        </Button>
        <Button
          :label="$t('classes.detail.copyTeacherInviteLink')"
          severity="secondary"
          outlined
          size="small"
          class="w-full text-xs sm:text-sm"
          @click="copyTeacherInviteLink"
        >
          <template #icon>
            <Icon name="solar:copy-line-duotone" class="text-base sm:text-lg" />
          </template>
        </Button>
        <Button
          :label="$t('classes.detail.udbb')"
          severity="secondary"
          outlined
          size="small"
          class="w-full text-xs sm:text-sm"
          @click="handleUDBB"
        >
          <template #icon>
            <Icon name="solar:document-text-line-duotone" class="text-base sm:text-lg" />
          </template>
        </Button>
      </div>
    </template>

    <!-- Navigation extra for detailed variant (desktop) -->
    <template v-else #navigation-extra>
      <Button
        unstyled
        class="bg-primary-600 dark:bg-primary-700 text-white px-2 pt-1 rounded-lg hover:bg-primary-700 dark:hover:bg-primary-800 transition-colors"
        @click="$emit('edit-class')"
      >
        <Icon name="solar:pen-line-duotone" class="text-md" />
      </Button>
    </template>

    <template #metadata>
      <div class="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3 justify-center md:justify-start">
        <div class="flex items-center gap-2 justify-center md:justify-start">
          <img
            :src="`https://flagcdn.com/w20/${classDetail.languageCode.toLowerCase()}.png`"
            :alt="classDetail.language"
            class="w-5 h-4 object-cover rounded"
          />
          <span class="text-sm text-surface-700 dark:text-surface-300">
            {{ classDetail.language }}
          </span>
        </div>
        <span class="hidden sm:inline text-primary-400 dark:text-primary-600 text-3xl">•</span>
        <span
          class="bg-info-100 dark:bg-info-900/30 text-info-700 dark:text-info-400 px-2 py-1 rounded-lg text-sm font-semibold w-fit mx-auto md:mx-0"
        >
          {{ classDetail.level }}
        </span>
      </div>
    </template>

    <template #info>
      <div class="flex items-center gap-2 justify-center md:justify-start">
        <Icon name="solar:users-group-rounded-line-duotone" class="text-primary-600 dark:text-primary-400 text-lg" />
        <span class="text-sm text-surface-600 dark:text-surface-400">
          {{ students.length }} {{ $t("students.students") }}
        </span>
      </div>
    </template>

    <template #sidebar>
      <div class="rounded-lg flex flex-col gap-3 sm:gap-4 mt-4 md:mt-0">
        <!-- Teachers Title -->
        <h3 class="text-sm font-semibold text-surface-900 dark:text-surface-100 text-left sm:text-right">
          {{ $t("classes.createModal.step2") }}:
        </h3>

        <!-- Owner/Teacher Info -->
        <div class="flex flex-col gap-3">
          <div class="flex justify-start sm:justify-end">
            <div class="flex gap-3">
              <LqAvatar
                :initials="getOwnerInitials()"
                shape="square"
                size="lg"
                avatar-class="bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300"
              />
              <div class="min-w-0 flex flex-col">
                <span class="font-semibold text-surface-900 dark:text-surface-100 truncate">
                  {{ classDetail.ownerName || t("classes.detail.teacher") }}
                </span>
                <span class="text-xs text-surface-600 dark:text-surface-400">
                  {{ $t("classes.createModal.owner") }}
                </span>
              </div>
            </div>
          </div>

          <!-- Other Teachers Avatar Group -->
          <div v-if="otherTeachers.length > 0" class="flex justify-start sm:justify-end">
            <div class="flex flex-col items-start sm:items-end gap-2">
              <span class="text-xs text-surface-600 dark:text-surface-400">
                {{ $t("classes.createModal.teachers") }}
              </span>
              <LqAvatarGroup
                :items="
                  otherTeachers.map((t) => ({
                    id: t.id,
                    src: t.photo || undefined,
                    initials: getInitialsFromName(t.name),
                  }))
                "
                size="md"
                avatar-class="border-2 border-white dark:border-surface-800 shadow-md bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 text-xs"
              />
            </div>
          </div>
        </div>

        <!-- Invite Link Buttons -->
        <div class="flex flex-col gap-2">
          <Button
            :label="$t('classes.detail.copyStudentInviteLink')"
            class="bg-surface-200 dark:bg-surface-700 text-surface-900 dark:text-surface-100 border-0 w-full justify-start hover:bg-surface-300 dark:hover:bg-surface-600 transition-colors text-xs sm:text-sm"
            size="small"
            @click="copyStudentInviteLink"
          >
            <template #icon>
              <Icon name="solar:copy-line-duotone" />
            </template>
          </Button>
          <Button
            :label="$t('classes.detail.copyTeacherInviteLink')"
            class="bg-surface-200 dark:bg-surface-700 text-surface-900 dark:text-surface-100 border-0 w-full justify-start hover:bg-surface-300 dark:hover:bg-surface-600 transition-colors text-xs sm:text-sm"
            size="small"
            @click="copyTeacherInviteLink"
          >
            <template #icon>
              <Icon name="solar:copy-line-duotone" />
            </template>
          </Button>
          <Button
            :label="$t('classes.detail.udbb')"
            class="bg-surface-200 dark:bg-surface-700 text-surface-900 dark:text-surface-100 border-0 w-full justify-start hover:bg-surface-300 dark:hover:bg-surface-600 transition-colors text-xs sm:text-sm"
            size="small"
            @click="handleUDBB"
          >
            <template #icon>
              <Icon name="solar:document-text-line-duotone" />
            </template>
          </Button>
        </div>
      </div>
    </template>
  </LqHero>
</template>
