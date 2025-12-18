<script setup lang="ts">
  import { ref, watch, computed } from "vue";
  import { SUPPORTED_LOCALES } from "@lq/i18n/config";

  export interface PersonalInfo {
    firstName: string;
    lastName: string;
    email: string;
    nativeLanguage: string;
    learningLanguages: string[];
    bio: string;
  }

  export interface PersonalInfoSectionProps {
    user: PersonalInfo;
    editable?: boolean;
  }

  const props = withDefaults(defineProps<PersonalInfoSectionProps>(), {
    editable: false,
  });

  const emit = defineEmits<{
    "update:user": [user: PersonalInfo];
    "edit": [];
  }>();

  const localUser = ref({ ...props.user });

  watch(
    () => props.user,
    (newUser: PersonalInfo) => {
      localUser.value = { ...newUser };
    },
    { deep: true },
  );

  // Use system supported languages
  const availableLanguages = computed(() =>
    SUPPORTED_LOCALES.map((locale) => ({
      label: locale.name,
      value: locale.code,
      flag: locale.flag,
    })),
  );

  const updateField = (field: keyof PersonalInfo, value: string | string[] | undefined) => {
    if (value !== undefined) {
      (localUser.value[field] as string | string[]) = value;
      emit("update:user", localUser.value);
    }
  };

  const pcChip = {
    token: {
      class:
        "!flex !flex-row-reverse !items-center !gap-2 !bg-slate-100 dark:!bg-surface-800 !border !border-slate-200 dark:!border-surface-700 !rounded-full !py-1 !px-3",
    },
    tokenLabel: { class: "!text-sm !font-medium !text-slate-700 dark:!text-surface-200" },
    removeTokenIcon: {
      class: "!ml-0 !mr-0 !text-slate-500 !text-xs cursor-pointer hover:!text-slate-700",
    },
  };
</script>

<template>
  <div
    class="bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 p-6 shadow-sm"
  >
    <!-- Header with Edit Button -->
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-bold text-surface-900 dark:text-surface-100">{{ $t("profile.personalInfo") }}</h2>
      <Button
        v-if="!editable"
        :label="$t('profile.edit')"
        class="!bg-primary-600 !border-primary-600 hover:!bg-primary-700"
        rounded
        @click="$emit('edit')"
      >
        <template #icon>
          <Icon name="solar:pen-new-square-line-duotone" class="mr-2" />
        </template>
      </Button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- First Name -->
      <div>
        <label class="block text-sm font-medium text-surface-600 dark:text-surface-400 mb-2">
          {{ $t("profile.firstName") }}
        </label>
        <InputText
          v-model="localUser.firstName"
          class="w-full !rounded-xl"
          :disabled="!editable"
          @update:model-value="updateField('firstName', $event)"
        />
      </div>

      <!-- Last Name -->
      <div>
        <label class="block text-sm font-medium text-surface-600 dark:text-surface-400 mb-2">
          {{ $t("profile.lastName") }}
        </label>
        <InputText
          v-model="localUser.lastName"
          class="w-full !rounded-xl"
          :disabled="!editable"
          @update:model-value="updateField('lastName', $event)"
        />
      </div>

      <!-- Email -->
      <div class="md:col-span-2">
        <label class="block text-sm font-medium text-surface-600 dark:text-surface-400 mb-2">
          {{ $t("profile.email") }}
        </label>
        <InputText
          v-model="localUser.email"
          type="email"
          class="w-full !rounded-xl"
          :disabled="!editable"
          @update:model-value="updateField('email', $event)"
        />
      </div>

      <!-- Native Language -->
      <div>
        <label class="block text-sm font-medium text-surface-600 dark:text-surface-400 mb-2">
          {{ $t("profile.nativeLanguage") }}
        </label>
        <Dropdown
          v-model="localUser.nativeLanguage"
          :options="availableLanguages"
          option-label="label"
          option-value="value"
          :placeholder="$t('profile.selectLanguage')"
          class="w-full !rounded-xl"
          :pt="{
            root: { class: '!rounded-xl' },
            input: { class: '!rounded-xl' },
          }"
          :disabled="!editable"
          @update:model-value="updateField('nativeLanguage', $event)"
        >
          <template #value="slotProps">
            <div v-if="slotProps.value" class="flex items-center gap-2">
              <Icon :name="availableLanguages.find((l) => l.value === slotProps.value)?.flag || ''" class="text-lg" />
              <span>{{ availableLanguages.find((l) => l.value === slotProps.value)?.label }}</span>
            </div>
            <span v-else>{{ slotProps.placeholder }}</span>
          </template>
          <template #option="slotProps">
            <div class="flex items-center gap-2">
              <Icon :name="slotProps.option.flag" class="text-lg" />
              <span>{{ slotProps.option.label }}</span>
            </div>
          </template>
        </Dropdown>
      </div>

      <!-- Learning Languages -->
      <div>
        <label class="block text-sm font-medium text-surface-600 dark:text-surface-400 mb-2">
          {{ $t("profile.learningLanguages") }}
        </label>
        <MultiSelect
          v-model="localUser.learningLanguages"
          :options="availableLanguages"
          option-label="label"
          option-value="value"
          :placeholder="$t('profile.selectLanguages')"
          class="w-full"
          :pt="{
            root: { class: '!rounded-xl' },
            ...pcChip,
          }"
          :disabled="!editable"
          display="chip"
          @update:model-value="updateField('learningLanguages', $event)"
        >
          <template #option="slotProps">
            <div class="flex items-center gap-2">
              <Icon :name="slotProps.option.flag" class="text-lg" />
              <span>{{ slotProps.option.label }}</span>
            </div>
          </template>
        </MultiSelect>
      </div>

      <!-- Bio -->
      <div class="md:col-span-2">
        <label class="block text-sm font-medium text-surface-600 dark:text-surface-400 mb-2">
          {{ $t("profile.bio") }}
        </label>
        <Textarea
          v-model="localUser.bio"
          rows="4"
          class="w-full !rounded-xl"
          :placeholder="$t('profile.bioPlaceholder')"
          :disabled="!editable"
          @update:model-value="updateField('bio', $event)"
        />
      </div>
    </div>
  </div>
</template>
