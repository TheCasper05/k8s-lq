import { ref, computed } from "vue";
import type { Class, ClassFilters } from "./types";

/**
 * Composable for filtering classes
 */
export const useClassesFilters = (classes: { value: Class[] }) => {
  const filters = ref<ClassFilters>({
    level: null,
    search: "",
  });

  const filteredClasses = computed(() => {
    let result = [...classes.value];

    // Filter by level
    if (filters.value.level) {
      result = result.filter((classItem) => classItem.level === filters.value.level);
    }

    // Filter by search (name or description)
    if (filters.value.search) {
      const searchLower = filters.value.search.toLowerCase();
      result = result.filter(
        (classItem) =>
          classItem.name.toLowerCase().includes(searchLower) ||
          classItem.description?.toLowerCase().includes(searchLower),
      );
    }

    return result;
  });

  const availableLevels = computed(() => {
    const levels = new Set(classes.value.map((classItem) => classItem.level));
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
    filteredClasses,
    availableLevels,
    clearFilters,
  };
};
