<script setup lang="ts">
  import { ref, watch } from "vue";
  import { useAddClassStudents } from "~/composables/classes/useAddClassStudents";
  import ClassInvitationCodeTab from "./components/ClassInvitationCodeTab.vue";
  import ClassSearchStudentsTab from "./components/ClassSearchStudentsTab.vue";

  const props = defineProps<{
    visible: boolean;
    activeTab?: number;
  }>();

  const emit = defineEmits<{
    "update:visible": [value: boolean];
    "update:active-tab": [value: number];
    "add-complete": [];
  }>();

  const { activeTab: composableActiveTab, setActiveTab, addStudents, closeModal } = useAddClassStudents();
  const localActiveTab = ref(String(props.activeTab ?? composableActiveTab.value));

  watch(
    () => props.activeTab,
    (newTab) => {
      if (newTab !== undefined) {
        localActiveTab.value = String(newTab);
        setActiveTab(newTab);
        composableActiveTab.value = newTab;
      }
    },
  );

  watch(localActiveTab, (newTab) => {
    setActiveTab(Number(newTab));
    emit("update:active-tab", Number(newTab));
  });

  watch(
    () => props.visible,
    (newValue) => {
      if (!newValue) {
        closeModal();
        // Reset when closing
        localActiveTab.value = "0";
      }
    },
  );

  const handleClose = () => {
    emit("update:visible", false);
  };

  const handleAddStudents = async () => {
    await addStudents();
    emit("update:visible", false);
    emit("add-complete");
  };
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
      header: { class: '!border-b !pb-4' },
      content: { class: '!pt-0' },
    }"
    @update:visible="handleClose"
  >
    <template #header>
      <div class="flex items-center justify-between w-full">
        <h2 class="text-2xl font-bold text-surface-900 dark:text-surface-100">
          {{ $t("classes.students.addModal.title") }}
        </h2>
      </div>
    </template>

    <Tabs :value="localActiveTab" class="w-full custom-tabview" @update:value="localActiveTab = String($event)">
      <TabList>
        <Tab value="0">
          <div class="flex items-center gap-2">
            <Icon name="solar:link-round-line-duotone" />
            <span>{{ $t("classes.students.addModal.invitationCode") }}</span>
          </div>
        </Tab>
        <Tab value="1">
          <div class="flex items-center gap-2">
            <Icon name="solar:magnifer-line-duotone" />
            <span>{{ $t("classes.students.addModal.searchStudents") }}</span>
          </div>
        </Tab>
      </TabList>
      <TabPanels>
        <TabPanel value="0">
          <ClassInvitationCodeTab @add-students="handleAddStudents" />
        </TabPanel>
        <TabPanel value="1">
          <ClassSearchStudentsTab @add-students="handleAddStudents" />
        </TabPanel>
      </TabPanels>
    </Tabs>
  </Dialog>
</template>
