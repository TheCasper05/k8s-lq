import { ref } from "vue";

export interface DashboardStat {
  titleKey: string;
  icon: string;
  value: string;
  subtitleKey: string;
  color: "primary" | "blue" | "green" | "orange";
}

export function useDashboardPage() {
  const { t } = useI18n();

  const adminStats = ref<DashboardStat[]>([
    {
      titleKey: "dashboard.admin.totalUsers",
      icon: "solar:users-group-rounded-linear",
      value: "1,234",
      subtitleKey: "dashboard.admin.activeUsers",
      color: "primary",
    },
    {
      titleKey: "dashboard.admin.institutions",
      icon: "solar:buildings-linear",
      value: "45",
      subtitleKey: "dashboard.admin.registeredInstitutions",
      color: "blue",
    },
    {
      titleKey: "dashboard.admin.courses",
      icon: "solar:book-linear",
      value: "328",
      subtitleKey: "dashboard.admin.totalCourses",
      color: "green",
    },
    {
      titleKey: "dashboard.admin.systemUptime",
      icon: "solar:chart-2-linear",
      value: "98%",
      subtitleKey: "dashboard.admin.last30Days",
      color: "orange",
    },
  ]);

  const getStatColorClasses = (color: DashboardStat["color"]) => {
    const colorMap = {
      primary:
        "bg-primary-100 dark:bg-primary-400/20 text-primary border-primary-200 dark:border-primary-400/40",
      blue: "bg-blue-100 dark:bg-blue-400/20 text-blue-600 dark:text-blue-400 border-blue-200 dark:border-blue-400/40",
      green:
        "bg-green-100 dark:bg-green-400/20 text-green-600 dark:text-green-400 border-green-200 dark:border-green-400/40",
      orange:
        "bg-orange-100 dark:bg-orange-400/20 text-orange-600 dark:text-orange-400 border-orange-200 dark:border-orange-400/40",
    };
    return colorMap[color];
  };

  return {
    adminStats,
    getStatColorClasses,
    t,
  };
}
