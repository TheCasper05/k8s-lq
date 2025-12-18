import { computed } from "vue";
import type { Student, StudentStats } from "./types";

/**
 * Composable for calculating student statistics
 */
export const useStudentsStats = (students: { value: Student[] }) => {
  const stats = computed<StudentStats>(() => {
    const totalStudents = students.value.length;

    // Calculate total study time
    const totalStudyMinutes = students.value.reduce((sum, student) => sum + student.studyTimeMinutes, 0);
    const totalStudyHours = Math.floor(totalStudyMinutes / 60);

    // Calculate average progress
    const averageProgress =
      students.value.length > 0
        ? Math.round(students.value.reduce((sum, student) => sum + student.progress, 0) / students.value.length)
        : 0;

    // Mock monthly changes (hardcoded for now)
    const monthlyChangePercent = 8; // +8% este mes
    const monthlyHoursChangePercent = 12; // +12% vs mes anterior

    return {
      totalStudents,
      totalStudyHours,
      totalStudyMinutes,
      averageProgress,
      monthlyChangePercent,
      monthlyHoursChangePercent,
    };
  });

  return {
    stats,
  };
};
