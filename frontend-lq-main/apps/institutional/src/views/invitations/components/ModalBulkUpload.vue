<script setup lang="ts">
  import { ref } from "vue";
  import Dialog from "primevue/dialog";
  import Button from "primevue/button";
  import { Icon } from "@iconify/vue";
  import { downloadInvitationTemplate } from "../utils/utils";

  const props = defineProps<{
    visible: boolean;
    loading?: boolean;
  }>();

  const emit = defineEmits<{
    (e: "update:visible", value: boolean): void;
    (e: "submit", file: File): void;
  }>();

  const fileInputRef = ref<HTMLInputElement | null>(null);
  const selectedFile = ref<File | null>(null);
  const isDragging = ref(false);

  function onCancel(): void {
    selectedFile.value = null;
    emit("update:visible", false);
  }

  function openFileSelector(): void {
    fileInputRef.value?.click();
  }

  function handleFileSelect(event: Event): void {
    const target = event.target as HTMLInputElement;
    const file = target.files?.[0];
    if (file) {
      selectedFile.value = file;
    }
  }

  function handleDrop(event: DragEvent): void {
    isDragging.value = false;
    const file = event.dataTransfer?.files[0];
    if (file && isValidFileType(file)) {
      selectedFile.value = file;
    }
  }

  function handleDragOver(event: DragEvent): void {
    event.preventDefault();
    isDragging.value = true;
  }

  function handleDragLeave(): void {
    isDragging.value = false;
  }

  function isValidFileType(file: File): boolean {
    const validTypes = [".csv", ".xlsx", ".xls"];
    return validTypes.some((type) => file.name.toLowerCase().endsWith(type));
  }

  function onSubmit(): void {
    if (selectedFile.value && !props.loading) {
      emit("submit", selectedFile.value);
      selectedFile.value = null;
    }
  }
</script>

<template>
  <Dialog
    :visible="visible"
    modal
    :header="$t('invitations.bulkUpload.title')"
    closable
    :style="{ width: '680px', maxWidth: '100%' }"
    @update:visible="$emit('update:visible', $event)"
  >
    <div class="flex flex-col gap-6">
      <p class="text-surface-600 text-sm">
        {{ $t("invitations.bulkUpload.subtitle") }}
      </p>

      <!-- Formato del Archivo Section -->
      <div class="bg-primary-50 rounded-2xl p-6 border-2 border-primary-200">
        <div class="flex items-start gap-4 mb-6">
          <div class="w-12 h-12 bg-primary-500 rounded-xl flex items-center justify-center shrink-0">
            <Icon icon="solar:document-line-duotone" class="text-white text-xl" />
          </div>
          <div class="flex-1 flex items-center justify-between">
            <div>
              <h3 class="font-bold text-lg mb-2 text-surface-900">
                {{ $t("invitations.bulkUpload.fileFormat.title") }}
              </h3>
              <p class="text-sm text-surface-600 mb-4">
                {{ $t("invitations.bulkUpload.fileFormat.description") }}
              </p>
            </div>
            <Button
              type="button"
              :label="$t('invitations.bulkUpload.downloadTemplate')"
              unstyled
              class="bg-primary-500 text-white flex gap-2 items-center justify-center px-4 py-2 rounded-xl border-2 border-primary-500 shadow-md hover:bg-primary-600 transition-all"
              @click="downloadInvitationTemplate"
            >
              <template #icon>
                <Icon icon="solar:download-line-duotone" />
              </template>
            </Button>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="flex items-start gap-3">
            <div
              class="w-8 h-8 bg-primary-500 text-white rounded-full flex items-center justify-center shrink-0 font-bold text-sm"
            >
              1
            </div>
            <div>
              <p class="font-semibold text-sm text-surface-900">
                {{ $t("invitations.bulkUpload.fileFormat.step1.title") }}
              </p>
              <p class="text-xs text-surface-600">
                {{ $t("invitations.bulkUpload.fileFormat.step1.description") }}
              </p>
            </div>
          </div>

          <div class="flex items-start gap-3">
            <div
              class="w-8 h-8 bg-primary-500 text-white rounded-full flex items-center justify-center shrink-0 font-bold text-sm"
            >
              2
            </div>
            <div>
              <p class="font-semibold text-sm text-surface-900">
                {{ $t("invitations.bulkUpload.fileFormat.step2.title") }}
              </p>
              <p class="text-xs text-surface-600">
                {{ $t("invitations.bulkUpload.fileFormat.step2.description") }}
              </p>
            </div>
          </div>

          <div class="flex items-start gap-3">
            <div
              class="w-8 h-8 bg-primary-500 text-white rounded-full flex items-center justify-center shrink-0 font-bold text-sm"
            >
              3
            </div>
            <div>
              <p class="font-semibold text-sm text-surface-900">
                {{ $t("invitations.bulkUpload.fileFormat.step3.title") }}
              </p>
              <p class="text-xs text-surface-600">
                {{ $t("invitations.bulkUpload.fileFormat.step3.description") }}
              </p>
            </div>
          </div>

          <div class="flex items-start gap-3">
            <div
              class="w-8 h-8 bg-primary-500 text-white rounded-full flex items-center justify-center shrink-0 font-bold text-sm"
            >
              4
            </div>
            <div>
              <p class="font-semibold text-sm text-surface-900">
                {{ $t("invitations.bulkUpload.fileFormat.step4.title") }}
              </p>
              <p class="text-xs text-surface-600">
                {{ $t("invitations.bulkUpload.fileFormat.step4.description") }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Drag & Drop Area -->
      <div
        :class="[
          'border-2 border-dashed rounded-2xl p-12 flex flex-col items-center justify-center transition-all cursor-pointer',
          isDragging ? 'border-primary-500 bg-primary-50' : 'border-surface-300 bg-surface-50 hover:border-primary-400',
        ]"
        @drop.prevent="handleDrop"
        @dragover.prevent="handleDragOver"
        @dragleave="handleDragLeave"
        @click="openFileSelector"
      >
        <div class="w-20 h-20 bg-primary-100 rounded-2xl flex items-center justify-center mb-4">
          <Icon icon="solar:upload-line-duotone" class="text-primary-600 text-3xl" />
        </div>

        <h4 class="text-lg font-bold text-surface-900 mb-2">
          {{ selectedFile ? selectedFile.name : $t("invitations.bulkUpload.dragDrop.title") }}
        </h4>
        <p class="text-sm text-surface-600 mb-4">
          {{ $t("invitations.bulkUpload.dragDrop.subtitle") }}
        </p>
        <Button
          type="button"
          :label="$t('invitations.bulkUpload.selectFile')"
          unstyled
          class="bg-primary-500 text-white flex gap-2 items-center justify-center px-6 py-3 rounded-xl font-semibold shadow-lg hover:bg-primary-600 transition-all"
          @click.stop="openFileSelector"
        >
          <template #icon>
            <Icon icon="solar:upload-line-duotone" />
          </template>
        </Button>

        <p class="text-xs text-surface-500 mt-4">
          {{ $t("invitations.bulkUpload.supportedFormats") }}
        </p>

        <input ref="fileInputRef" type="file" accept=".csv,.xlsx,.xls" class="hidden" @change="handleFileSelect" />
      </div>

      <!-- Action Buttons -->
      <div class="flex justify-between gap-3">
        <Button
          type="button"
          :label="$t('common.cancel')"
          severity="danger"
          class="w-1/2"
          :disabled="loading"
          @click="onCancel"
        />
        <Button
          :label="$t('invitations.bulkUpload.uploadButton')"
          :severity="selectedFile ? undefined : 'secondary'"
          :unstyled="!!selectedFile"
          :disabled="loading || !selectedFile"
          :loading="loading"
          :class="
            selectedFile && !loading
              ? 'bg-primary-500 text-white! px-3! py-2! rounded-2xl border-2 border-primary-500 shadow-[0_4px_6px_-4px_rgba(0,0,0,0.1),0_10px_15px_-3px_rgba(0,0,0,0.1)] w-1/2'
              : 'w-1/2'
          "
          @click="onSubmit"
        />
      </div>
    </div>
  </Dialog>
</template>
