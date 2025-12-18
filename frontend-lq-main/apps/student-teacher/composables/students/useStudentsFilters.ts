import { ref, computed } from "vue";
import type { Student, StudentFilters } from "./types";

/**
 * Composable for filtering students
 */
export const useStudentsFilters = (students: { value: Student[] }) => {
  const filters = ref<StudentFilters>({
    level: null,
    search: "",
  });

  const filteredStudents = computed(() => {
    let result = [...students.value];

    // Filter by level
    if (filters.value.level) {
      result = result.filter((student) => student.level === filters.value.level);
    }

    // Filter by search (name or email)
    if (filters.value.search) {
      const searchLower = filters.value.search.toLowerCase();
      result = result.filter(
        (student) =>
          student.firstName.toLowerCase().includes(searchLower) ||
          student.lastName.toLowerCase().includes(searchLower) ||
          student.email.toLowerCase().includes(searchLower),
      );
    }

    return result;
  });

  const availableLevels = computed(() => {
    const levels = new Set(students.value.map((student) => student.level));
    return Array.from(levels).sort();
  });

  const clearFilters = () => {
    filters.value = {
      level: null,
      search: "",
    };
  };

  return {
    filters,
    filteredStudents,
    availableLevels,
    clearFilters,
  };
};
