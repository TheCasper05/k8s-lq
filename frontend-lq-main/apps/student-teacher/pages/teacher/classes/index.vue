<script setup lang="ts">
  import { onMounted } from "vue";
  import { useRouter } from "vue-router";
  import { useClasses } from "~/composables/classes/useClasses";
  import { useClassesStats } from "~/composables/classes/useClassesStats";
  import { useClassesFilters } from "~/composables/classes/useClassesFilters";
  import { useCreateClass } from "~/composables/classes/useCreateClass";
  import ClassesHeader from "~/components/classes/ClassesHeader.vue";
  import ClassesKPIs from "~/components/classes/ClassesKPIs.vue";
  import ClassesFilters from "~/components/classes/ClassesFilters.vue";
  import ClassesGallery from "~/components/classes/ClassesGallery.vue";
  import CreateClassModal from "~/components/classes/modals/CreateClassModal.vue";
  import type { Class } from "~/composables/classes/types";

  const router = useRouter();

  const { classes, fetchClasses, addClass } = useClasses();
  const { stats } = useClassesStats(classes);
  const { filters, filteredClasses, availableLevels } = useClassesFilters(classes);
  const { showModal: showCreateModal, openModal, closeModal } = useCreateClass();

  const handleCreateClass = () => {
    openModal();
  };

  const updateFilters = (newFilters: typeof filters.value) => {
    filters.value = { ...newFilters };
  };

  const handleCreateClassComplete = (newClass?: Class) => {
    if (newClass) {
      // Add the new class to the list
      addClass(newClass);
      // Close the modal
      closeModal();
      // Redirect to the class detail page
      router.push(`/teacher/classes/${newClass.id}`);
    } else {
      // If no class was passed, it means there was an error
      // The error is already shown in the modal, so we don't close it
      // Just wait for the user to fix the issue or try again
    }
  };

  const handleExport = () => {
    // TODO: Implement export functionality
  };

  const handleClassAction = (action: string, classId: string) => {
    if (action === "click") {
      // Navigate to class detail page
      router.push(`/teacher/classes/${classId}`);
      return;
    }
    // TODO: Implement class actions (edit, duplicate, favorite, archive, delete)
    // Action: ${action}, Class ID: ${classId}
  };

  onMounted(() => {
    fetchClasses();
  });
</script>

<template>
  <div class="flex flex-col lq-container">
    <ClassesKPIs :stats="stats" />
    <ClassesHeader @create-class="handleCreateClass" />
    <div class="flex flex-col">
      <div class="w-full py-4">
        <ClassesFilters
          :filters="filters"
          :available-levels="availableLevels"
          @update:filters="updateFilters"
          @export="handleExport"
        />
      </div>
      <ClassesGallery
        :classes="filteredClasses"
        @edit="handleClassAction('edit', $event)"
        @duplicate="handleClassAction('duplicate', $event)"
        @favorite="handleClassAction('favorite', $event)"
        @archive="handleClassAction('archive', $event)"
        @delete="handleClassAction('delete', $event)"
        @click="handleClassAction('click', $event)"
      />
    </div>
    <CreateClassModal v-model:visible="showCreateModal" @create-complete="handleCreateClassComplete" />
  </div>
</template>
