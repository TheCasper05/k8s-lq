import { computed } from "vue";
import type { Class, ClassStats } from "./types";

/**
 * Composable for calculating class statistics
 */
export const useClassesStats = (classes: { value: Class[] }) => {
  const stats = computed<ClassStats>(() => {
    const totalClasses = classes.value.length;
    const activeClasses = classes.value.filter((c) => c.status === "active").length;
    const totalStudents = classes.value.reduce((sum, c) => sum + c.students, 0);
    const avgPerClass = totalClasses > 0 ? Math.round(totalStudents / totalClasses) : 0;

    return {
      totalClasses,
      activeClasses,
      totalStudents,
      avgPerClass,
    };
  });

  return {
    stats,
  };
};
