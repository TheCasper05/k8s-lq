<script setup lang="ts">
  import { computed, ref, watch } from "vue";
  import { useI18n } from "vue-i18n";
  import { useQuery } from "@vue/apollo-composable";
  import { Form, type FormInstance } from "@primevue/forms";
  import { zodResolver } from "@primevue/forms/resolvers/zod";
  import { z } from "zod";
  import { useAuthStore } from "@lq/stores";
  import { Icon } from "@iconify/vue";
  import Dialog from "primevue/dialog";
  import Chip from "primevue/chip";
  import Select from "primevue/select";
  import Textarea from "primevue/textarea";
  import InputText from "primevue/inputtext";
  import Message from "primevue/message";
  import Button from "primevue/button";
  import { InvitationRole } from "../utils/constants";
  import type { WorkspaceOption, RoleOption, ClassroomOption, InvitationDto } from "../utils/types";
  import { SEARCH_WORKSPACES, SEARCH_CLASSROOMS, type CreateInvitationInput } from "@lq/graphql";

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

  const formRef = ref<FormInstance | null>(null);

  const dataDto = ref<InvitationDto>({
    emails: [],
    workspace: null,
    role: InvitationRole.STUDENT,
    classrooms: [],
    welcomeMessage: "",
  });

  const isValidForm = computed(() => {
    return dataDto.value.emails.length > 0 && !!dataDto.value.workspace && !!dataDto.value.role;
  });

  const isValidFormFull = computed(() => {
    return isValidForm.value && formRef.value?.valid;
  });

  const resolver = computed(() =>
    zodResolver(
      z.object({
        email: z
          .email()
          .optional()
          .refine((email) => (email ? !dataDto.value.emails.includes(email.trim()) : true), {
            message: t("invitations.form.emailDuplicate"),
          }),
        workspace: z.string("This field is required"),
        role: z.string("This field is required"),
      }),
    ),
  );

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

  const newEmail = ref("");

  function addEmail(): void {
    const email = newEmail.value.trim();
    if (email && !dataDto.value.emails.includes(email)) {
      dataDto.value.emails.push(email);
      newEmail.value = "";
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

  function onSubmit({ valid }: { valid: boolean }): void {
    if (!valid || props.loading) return;

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
  }
</script>

<template>
  <Dialog
    :visible="visible"
    modal
    :header="$t('invitations.newInvitation')"
    closable
    :style="{ width: '640px', maxWidth: '100%' }"
    @update:visible="$emit('update:visible', $event)"
  >
    <Form v-slot="$form" ref="formRef" class="flex flex-col gap-5" :resolver="resolver">
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
              <Icon icon="solar:letter-line-duotone" />
            </template>
          </Chip>
        </div>

        <div class="flex items-stretch gap-2">
          <InputText
            v-model="newEmail"
            name="email"
            :placeholder="$t('invitations.form.emailPlaceholder')"
            class="flex-1"
            @keydown.enter.prevent="addEmail"
          />

          <Button type="button" severity="secondary" class="rounded-2xl px-3! py-1!" @click="addEmail">
            <template #icon>
              <Icon icon="solar:add-circle-line-duotone" />
            </template>
          </Button>
        </div>
        <Message v-if="$form.email?.invalid && newEmail" severity="error" size="small" variant="simple">
          {{ $form.email.error.message }}
        </Message>

        <small class="text-xs text-surface-500">
          {{ emailsCountLabel }}
        </small>
      </div>

      <div class="flex flex-col gap-2">
        <label class="font-medium text-sm">{{ $t("invitations.form.workspace") }} *</label>
        <Select
          v-model="dataDto.workspace"
          name="workspace"
          :options="workspaces"
          option-label="name"
          option-value="id"
          :placeholder="$t('invitations.form.workspacePlaceholder')"
          filter
          show-clear
          class="w-full"
        />
        <Message v-if="$form.workspace?.invalid" severity="error" size="small" variant="simple">
          {{ $form.workspace.error.message }}
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
                dataDto.role === role.value
                  ? 'bg-primary-500 text-white px-3 py-2 rounded-2xl border-2 border-primary-500 shadow-[0_4px_6px_-4px_rgba(0,0,0,0.1),0_10px_15px_-3px_rgba(0,0,0,0.1)]'
                  : 'border-2 border-primary-200 px-3 py-2 rounded-2xl',
            }"
            @click="dataDto.role = role.value"
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
            @click="onSubmit({ valid: !!isValidFormFull })"
          />
        </div>
      </div>
    </Form>
  </Dialog>
</template>
