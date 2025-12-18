import { ref, computed } from "vue";
import { CEFRLevel, type Activity, type ActivityMetric, type ViewMode } from "~/types/activities";
import { getMockActivities, generateId } from "~/utils/mockActivities";

export const useActivities = () => {
  const activities = ref<Activity[]>([]);
  const loading = ref(false);
  const searchQuery = ref("");
  const levelFilter = ref<CEFRLevel | null>(null);
  const viewMode = ref<ViewMode>("grid");

  // Computed: Filtered activities
  const filteredActivities = computed(() => {
    return activities.value.filter((activity) => {
      const matchesSearch = activity.title.toLowerCase().includes(searchQuery.value.toLowerCase());
      const matchesLevel = !levelFilter.value || activity.level === levelFilter.value;
      return matchesSearch && matchesLevel;
    });
  });

  // Computed: Metrics
  const { t } = useI18n();

  const metrics = computed<ActivityMetric[]>(() => {
    const total = activities.value.length;
    const assigned = activities.value.reduce((sum, a) => sum + a.assignedClasses, 0);
    const avgAssignments = total > 0 ? Math.round(assigned / total) : 0;
    const favorites = activities.value.filter((a) => a.isFavorite).length;

    return [
      {
        id: "total",
        label: t("teacher.scenarios.metrics.total"),
        value: total,
        icon: "solar:file-text-line-duotone",
        color: "primary",
      },
      {
        id: "assigned",
        label: t("teacher.scenarios.metrics.assigned"),
        value: assigned,
        icon: "solar:users-group-rounded-line-duotone",
        color: "info",
      },
      {
        id: "avg",
        label: t("teacher.scenarios.metrics.avg"),
        value: avgAssignments,
        icon: "solar:chart-2-line-duotone",
        color: "success",
      },
      {
        id: "favorites",
        label: t("teacher.scenarios.metrics.favorites"),
        value: favorites,
        icon: "solar:star-line-duotone",
        color: "warning",
      },
    ];
  });

  // Fetch activities (mock)
  const fetchActivities = async () => {
    loading.value = true;
    try {
      // Simulate API delay
      await new Promise((resolve) => setTimeout(resolve, 500));
      activities.value = getMockActivities();
    } catch (error) {
      console.error("Error fetching activities:", error);
    } finally {
      loading.value = false;
    }
  };

  // Create activity (mock)
  const createActivity = (data: Partial<Activity>): Activity => {
    const newActivity: Activity = {
      id: generateId(),
      title: data.title || "New Activity",
      description: data.description || "",
      coverImage:
        data.coverImage || "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&h=450&fit=crop",
      level: data.level || CEFRLevel.A1,
      theme: data.theme || "General",
      learningObjective: data.learningObjective || "",
      aiAssistantRole: data.aiAssistantRole || "Assistant",
      studentRole: data.studentRole || "Student",
      assignedClasses: 0,
      totalStudents: 0,
      completions: 0,
      avgScore: 0,
      isFavorite: false,
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    activities.value.unshift(newActivity);
    return newActivity;
  };

  // Update activity (mock)
  const updateActivity = (id: string, data: Partial<Activity>): void => {
    const index = activities.value.findIndex((a) => a.id === id);
    if (index !== -1) {
      activities.value[index] = {
        ...activities.value[index],
        ...data,
        updatedAt: new Date(),
      };
    }
  };

  // Delete activity (mock)
  const deleteActivity = (id: string): void => {
    activities.value = activities.value.filter((a) => a.id !== id);
  };

  // Toggle favorite
  const toggleFavorite = (id: string): void => {
    const activity = activities.value.find((a) => a.id === id);
    if (activity) {
      activity.isFavorite = !activity.isFavorite;
      activity.updatedAt = new Date();
    }
  };

  return {
    // State
    activities,
    loading,
    searchQuery,
    levelFilter,
    viewMode,

    // Computed
    filteredActivities,
    metrics,

    // Methods
    fetchActivities,
    createActivity,
    updateActivity,
    deleteActivity,
    toggleFavorite,
  };
};
