import { ref, computed } from "vue";
import type { TeacherDashboardData } from "./types";

/**
 * Composable for teacher dashboard mock data
 * This will be replaced with real API calls later
 */
export const useTeacherDashboardData = () => {
  // Loading and error states
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // Mock data - will be replaced with API calls
  const mockData = ref<TeacherDashboardData>({
    quickActions: [
      {
        id: "create-activity",
        title: "Create New Activity",
        description: "Generate custom learning scenarios in seconds",
        icon: "solar:star-circle-line-duotone",
        route: "/scenarios/new",
        variant: "primary",
        badge: "AI Powered",
      },
      {
        id: "browse-scenarios",
        title: "Browse Scenarios",
        description: "View and assign existing scenarios to classes",
        icon: "solar:document-text-line-duotone",
        route: "/scenarios",
        variant: "default",
        badge: "Library",
      },
      {
        id: "view-classes",
        title: "View Classes",
        description: "Manage your classes and student progress",
        icon: "solar:users-group-rounded-line-duotone",
        route: "/classes",
        variant: "default",
        badge: "Manage",
      },
    ],
    metrics: {
      totalStudents: {
        value: 127,
        change: 8,
        label: "Total Students",
        i18nKey: "totalstudents",
        icon: "solar:users-group-rounded-line-duotone",
        color: "info",
      },
      activeScenarios: {
        value: "18/20",
        change: 3,
        label: "scenarios vs completed",
        i18nKey: "activescenarios",
        icon: "solar:document-text-line-duotone",
        color: "success",
      },
      totalPracticeTime: {
        value: "20 hrs",
        change: 5,
        label: "total student practice time",
        i18nKey: "totalstudentpracticetime",
        icon: "solar:clock-circle-line-duotone",
        color: "primary",
      },
      totalTimeSaved: {
        value: "40 Hrs",
        change: 12,
        label: "total teacher time saved",
        i18nKey: "totalteachertimesaved",
        icon: "solar:chart-2-line-duotone",
        color: "warning",
        tooltip: "time saved creating activities, implementing activities, giving feedback, and evaluating by our AI",
      },
    },
    needsAttention: [
      {
        id: "1",
        title: "12 assignments to review",
        description: "Business English Advanced",
        actionLabel: "Review",
        actionRoute: "/assignments/pending",
        severity: "warning",
      },
      {
        id: "2",
        title: "3 students inactive for 5+ days",
        description: "Conversational Spanish",
        actionLabel: "View",
        actionRoute: "/classes/123",
        severity: "danger",
      },
      {
        id: "3",
        title: "Class average improved by 15%",
        description: "English for Beginners",
        actionLabel: "Details",
        actionRoute: "/classes/456",
        severity: "success",
      },
    ],
    recentActivity: [
      {
        id: "1",
        type: "completion",
        title: 'Emma Wilson completed "Restaurant Ordering"',
        description: "Score: 92% • 5 min ago",
        timestamp: new Date(Date.now() - 5 * 60 * 1000), // 5 minutes ago
        icon: "solar:check-circle-line-duotone",
        studentName: "Emma Wilson",
        studentAvatar: undefined,
      },
      {
        id: "2",
        type: "assignment",
        title: "Scenario assigned to Business English Advanced ",
        description: '"Job Interview Practice"• 23 min ago',
        timestamp: new Date(Date.now() - 23 * 60 * 1000), // 23 minutes ago
        icon: "solar:book-line-duotone",
      },
      {
        id: "3",
        type: "assignment",
        title: "New scenario created ",
        description: '"Hotel Reservation" • 2 hours ago',
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
        icon: "solar:star-circle-line-duotone",
      },
    ],
    recentCompletions: [
      {
        id: "1",
        studentName: "Emma Wilson",
        activityName: "Restaurant Ordering",
        completedAt: new Date(Date.now() - 5 * 60 * 1000), // 5 minutes ago
        score: 92,
      },
      {
        id: "2",
        studentName: "Lucas Smith",
        activityName: "Airport Check-in",
        completedAt: new Date(Date.now() - 12 * 60 * 1000), // 12 minutes ago
        score: 88,
      },
      {
        id: "3",
        studentName: "Sofia Garcia",
        activityName: "Job Interview",
        completedAt: new Date(Date.now() - 60 * 60 * 1000), // 1 hour ago
        score: 95,
      },
      {
        id: "4",
        studentName: "James Chen",
        activityName: "Hotel Reservation",
        completedAt: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
        score: 85,
      },
    ],
    upcomingClasses: [
      {
        id: "1",
        name: "Business English Advanced",
        time: "2:00 PM",
        dateLabel: "Today",
        studentCount: 24,
        level: "Advanced",
      },
      {
        id: "2",
        name: "Business English Advanced",
        time: "2:00 PM",
        dateLabel: "Today",
        studentCount: 20,
        level: "Advanced",
      },
      {
        id: "3",
        name: "Business English Advanced",
        time: "10:00 AM",
        dateLabel: "Tomorrow",
        studentCount: 34,
        level: "Advanced",
      },
    ],
  });

  const quickActions = computed(() => mockData.value.quickActions);
  const metrics = computed(() => mockData.value.metrics);
  const needsAttention = computed(() => mockData.value.needsAttention);
  const recentActivity = computed(() => mockData.value.recentActivity);
  const recentCompletions = computed(() => mockData.value.recentCompletions);
  const upcomingClasses = computed(() => mockData.value.upcomingClasses);

  // Calculate total time saved based on assigned activities
  // Mock calculation: 15 minutes per assigned activity
  const calculateTimeSaved = (assignedActivities: number): string => {
    const totalMinutes = assignedActivities * 15;
    const hours = Math.floor(totalMinutes / 60);
    return `${hours} Hrs`;
  };

  // Function to fetch data (currently mock, will be replaced with API call)
  const fetchDashboardData = async () => {
    try {
      isLoading.value = true;
      error.value = null;

      // Simulate API call delay
      await new Promise((resolve) => setTimeout(resolve, 500));

      // In the future, replace this with actual API call:
      // const response = await api.get('/teacher/dashboard');
      // mockData.value = response.data;

      isLoading.value = false;
    } catch (err) {
      error.value = err instanceof Error ? err.message : "Failed to load dashboard data";
      isLoading.value = false;
    }
  };

  // Initialize data on mount (for future API integration)
  // fetchDashboardData();

  return {
    quickActions,
    metrics,
    needsAttention,
    recentActivity,
    recentCompletions,
    upcomingClasses,
    calculateTimeSaved,
    isLoading,
    error,
    fetchDashboardData,
  };
};
