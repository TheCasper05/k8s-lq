<script setup lang="ts">
  import { ref, onMounted } from "vue";
  import { useStudents } from "~/composables/students/useStudents";
  import { useStudentsStats } from "~/composables/students/useStudentsStats";
  import { useStudentsFilters } from "~/composables/students/useStudentsFilters";
  import { useAddStudents } from "~/composables/students/useAddStudents";
  import StudentsHeader from "~/components/students/StudentsHeader.vue";
  import StudentsKPIs from "~/components/students/StudentsKPIs.vue";
  import StudentsFilters from "~/components/students/StudentsFilters.vue";
  import StudentsGallery from "~/components/students/StudentsGallery.vue";
  import StudentsTable from "~/components/students/StudentsTable.vue";
  import AddStudentsModal from "~/components/students/modals/AddStudentsModal.vue";

  definePageMeta({
    layout: "app",
  });

  const { students, fetchStudents } = useStudents();
  const { stats } = useStudentsStats(students);
  const { filters, filteredStudents, availableLevels } = useStudentsFilters(students);
  const { showModal: showAddModal, activeTab, openModal, closeModal } = useAddStudents();

  const currentView = ref<"gallery" | "list">("gallery");

  const viewOptions = [
    { value: "gallery", label: "students.gallery", icon: "solar:widget-2-linear" },
    { value: "list", label: "students.list", icon: "solar:list-linear" },
  ];

  const handleAddStudent = () => {
    openModal();
  };

  const updateFilters = (newFilters: typeof filters.value) => {
    filters.value = { ...newFilters };
  };

  const handleAddStudents = () => {
    closeModal();
    // Refresh students list
    fetchStudents();
  };

  const handleExport = () => {
    // TODO: Implement export functionality
  };

  onMounted(() => {
    fetchStudents();
  });
</script>

<template>
  <div class="space-y-4 sm:space-y-6 lq-container">
    <StudentsHeader @add-student="handleAddStudent" />
    <StudentsKPIs :stats="stats" />
    <div class="flex flex-col gap-4">
      <div
        class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 sm:gap-4 bg-surface-0 dark:bg-surface-900 p-3 sm:p-4 rounded-lg border"
      >
        <SelectButton
          v-model="currentView"
          :options="viewOptions"
          option-label="label"
          option-value="value"
          data-key="value"
          aria-labelledby="view-toggle"
          size="large"
        >
          <template #option="slotProps">
            <Icon :name="slotProps.option.icon" class="text-sm" />
            <span>{{ $t(slotProps.option.label) }}</span>
          </template>
        </SelectButton>
        <StudentsFilters
          :filters="filters"
          :available-levels="availableLevels"
          @update:filters="updateFilters"
          @export="handleExport"
        />
      </div>
      <StudentsGallery v-if="currentView === 'gallery'" :students="filteredStudents" />
      <StudentsTable v-else :students="filteredStudents" />
    </div>
    <AddStudentsModal
      v-model:visible="showAddModal"
      :active-tab="activeTab"
      @update:active-tab="activeTab = $event"
      @add-students="handleAddStudents"
    />
  </div>
</template>
