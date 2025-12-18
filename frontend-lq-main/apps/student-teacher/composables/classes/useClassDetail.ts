import { ref } from "vue";
import type { Class } from "./types";
import { getMockClasses, loadClassesFromStorage } from "./useClasses";

/**
 * Composable for managing class detail data
 */
export const useClassDetail = () => {
  const classDetail = ref<Class | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const fetchClassDetail = (classId: string) => {
    loading.value = true;
    error.value = null;

    try {
      // Try to load from localStorage first
      let allClasses = loadClassesFromStorage();

      // If no stored data, use mock data
      if (!allClasses || allClasses.length === 0) {
        allClasses = getMockClasses();
      }

      // Find class by ID
      const foundClass = allClasses.find((c) => c.id === classId);

      if (foundClass) {
        classDetail.value = { ...foundClass };
      } else {
        error.value = "Class not found";
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : "Error fetching class detail";
    } finally {
      loading.value = false;
    }
  };

  return {
    classDetail,
    loading,
    error,
    fetchClassDetail,
  };
};
