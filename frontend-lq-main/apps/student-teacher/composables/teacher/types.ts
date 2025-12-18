export interface QuickAction {
  id: string;
  title: string;
  description: string;
  icon: string;
  route: string;
  variant: "primary" | "default";
  badge?: string;
}

export interface MetricValue {
  value: number | string;
  change?: number;
  label: string;
  i18nKey: string; // Key for i18n translation (e.g., "totalstudents", "activescenarios")
  icon: string;
  color: "primary" | "success" | "info" | "warning";
  tooltip?: string;
}

export interface DashboardMetrics {
  totalStudents: MetricValue;
  activeScenarios: MetricValue;
  totalPracticeTime: MetricValue;
  totalTimeSaved: MetricValue;
}

export interface AttentionItem {
  id: string;
  title: string;
  description: string;
  actionLabel: string;
  actionRoute: string;
  severity: "success" | "warning" | "danger";
}

export interface ActivityItem {
  id: string;
  type: "assignment" | "completion" | "class" | "student";
  title: string;
  description: string;
  timestamp: Date;
  icon: string;
  studentAvatar?: string;
  studentName?: string;
}

export interface CompletionItem {
  id: string;
  studentName: string;
  studentAvatar?: string;
  activityName: string;
  completedAt: Date;
  score?: number;
}

export interface UpcomingClass {
  id: string;
  name: string;
  time: string;
  dateLabel?: string; // "Today" or "Tomorrow"
  studentCount: number;
  level: string;
}

export interface TeacherDashboardData {
  quickActions: QuickAction[];
  metrics: DashboardMetrics;
  needsAttention: AttentionItem[];
  recentActivity: ActivityItem[];
  recentCompletions: CompletionItem[];
  upcomingClasses: UpcomingClass[];
}
