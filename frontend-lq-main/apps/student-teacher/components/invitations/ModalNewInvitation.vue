<template>
  <Dialog
    :visible="visible"
    modal
    :header="$t('invitations.newInvitation')"
    closable
    :style="{ width: '640px', maxWidth: '100%' }"
    @update:visible="$emit('update:visible', $event)"
  >
    <form class="flex flex-col gap-5" @submit.prevent="handleSubmit">
      <div class="flex flex-col gap-2">
        <label class="font-medium text-sm">{{ $t("invitations.form.guestEmails") }} *</label>

        <div
          v-if="dataDto.emails.length"
          class="flex flex-wrap items-center gap-2 min-h-13 border-2 border-surface-200 rounded-2xl bg-primary-50 p-2"
        >
          <Chip
            v-for="(email, index) in dataDto.emails"
            :key="email"
            :label="email"
            removable
            class="px-2 py-1 border border-primary-200 bg-white flex items-center gap-2 rounded-xl text-primary-600 shadow"
            unstyled
            @remove="removeEmail(index)"
          >
            <template #icon>
              <Icon name="solar:letter-line-duotone" />
            </template>
          </Chip>
        </div>

        <div class="flex items-stretch gap-2">
          <InputText
            v-model="newEmail"
            :placeholder="$t('invitations.form.emailPlaceholder')"
            class="flex-1"
            :invalid="!!(emailError && newEmail)"
            @keydown.enter.prevent="addEmail"
            @blur="validateEmail"
          />

          <Button type="button" severity="secondary" class="rounded-2xl px-3! py-1!" @click="addEmail">
            <template #icon>
              <Icon name="solar:add-circle-line-duotone" />
            </template>
          </Button>
        </div>
        <Message v-if="emailError && newEmail" severity="error" size="small" variant="simple">
          {{ emailError }}
        </Message>

        <small class="text-xs text-surface-500">
          {{ emailsCountLabel }}
        </small>
      </div>

      <div class="flex flex-col gap-2">
        <label class="font-medium text-sm">{{ $t("invitations.form.workspace") }} *</label>
        <Select
          v-model="workspaceValue"
          :options="workspaces"
          option-label="name"
          option-value="id"
          :placeholder="$t('invitations.form.workspacePlaceholder')"
          filter
          show-clear
          class="w-full"
          :invalid="!!workspaceError"
          @blur="validateWorkspace"
        />
        <Message v-if="workspaceError" severity="error" size="small" variant="simple">
          {{ workspaceError }}
        </Message>
      </div>

      <div class="flex flex-col gap-2">
        <label class="font-medium text-sm">{{ $t("invitations.form.role") }} *</label>

        <div class="flex flex-wrap gap-2">
          <Button
            v-for="role in roles"
            :key="role.value"
            :label="role.label"
            unstyled
            :pt:root="{
              class:
                roleValue === role.value
                  ? 'bg-primary-500 text-white px-3 py-2 rounded-2xl border-2 border-primary-500 shadow-[0_4px_6px_-4px_rgba(0,0,0,0.1),0_10px_15px_-3px_rgba(0,0,0,0.1)]'
                  : 'border-2 border-primary-200 px-3 py-2 rounded-2xl',
            }"
            @click="roleValue = role.value"
          />
        </div>
      </div>

      <div v-if="hasClassrooms" class="flex flex-col gap-2">
        <div class="flex items-center gap-2 text-sm">
          <span class="font-medium">{{ $t("invitations.form.classrooms") }}</span>
          <span class="text-surface-500 text-xs">{{ $t("invitations.form.classroomsOptional") }}</span>
        </div>

        <div class="flex flex-wrap gap-2">
          <Button
            v-for="classroom in classroomOptions"
            :key="classroom.value"
            :label="classroom.label"
            unstyled
            :class="
              dataDto.classrooms.includes(classroom.value)
                ? 'bg-primary-500 text-white! px-3! py-2! rounded-2xl border-2 border-primary-500 shadow-[0_4px_6px_-4px_rgba(0,0,0,0.1),0_10px_15px_-3px_rgba(0,0,0,0.1)]'
                : 'border-2 border-primary-200 px-3! py-2! rounded-2xl'
            "
            @click="toggleClassroom(classroom.value)"
          />
        </div>
      </div>

      <div class="flex flex-col gap-2">
        <div class="flex items-center gap-2 text-sm">
          <span class="font-medium">{{ $t("invitations.form.welcomeMessage") }}</span>
          <span class="text-surface-500 text-xs">{{ $t("invitations.form.welcomeMessageOptional") }}</span>
        </div>

        <Textarea
          v-model="dataDto.welcomeMessage"
          auto-resize
          rows="3"
          :placeholder="$t('invitations.form.welcomeMessagePlaceholder')"
          class="w-full"
        />
      </div>

      <Message
        unstyled
        :closable="false"
        class="w-full font-normal text-sm text-surface-600 bg-surface-50 p-3 rounded-2xl border border-surface-200"
      >
        {{ $t("invitations.form.info") }}
      </Message>

      <div class="flex flex-col gap-3 w-full">
        <div class="flex justify-between gap-3">
          <Button type="button" :label="$t('common.cancel')" severity="danger" class="w-1/2" @click="onCancel" />
          <Button
            type="submit"
            :label="sendButtonLabel"
            :severity="isValidFormFull ? undefined : 'secondary'"
            :unstyled="isValidFormFull"
            :disabled="loading || !isValidFormFull"
            :loading="loading"
            :class="
              isValidFormFull && !loading
                ? 'bg-primary-500 text-white! px-3! py-2! rounded-2xl border-2 border-primary-500 shadow-[0_4px_6px_-4px_rgba(0,0,0,0.1),0_10px_15px_-3px_rgba(0,0,0,0.1)] w-1/2'
                : 'w-1/2'
            "
          />
        </div>
      </div>
    </form>
  </Dialog>
</template>

<script setup lang="ts">
  import { computed, ref, watch } from "vue";
  import { useQuery } from "@vue/apollo-composable";
  import { useField, useForm } from "vee-validate";
  import { toTypedSchema } from "@vee-validate/zod";
  import { z } from "zod";
  import { InvitationRole } from "~/utils/invitations/constants";
  import type { WorkspaceOption, RoleOption, ClassroomOption, InvitationDto } from "~/utils/invitations/types";
  import { SEARCH_WORKSPACES, SEARCH_CLASSROOMS, type CreateInvitationInput } from "@lq/graphql";
  import { useAuthStore } from "@lq/stores";

  const { t } = useI18n();
  const authStore = useAuthStore();

  const props = defineProps<{
    visible: boolean;
    loading?: boolean;
  }>();

  const emit = defineEmits<{
    (e: "update:visible", value: boolean): void;
    (e: "submit", payload: Array<CreateInvitationInput>): void;
  }>();

  const dataDto = ref<InvitationDto>({
    emails: [],
    workspace: null,
    role: InvitationRole.STUDENT,
    classrooms: [],
    welcomeMessage: "",
  });

  const newEmail = ref("");

  // Validation schema (reactive)
  const schema = computed(() =>
    toTypedSchema(
      z.object({
        email: z
          .union([z.string().email(t("invitations.form.emailInvalid")), z.literal("")])
          .optional()
          .refine((email) => (email ? !dataDto.value.emails.includes(email.trim()) : true), {
            message: t("invitations.form.emailDuplicate"),
          }),
        workspace: z.string().min(1, t("invitations.messages.validationWorkspace")),
        role: z.string().min(1, t("invitations.messages.validationRole")),
      }),
    ),
  );

  // Vee-validate setup
  const { handleSubmit: veeHandleSubmit, meta } = useForm({
    validationSchema: schema,
  });

  const { value: emailValue, errorMessage: emailError } = useField<string>("email");
  const { value: workspaceValue, errorMessage: workspaceError } = useField<string>("workspace");
  const { value: roleValue } = useField<string>("role");

  // Sync refs with vee-validate
  watch(newEmail, (val) => {
    emailValue.value = val;
  });

  watch(emailValue, (val) => {
    newEmail.value = val || "";
  });

  watch(
    () => dataDto.value.workspace,
    (val) => {
      workspaceValue.value = val || "";
    },
  );

  watch(workspaceValue, (val) => {
    dataDto.value.workspace = val || null;
  });

  watch(
    () => dataDto.value.role,
    (val) => {
      roleValue.value = val || "";
    },
  );

  watch(roleValue, (val) => {
    if (val) {
      dataDto.value.role = val as (typeof InvitationRole)[keyof typeof InvitationRole];
    }
  });

  // Initialize vee-validate values
  workspaceValue.value = dataDto.value.workspace || "";
  roleValue.value = dataDto.value.role;

  const validateEmail = () => {
    emailValue.value = newEmail.value;
  };

  const validateWorkspace = () => {
    workspaceValue.value = dataDto.value.workspace || "";
  };

  const isValidForm = computed(() => {
    return dataDto.value.emails.length > 0 && !!dataDto.value.workspace && !!dataDto.value.role;
  });

  const isValidFormFull = computed(() => {
    return isValidForm.value && meta.value.valid;
  });

  const workspacesVariables = computed(() => {
    const currentUserId = authStore.userId;
    if (!currentUserId) {
      return null;
    }

    return {
      where: {
        isActive: {
          exact: true,
        },
        memberships: {
          user: {
            id: {
              exact: currentUserId,
            },
          },
          role: {
            in: ["admin_institucional", "coordinator", "admin_sede"],
          },
          status: {
            exact: "active",
          },
          isActive: {
            exact: true,
          },
        },
      },
    };
  });

  const { result: workspacesResult } = useQuery(SEARCH_WORKSPACES, workspacesVariables, () => ({
    enabled: !!authStore.userAuth?.id,
    fetchPolicy: "network-only",
  }));

  const workspaces = computed<WorkspaceOption[]>(() => {
    const objects = workspacesResult.value?.searchWorkspaces?.objects;
    if (!objects) return [];
    return objects;
  });

  const roles = computed<RoleOption[]>(() => [
    { label: t("invitations.form.roleStudent"), value: InvitationRole.STUDENT },
    { label: t("invitations.form.roleTeacher"), value: InvitationRole.TEACHER },
    { label: t("invitations.form.roleCoordinator"), value: InvitationRole.COORDINATOR },
    { label: t("invitations.form.roleAdmin"), value: InvitationRole.ADMIN_INSTITUCIONAL },
  ]);

  const classroomsVariables = computed(() => {
    if (!dataDto.value.workspace) {
      return null;
    }
    return {
      where: {
        workspace: {
          id: {
            exact: dataDto.value.workspace,
          },
        },
        isActive: {
          exact: true,
        },
      },
    };
  });

  const { result: classroomsResult } = useQuery(SEARCH_CLASSROOMS, classroomsVariables, () => ({
    enabled: !!dataDto.value.workspace,
    fetchPolicy: "network-only",
  }));

  watch(
    () => dataDto.value.workspace,
    () => {
      dataDto.value.classrooms = [];
    },
  );

  const classroomOptions = computed<ClassroomOption[]>(() => {
    const objects = classroomsResult.value?.searchClassrooms?.objects;
    if (!objects) return [];
    return objects;
  });

  const hasClassrooms = computed(() => classroomOptions.value.length > 0);

  function addEmail(): void {
    const email = newEmail.value.trim();
    if (email && !dataDto.value.emails.includes(email)) {
      // Validate email before adding
      emailValue.value = email;
      if (!emailError.value) {
        dataDto.value.emails.push(email);
        newEmail.value = "";
        emailValue.value = "";
      }
    }
  }

  function removeEmail(index: number): void {
    dataDto.value.emails.splice(index, 1);
  }

  const emailsCountLabel = computed(() => {
    const count = dataDto.value.emails.length;
    if (count === 0) return t("invitations.form.emailsCount.zero");
    if (count === 1) return t("invitations.form.emailsCount.one");
    return t("invitations.form.emailsCount.other", { count });
  });

  function toggleClassroom(classroomValue: string): void {
    const index = dataDto.value.classrooms.indexOf(classroomValue);
    if (index === -1) {
      dataDto.value.classrooms.push(classroomValue);
    } else {
      dataDto.value.classrooms.splice(index, 1);
    }
  }

  const sendButtonLabel = computed(() => {
    const count = dataDto.value.emails.length;
    if (count === 0) return t("invitations.form.sendButton.zero");
    if (count === 1) return t("invitations.form.sendButton.one");
    return t("invitations.form.sendButton.other", { count });
  });

  function onCancel(): void {
    emit("update:visible", false);
  }

  const handleSubmit = veeHandleSubmit(() => {
    if (props.loading || !isValidFormFull.value) return;

    const invitationsInput: CreateInvitationInput[] = dataDto.value.emails.map((email) => {
      const input = {
        email: email.trim() as `${string}@${string}`,
        workspace: dataDto.value.workspace!,
        role: dataDto.value.role,
        ...(dataDto.value.welcomeMessage && { welcomeMessage: dataDto.value.welcomeMessage }),
        ...(dataDto.value.classrooms.length > 0 && { classrooms: dataDto.value.classrooms }),
      } as CreateInvitationInput;
      return input;
    });

    emit("submit", invitationsInput);
    dataDto.value = {
      emails: [],
      workspace: null,
      role: InvitationRole.STUDENT,
      classrooms: [],
      welcomeMessage: "",
    };
    newEmail.value = "";
    emailValue.value = "";
    workspaceValue.value = "";
    roleValue.value = InvitationRole.STUDENT;
  });
</script>
