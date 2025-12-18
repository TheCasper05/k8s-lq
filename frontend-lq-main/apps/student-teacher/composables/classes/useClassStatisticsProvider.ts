import { computed } from "vue";
import type { LqMetric } from "@lq/ui";
import type { Student } from "~/composables/students/types";
import type { Assignment, AssignmentGrade } from "~/composables/classes/types";
import { useClassStatistics } from "~/composables/classes/useClassStatistics";

export const useClassStatisticsProvider = (
  students: Student[],
  assignments: Assignment[],
  grades: AssignmentGrade[],
) => {
  const { statistics, leaderboard, assignmentsChartData, skillsChartData, studyTimeChartData } = useClassStatistics(
    students,
    assignments,
    grades,
  );

  const metricsCards = computed<LqMetric[]>(() => [
    {
      icon: "solar:chart-line-duotone",
      label: "Avg Score",
      value: `${statistics.value.avgScore}%`,
      badge: statistics.value.cefrLevel,
      color: "primary" as const,
    },
    {
      icon: "solar:check-circle-line-duotone",
      label: `Completion ${statistics.value.completionFraction}`,
      value: `${statistics.value.completionRate}%`,
      color: "success" as const,
    },
    {
      icon: "solar:users-group-rounded-line-duotone",
      label: "last 30 days Active",
      value: `${statistics.value.activeStudents}/${students.length}`,
      color: "info" as const,
    },
    {
      icon: "solar:clock-circle-line-duotone",
      label: "Total practice time",
      value: statistics.value.totalPracticeTime,
      color: "warning" as const,
    },
  ]);

  const topThree = computed(() => leaderboard.value.slice(0, 3));

  const getBadgeClass = (level: string) => {
    const baseClasses = "px-2 py-1 rounded text-xs font-semibold";
    switch (level) {
      case "C2":
        return `${baseClasses} bg-success-500 dark:bg-success-600 text-white`;
      case "C1":
        return `${baseClasses} bg-success-400 dark:bg-success-500 text-white`;
      case "B2":
        return `${baseClasses} bg-info-500 dark:bg-info-600 text-white`;
      case "B1":
        return `${baseClasses} bg-info-400 dark:bg-info-500 text-white`;
      case "A2":
        return `${baseClasses} bg-warning-500 dark:bg-warning-600 text-white`;
      case "A1":
        return `${baseClasses} bg-warning-400 dark:bg-warning-500 text-white`;
      default:
        return `${baseClasses} bg-surface-300 dark:bg-surface-700 text-surface-700 dark:text-surface-300`;
    }
  };

  const barChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 1,
        ticks: {
          callback: (value: number | string) => `${Math.round(Number(value) * 100)}%`,
        },
      },
    },
  };

  const doughnutChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
    },
  };

  const lineChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  const getRankBadgeClass = (rank: number) => {
    if (rank === 1) return "bg-warning-400 dark:bg-warning-500 text-warning-900 dark:text-warning-50";
    if (rank === 2) return "bg-surface-300 dark:bg-surface-600 text-surface-700 dark:text-surface-200";
    if (rank === 3) return "bg-warning-500 dark:bg-warning-600 text-warning-900 dark:text-warning-50";
    return "bg-surface-200 dark:bg-surface-700 text-surface-600 dark:text-surface-300";
  };

  return {
    statistics,
    leaderboard,
    assignmentsChartData,
    skillsChartData,
    studyTimeChartData,
    metricsCards,
    topThree,
    getBadgeClass,
    getRankBadgeClass,
    barChartOptions,
    doughnutChartOptions,
    lineChartOptions,
  };
};
