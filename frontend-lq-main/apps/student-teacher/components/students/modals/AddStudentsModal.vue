<template>
  <Dialog
    :visible="visible"
    :header="$t('students.addStudents')"
    modal
    closable
    :draggable="false"
    class="w-full max-w-2xl"
    @update:visible="$emit('update:visible', $event)"
  >
    <Tabs :value="localActiveTab" class="w-full custom-tabview" @update:value="localActiveTab = String($event)">
      <TabList>
        <Tab value="0">{{ $t("students.invitationCode") }}</Tab>
        <Tab value="1">{{ $t("students.searchStudents") }}</Tab>
      </TabList>
      <TabPanels>
        <TabPanel value="0">
          <InvitationCodeTab @add-students="handleAddStudents" />
        </TabPanel>
        <TabPanel value="1">
          <SearchStudentsTab @add-students="handleAddStudents" />
        </TabPanel>
      </TabPanels>
    </Tabs>
  </Dialog>
</template>

<script setup lang="ts">
  import { ref, watch } from "vue";
  import InvitationCodeTab from "./components/InvitationCodeTab.vue";
  import SearchStudentsTab from "./components/SearchStudentsTab.vue";

  const props = defineProps<{
    visible: boolean;
    activeTab?: number;
  }>();

  const emit = defineEmits<{
    "update:visible": [value: boolean];
    "update:active-tab": [value: number];
  }>();

  const localActiveTab = ref(String(props.activeTab || 0));

  watch(
    () => props.activeTab,
    (newTab) => {
      if (newTab !== undefined) {
        localActiveTab.value = String(newTab);
      }
    },
  );

  watch(localActiveTab, (newTab) => {
    emit("update:active-tab", Number(newTab));
  });

  const handleAddStudents = () => {
    emit("update:visible", false);
  };
</script>
