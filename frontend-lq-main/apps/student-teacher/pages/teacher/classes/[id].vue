<script setup lang="ts">
  import { computed, onMounted, ref } from "vue";
  import { useRoute } from "vue-router";
  import { useClassDetail } from "~/composables/classes/useClassDetail";
  import { useClassAssignments } from "~/composables/classes/useClassAssignments";
  import { useClassStudents } from "~/composables/classes/useClassStudents";
  import { useClasses } from "~/composables/classes/useClasses";
  import type { AssignmentGrade, Class } from "~/composables/classes/types";
  import { useEditClass } from "~/composables/classes/useEditClass";
  import { useAddAssignment } from "~/composables/classes/useAddAssignment";
  import { useEditAssignment } from "~/composables/classes/useEditAssignment";
  import { useAssignmentDetails } from "~/composables/classes/useAssignmentDetails";
  import { useAddClassStudents } from "~/composables/classes/useAddClassStudents";
  import { useStudentProfile } from "~/composables/classes/useStudentProfile";
  import ClassDetailHeader from "~/components/classes/detail/ClassDetailHeader.vue";
  import ClassDetailTabs from "~/components/classes/detail/ClassDetailTabs.vue";
  import ClassMetricsCards from "~/components/classes/detail/ClassMetricsCards.vue";
  import AssignmentsView from "~/components/classes/detail/assignments/AssignmentsView.vue";
  import AssignmentsGradebook from "~/components/classes/detail/assignments/AssignmentsGradebook.vue";
  import ClassStudentsView from "~/components/classes/detail/students/ClassStudentsView.vue";
  import ClassStatisticsView from "~/components/classes/detail/statistics/ClassStatisticsView.vue";
  import EditClassModal from "~/components/classes/detail/modals/EditClassModal.vue";
  import AddAssignmentModal from "~/components/classes/detail/modals/AddAssignmentModal.vue";
  import EditAssignmentModal from "~/components/classes/detail/modals/EditAssignmentModal.vue";
  import AssignmentDetailsModal from "~/components/classes/detail/modals/AssignmentDetailsModal.vue";
  import AddClassStudentsModal from "~/components/classes/detail/modals/AddClassStudentsModal.vue";
  import StudentProfileModal from "~/components/classes/detail/modals/StudentProfileModal.vue";

  const route = useRoute();
  const classId = computed(() => route.params.id as string);

  const { classDetail, fetchClassDetail } = useClassDetail();
  const { assignments, fetchAssignments } = useClassAssignments();
  const { students, fetchClassStudents } = useClassStudents();
  const { updateClass } = useClasses();

  // Mock grades data - will be replaced with real data later
  // Class 2 students: s13 to s20, assignments: b1, b2
  const grades = ref<AssignmentGrade[]>([
    // Carlos Mendoza (s13) - Has completed assignments with scores
    {
      assignmentId: "b1",
      studentId: "s13",
      status: "graded",
      score: 82,
      cefrLevel: "A1",
      practiceTime: "1h 30m",
      skills: {
        grammar: 85,
        pronunciation: 78,
        vocabulary: 80,
        fluency: 84,
        cohesion: 83,
      },
    },
    {
      assignmentId: "b2",
      studentId: "s13",
      status: "completed",
      score: 98,
      cefrLevel: "C2",
      practiceTime: "3h 15m",
      skills: {
        grammar: 96,
        pronunciation: 95,
        vocabulary: 99,
        fluency: 98,
        cohesion: 97,
      },
    },
    // Ana García (s14) - Mix of statuses
    {
      assignmentId: "b1",
      studentId: "s14",
      status: "pending",
    },
    {
      assignmentId: "b2",
      studentId: "s14",
      status: "graded",
      score: 76,
      cefrLevel: "B1",
      practiceTime: "2h 7m",
      skills: {
        grammar: 96,
        pronunciation: 88,
        vocabulary: 75,
        fluency: 91,
        cohesion: 81,
      },
    },
    // Luis Fernandez (s15) - In progress
    {
      assignmentId: "b1",
      studentId: "s15",
      status: "in_progress",
    },
    {
      assignmentId: "b2",
      studentId: "s15",
      status: "pending",
    },
    // Maria Lopez (s16) - More variety
    {
      assignmentId: "b1",
      studentId: "s16",
      status: "graded",
      score: 94,
      cefrLevel: "A1",
      practiceTime: "2h 45m",
      skills: {
        grammar: 92,
        pronunciation: 94,
        vocabulary: 95,
        fluency: 94,
        cohesion: 93,
      },
    },
    {
      assignmentId: "b2",
      studentId: "s16",
      status: "in_progress",
    },
    // Juan Perez (s17) - Not started
    {
      assignmentId: "b1",
      studentId: "s17",
      status: "pending",
    },
    {
      assignmentId: "b2",
      studentId: "s17",
      status: "pending",
    },
    // Carmen Sanchez (s18) - Not started
    {
      assignmentId: "b1",
      studentId: "s18",
      status: "pending",
    },
    {
      assignmentId: "b2",
      studentId: "s18",
      status: "pending",
    },
    // Pedro Gomez (s19) - Not started
    {
      assignmentId: "b1",
      studentId: "s19",
      status: "pending",
    },
    {
      assignmentId: "b2",
      studentId: "s19",
      status: "pending",
    },
    // Laura Torres (s20) - Not started
    {
      assignmentId: "b1",
      studentId: "s20",
      status: "pending",
    },
    {
      assignmentId: "b2",
      studentId: "s20",
      status: "pending",
    },
  ]);
  const { showModal: showEditClassModal, openModal: openEditClassModal, classData: editedClassData } = useEditClass();
  const { showModal: showAddAssignmentModal, openModal: openAddAssignmentModal } = useAddAssignment();
  const { showModal: showEditAssignmentModal, openModal: openEditAssignmentModal } = useEditAssignment();
  const { showModal: showAssignmentDetailsModal, openModal: openAssignmentDetailsModal } = useAssignmentDetails();
  const { showModal: showAddClassStudentsModal, openModal: openAddClassStudentsModal } = useAddClassStudents();
  const { showModal: showStudentProfileModal, openModal: openStudentProfileModal } = useStudentProfile();

  const handleEditClass = () => {
    if (classDetail.value) {
      openEditClassModal(classDetail.value);
    }
  };

  const handleAddActivity = () => {
    openAddAssignmentModal();
  };

  const handleExportGradebook = () => {
    // TODO: Implement export gradebook functionality
  };

  const handleViewDetails = (assignmentId: string) => {
    const assignment = assignments.value.find((a) => a.id === assignmentId);
    if (assignment) {
      openAssignmentDetailsModal(assignment);
    }
  };

  const handleEditAssignment = (assignmentId: string) => {
    const assignment = assignments.value.find((a) => a.id === assignmentId);
    if (assignment) {
      openEditAssignmentModal(assignment);
    }
  };

  const handleSaveClass = (updatedClass?: Class | null) => {
    // Update class in localStorage and local state
    if (updatedClass) {
      updateClass(updatedClass);
      // Update local classDetail to reflect changes immediately
      // Use Object.assign to ensure reactivity
      if (classDetail.value) {
        Object.assign(classDetail.value, updatedClass);
      } else {
        classDetail.value = { ...updatedClass };
      }
      // Refresh students list to reflect any changes
      fetchClassStudents(classId.value);
    } else if (editedClassData.value) {
      // Fallback: Use editedClassData if updatedClass is not provided
      updateClass(editedClassData.value);
      if (classDetail.value) {
        Object.assign(classDetail.value, editedClassData.value);
      } else {
        classDetail.value = { ...editedClassData.value };
      }
      // Refresh students list to reflect any changes
      fetchClassStudents(classId.value);
    } else {
      // Final fallback: Refresh class data
      fetchClassDetail(classId.value);
      fetchClassStudents(classId.value);
    }
    // Clear edited class data after saving
    editedClassData.value = null;
  };

  const handleCreateAssignment = () => {
    // Refresh assignments
    fetchAssignments(classId.value);
  };

  const handleSaveAssignment = () => {
    // Refresh assignments
    fetchAssignments(classId.value);
  };

  const handleAddStudent = () => {
    openAddClassStudentsModal(classId.value);
  };

  const handleViewStudentProfile = (studentId: string) => {
    const student = students.value.find((s) => s.id === studentId);
    if (student) {
      openStudentProfileModal(student);
    }
  };

  const handleAddStudentsComplete = () => {
    // Refresh students list and class detail
    fetchClassStudents(classId.value);
    fetchClassDetail(classId.value);
  };

  const handleGradeCellClick = (_data: { assignmentId: string; studentId: string }) => {
    // This handler is kept for compatibility but the popover is now handled in the component
    // The component will handle showing the popover directly
  };

  const handleViewPractice = () => {
    // Handle view practice action
    // TODO: Implement view practice functionality
  };

  onMounted(() => {
    fetchClassDetail(classId.value);
    fetchAssignments(classId.value);
    fetchClassStudents(classId.value);
  });
</script>

<template>
  <div class="space-y-6">
    <ClassDetailHeader :class-detail="classDetail" :students="students" @edit-class="handleEditClass" />
    <ClassMetricsCards />
    <ClassDetailTabs>
      <template #assignments>
        <AssignmentsView
          :assignments="assignments"
          @add-activity="handleAddActivity"
          @view-details="handleViewDetails"
          @edit="handleEditAssignment"
        />
      </template>
      <template #gradebook>
        <AssignmentsGradebook
          :assignments="assignments"
          :students="students"
          :grades="grades"
          @cell-click="handleGradeCellClick"
          @export-gradebook="handleExportGradebook"
          @add-activity="handleAddActivity"
          @view-practice="handleViewPractice"
        />
      </template>
      <template #students>
        <ClassStudentsView
          :students="students"
          @add-student="handleAddStudent"
          @view-profile="handleViewStudentProfile"
        />
      </template>
      <template #statistics>
        <ClassStatisticsView :students="students" :assignments="assignments" :grades="grades" />
      </template>
    </ClassDetailTabs>

    <!-- Modals -->
    <EditClassModal v-model:visible="showEditClassModal" :class-data="classDetail" @save-complete="handleSaveClass" />
    <AddAssignmentModal v-model:visible="showAddAssignmentModal" @create-complete="handleCreateAssignment" />
    <EditAssignmentModal v-model:visible="showEditAssignmentModal" @save-complete="handleSaveAssignment" />
    <AssignmentDetailsModal v-model:visible="showAssignmentDetailsModal" />
    <AddClassStudentsModal v-model:visible="showAddClassStudentsModal" @add-complete="handleAddStudentsComplete" />
    <StudentProfileModal v-model:visible="showStudentProfileModal" />
  </div>
</template>
