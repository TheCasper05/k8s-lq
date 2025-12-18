<script setup lang="ts">
  import { ref, computed } from "vue";
  import { SUPPORTED_LOCALES } from "@lq/i18n/config";
  import type { CreateClassFormData, CreateClassErrors } from "~/composables/classes/useCreateClass";
  import Textarea from "primevue/textarea";
  import IconField from "primevue/iconfield";
  import InputIcon from "primevue/inputicon";
  import Message from "primevue/message";

  defineProps<{
    formData: CreateClassFormData;
    errors: CreateClassErrors;
  }>();

  const emit = defineEmits<{
    "update:formData": [data: Partial<CreateClassFormData>];
  }>();

  const fileInputRef = ref<HTMLInputElement | null>(null);
  const isDragging = ref(false);

  const levels = ["A1", "A2", "B1", "B2", "C1", "C2"];

  const availableLanguages = computed(() =>
    SUPPORTED_LOCALES.map((locale) => ({
      code: locale.code,
      name: locale.name,
      flag: locale.flag,
    })),
  );

  const updateField = (field: keyof CreateClassFormData, value: string | File | null) => {
    emit("update:formData", { [field]: value });
  };

  const openFileSelector = () => {
    fileInputRef.value?.click();
  };

  const handleFileSelect = (event: Event) => {
    const target = event.target as HTMLInputElement;
    const file = target.files?.[0];
    if (file && isValidImageType(file)) {
      const reader = new FileReader();
      reader.onload = (e) => {
        updateField("coverImagePreview", e.target?.result as string);
      };
      reader.readAsDataURL(file);
      updateField("coverImage", file);
    }
  };

  const handleDrop = (event: DragEvent) => {
    event.preventDefault();
    isDragging.value = false;
    const file = event.dataTransfer?.files[0];
    if (file && isValidImageType(file)) {
      const reader = new FileReader();
      reader.onload = (e) => {
        updateField("coverImagePreview", e.target?.result as string);
      };
      reader.readAsDataURL(file);
      updateField("coverImage", file);
    }
  };

  const handleDragOver = (event: DragEvent) => {
    event.preventDefault();
    isDragging.value = true;
  };

  const handleDragLeave = () => {
    isDragging.value = false;
  };

  const isValidImageType = (file: File): boolean => {
    const validTypes = [".jpg", ".jpeg", ".png", ".webp"];
    return validTypes.some((type) => file.name.toLowerCase().endsWith(type));
  };

  const removeImage = () => {
    updateField("coverImage", null);
    updateField("coverImagePreview", null);
    if (fileInputRef.value) {
      fileInputRef.value.value = "";
    }
  };

  const handleLanguageChange = (languageCode: string) => {
    const language = availableLanguages.value.find((l) => l.code === languageCode);
    if (language) {
      updateField("language", language.name);
      updateField("languageCode", language.code);
    }
  };
</script>

<template>
  <div class="flex flex-col gap-6 py-4">
    <!-- Cover Image -->
    <div>
      <label class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
        {{ $t("classes.createModal.coverImageOptional") }}
      </label>
      <div
        v-if="!formData.coverImagePreview"
        :class="[
          'border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center transition-all cursor-pointer',
          isDragging
            ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
            : 'border-surface-300 dark:border-surface-700 bg-surface-50 dark:bg-surface-800 hover:border-primary-400 dark:hover:border-primary-600',
        ]"
        @drop.prevent="handleDrop"
        @dragover.prevent="handleDragOver"
        @dragleave="handleDragLeave"
        @click="openFileSelector"
      >
        <div class="w-16 h-16 bg-primary-100 dark:bg-primary-900/30 rounded-xl flex items-center justify-center mb-4">
          <Icon name="solar:upload-line-duotone" class="text-2xl text-primary-600 dark:text-primary-400" />
        </div>
        <p class="text-sm font-medium text-surface-700 dark:text-surface-300 mb-1">
          {{ $t("classes.createModal.clickToUpload") }}
        </p>
        <p class="text-xs text-surface-500 dark:text-surface-500">{{ $t("classes.createModal.imageFormats") }}</p>
        <input
          ref="fileInputRef"
          type="file"
          accept="image/jpeg,image/png,image/webp"
          class="hidden"
          @change="handleFileSelect"
        />
      </div>
      <div v-else class="relative rounded-xl overflow-hidden border border-surface-200 dark:border-surface-700">
        <img :src="formData.coverImagePreview" alt="Cover preview" class="w-full h-48 object-cover" />
        <button
          type="button"
          class="absolute top-2 right-2 bg-danger-500 text-white rounded-lg p-2 hover:bg-danger-600 transition-colors"
          @click="removeImage"
        >
          <Icon name="solar:trash-bin-trash-line-duotone" />
        </button>
      </div>
    </div>

    <!-- Class Name -->
    <div>
      <label for="className" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
        {{ $t("classes.createModal.className") }} *
      </label>
      <InputText
        id="className"
        :model-value="formData.name"
        :placeholder="$t('classes.createModal.classNamePlaceholder')"
        class="w-full"
        :invalid="!!errors.name"
        @update:model-value="updateField('name', $event)"
      />
      <Message v-if="errors.name" severity="error" :closable="false" size="small" class="mt-1 block">
        {{ $t(errors.name) }}
      </Message>
    </div>

    <!-- Level and Language Row -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Level -->
      <div>
        <label for="level" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
          {{ $t("classes.createModal.level") }} *
        </label>
        <Select
          id="level"
          :model-value="formData.level"
          :options="levels"
          :placeholder="$t('classes.createModal.level')"
          class="w-full"
          :invalid="!!errors.level"
          @update:model-value="updateField('level', $event)"
        />
        <Message v-if="errors.level" severity="error" :closable="false" size="small" class="mt-1 block">
          {{ $t(errors.level) }}
        </Message>
      </div>

      <!-- Language -->
      <div>
        <label for="language" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
          {{ $t("classes.createModal.language") }} *
        </label>
        <Select
          id="language"
          :model-value="formData.languageCode"
          :options="availableLanguages"
          option-label="name"
          option-value="code"
          :placeholder="$t('classes.createModal.language')"
          class="w-full"
          :invalid="!!errors.language"
          @update:model-value="handleLanguageChange"
        >
          <template #value="{ value }">
            <div v-if="value" class="flex items-center gap-2">
              <Icon :name="availableLanguages.find((l) => l.code === value)?.flag || ''" class="text-lg" />
              <span>{{ availableLanguages.find((l) => l.code === value)?.name }}</span>
            </div>
            <span v-else>{{ $t("classes.createModal.language") }}</span>
          </template>
          <template #option="{ option }">
            <div class="flex items-center gap-2">
              <Icon :name="option.flag" class="text-lg" />
              <span>{{ option.name }}</span>
            </div>
          </template>
        </Select>
        <Message v-if="errors.language" severity="error" :closable="false" size="small" class="mt-1 block">
          {{ $t(errors.language) }}
        </Message>
      </div>
    </div>

    <!-- Description -->
    <div>
      <label for="description" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
        {{ $t("classes.createModal.descriptionOptional") }}
      </label>
      <Textarea
        id="description"
        :model-value="formData.description"
        :placeholder="$t('classes.createModal.descriptionPlaceholder')"
        rows="4"
        class="w-full"
        @update:model-value="updateField('description', $event)"
      />
    </div>

    <!-- Schedule -->
    <div>
      <label for="schedule" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
        {{ $t("classes.createModal.scheduleOptional") }}
      </label>
      <IconField class="w-full">
        <InputIcon>
          <Icon name="solar:calendar-line-duotone" />
        </InputIcon>
        <InputText
          id="schedule"
          :model-value="formData.schedule"
          :placeholder="$t('classes.createModal.schedulePlaceholder')"
          class="w-full"
          @update:model-value="updateField('schedule', $event)"
        />
      </IconField>
    </div>
  </div>
</template>
