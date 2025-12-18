export enum CEFRLevel {
  A1 = "A1",
  A2 = "A2",
  B1 = "B1",
  B2 = "B2",
  C1 = "C1",
  C2 = "C2",
}

export interface Activity {
  id: string;
  title: string;
  description: string;
  coverImage: string;
  level: CEFRLevel;
  theme: string;
  learningObjective: string;
  aiAssistantRole: string;
  studentRole: string;
  assignedClasses: number;
  totalStudents: number;
  completions: number;
  avgScore: number;
  isFavorite: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface ActivityMetric {
  id: string;
  label: string;
  value: number | string;
  icon: string;
  color: "primary" | "info" | "success" | "warning" | "danger";
  trend?: string;
}

export interface ClassData {
  id: string;
  name: string;
  country: string;
  flag: string;
  level: CEFRLevel;
  studentCount: number;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export type ViewMode = "grid" | "list";

// Chart.js types (TODO: Import from chart.js when types are available)
export interface ChartConfig {
  data: {
    labels?: string[];
    datasets: Array<{
      label?: string;
      data: number[];
      backgroundColor?: string | string[];
      borderColor?: string;
      borderWidth?: number;
      tension?: number;
      fill?: boolean;
      pointRadius?: number;
      pointBackgroundColor?: string;
    }>;
  };
  options: {
    responsive?: boolean;
    maintainAspectRatio?: boolean;
    plugins?: {
      legend?: {
        display?: boolean;
      };
      tooltip?: {
        enabled?: boolean;
        callbacks?: Record<string, unknown>;
      };
    };
    scales?: {
      x?: {
        grid?: {
          display?: boolean;
          drawBorder?: boolean;
        };
        ticks?: {
          color?: string;
          font?: { size?: number };
        };
      };
      y?: {
        grid?: {
          color?: string;
          drawBorder?: boolean;
        };
        ticks?: {
          stepSize?: number;
          color?: string;
          font?: { size?: number };
        };
      };
    };
  };
}

export interface TopPerformer {
  id: string;
  name: string;
  className: string;
  score: number;
  rank: number;
  color: string;
  emoji: string;
  cardClass?: string;
  scoreClass?: string;
}

export interface AnalyticsInsight {
  id: string;
  icon: string;
  label: string;
  value: string;
}

export interface ActionButtonConfig {
  id: string;
  icon: string;
  label: string;
  severity?: string;
  outlined?: boolean;
  disabled?: boolean;
  class?: string;
  onClick?: () => void;
}

export interface AiSuggestion {
  id: string;
  title: string;
  description: string;
  icon: string;
  color: string;
}

export interface SidebarDetailItem {
  id: string;
  icon: string;
  iconClasses: string;
  label: string;
  value: string;
}
