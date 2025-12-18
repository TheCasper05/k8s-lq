<script setup lang="ts">
  import AssignedStudentsTable, { type AssignedStudent } from "~/components/activities/table/AssignedStudentsTable.vue";

  interface Props {
    students: AssignedStudent[];
  }

  defineProps<Props>();
</script>

<template>
  <div class="animate-fade-in">
    <AssignedStudentsTable :students="students" />
  </div>
</template>
