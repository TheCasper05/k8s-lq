<script setup lang="ts">
  import { watch } from "vue";
  import { useAssignmentDetails } from "~/composables/classes/useAssignmentDetails";

  const props = defineProps<{
    visible: boolean;
  }>();

  const emit = defineEmits<{
    "update:visible": [value: boolean];
  }>();

  const { closeModal, viewPractice } = useAssignmentDetails();

  const handleClose = () => {
    closeModal();
    emit("update:visible", false);
  };

  const handleViewPractice = () => {
    viewPractice();
    emit("update:visible", false);
  };

  watch(
    () => props.visible,
    (newValue) => {
      if (!newValue) {
        closeModal();
      }
    },
  );
</script>

<template>
  <Dialog
    :visible="visible"
    modal
    closable
    :draggable="false"
    class="w-full max-w-4xl"
    :pt="{
      root: { class: '!rounded-xl' },
      header: { class: '!border-b-0 !pb-0' },
      content: { class: '!pt-0' },
    }"
    @update:visible="handleClose"
  >
    <template #header>
      <div class="flex items-center gap-4">
        <div class="bg-primary-100 dark:bg-primary-900/30 rounded-lg p-3">
          <Icon name="solar:document-text-line-duotone" class="text-2xl text-primary-600 dark:text-primary-400" />
        </div>
        <div class="flex flex-col flex-1">
          <h2 class="text-2xl font-bold text-surface-900 dark:text-surface-100">
            {{ $t("classes.assignments.detailsModal.title") }}
          </h2>
        </div>
      </div>
    </template>

    <div />

    <template #footer>
      <div class="flex items-center justify-end gap-3">
        <Button :label="$t('common.close')" variant="outlined" severity="secondary" @click="handleClose" />
        <Button
          :label="$t('classes.assignments.detailsModal.viewPractice')"
          class="bg-primary-600 text-white border-0"
          @click="handleViewPractice"
        >
          <template #icon>
            <Icon name="solar:eye-line-duotone" />
          </template>
        </Button>
      </div>
    </template>
  </Dialog>
</template>
