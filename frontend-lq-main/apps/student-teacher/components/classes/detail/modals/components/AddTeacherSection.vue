<script setup lang="ts">
  import { ref, computed } from "vue";
  import { useI18n } from "vue-i18n";
  import IconField from "primevue/iconfield";
  import InputIcon from "primevue/inputicon";
  import { useEditClass } from "~/composables/classes/useEditClass";

  defineProps<{
    showAddTeacher?: boolean;
  }>();

  const emit = defineEmits<{
    add: [email: string];
    cancel: [];
  }>();

  const { teacherEmail, cancelAddTeacher, addTeacher: addTeacherToClass } = useEditClass();
  const email = teacherEmail;
  const emailError = ref<string>("");

  const emailRegex = /^[\w.%+-]+@[a-z0-9.-]+\.[a-z]{2,}$/i;

  const isEmailValid = computed(() => {
    if (!email.value.trim()) {
      return false;
    }
    return emailRegex.test(email.value);
  });

  const { t: $t } = useI18n();

  const handleAdd = () => {
    emailError.value = "";
    if (!email.value.trim()) {
      emailError.value = $t("classes.editModal.emailRequired");
      return;
    }
    if (!isEmailValid.value) {
      emailError.value = $t("classes.editModal.emailInvalid");
      return;
    }
    addTeacherToClass(email.value);
    emit("add", email.value);
    email.value = "";
  };

  const handleCancel = () => {
    emailError.value = "";
    cancelAddTeacher();
    emit("cancel");
  };
</script>

<template>
  <div v-if="showAddTeacher" class="bg-surface-50 dark:bg-surface-800 rounded-lg p-4 mt-3">
    <label class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
      {{ $t("classes.editModal.teacherEmail") }}
    </label>
    <div class="flex gap-3">
      <IconField class="flex-1">
        <InputIcon>
          <Icon name="solar:letter-line-duotone" />
        </InputIcon>
        <InputText
          v-model="email"
          type="email"
          class="w-full"
          :class="{ 'p-invalid': emailError }"
          @keyup.enter="handleAdd"
        />
      </IconField>
      <Button
        :label="$t('classes.createModal.add')"
        class="bg-primary-600 text-white border-0"
        :disabled="!isEmailValid"
        @click="handleAdd"
      />
      <Button :label="$t('common.cancel')" variant="outlined" severity="secondary" @click="handleCancel" />
    </div>
    <small v-if="emailError" class="p-error mt-1 block">
      {{ emailError }}
    </small>
  </div>
</template>
