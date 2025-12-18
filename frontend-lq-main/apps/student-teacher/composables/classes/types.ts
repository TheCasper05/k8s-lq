/**
 * Types for Classes Management Module
 */

export interface Class {
  id: string;
  name: string;
  level: string; // A1, A2, B1, B2, C1, C2
  language: string; // e.g., "English", "Spanish"
  languageCode: string; // e.g., "en", "es" for flag
  description?: string | null;
  schedule?: string | null; // e.g., "Mon, Wed 10:00 AM" or "Flexible"
  coverImage?: string | null;
  students: number;
  avgProgress: number; // 0-100 percentage
  status: "active" | "inactive" | "no-students";
  isFavorite?: boolean;
  ownerId: string;
  ownerName?: string;
  ownerEmail?: string;
  studentIds?: string[]; // Array of student IDs in this class
  teacherIds?: string[]; // Array of teacher IDs (excluding owner)
  createdAt?: string;
  updatedAt?: string;
}

export interface ClassStats {
  totalClasses: number;
  activeClasses: number;
  totalStudents: number;
  avgPerClass: number;
}

export interface ClassFilters {
  level: string | null;
  search: string;
}

/**
 * Assignment types for class detail
 */
export type AssignmentType = "activity" | "course" | "vocabulary" | "speaking" | "writing" | "reading" | "listening";

export interface Assignment {
  id: string;
  name: string;
  type: AssignmentType;
  level: string | null; // A1, A2, B1, B2, C1, C2 or null if using classroom defaults
  language?: string | null; // Language code (e.g., "en", "es") or null if using classroom defaults
  description?: string | null;
  dueDate?: string | null;
  assignedStudents: number;
  totalStudents: number;
  progress: number; // 0-100 percentage
  isCourse?: boolean; // If true, it's a course with sub-assignments
  parentId?: string | null; // If this is a sub-assignment
  subAssignments?: Assignment[]; // Sub-assignments if it's a course
  minutes?: number; // Minimum time required
  viewTranscription?: boolean; // Allow viewing transcription
  viewTranslation?: boolean; // Allow viewing translation
  viewHints?: boolean; // Allow viewing hints
  nativeLanguage?: boolean; // Allow viewing in native language
  showScore?: boolean; // Show score to students
  showProgress?: boolean; // Show progress to students
  createdAt?: string;
  updatedAt?: string;
}

export interface AssignmentGrade {
  assignmentId: string;
  studentId: string;
  score?: number | null; // 0-100 percentage
  status: "pending" | "completed" | "graded" | "in_progress";
  skills?: {
    grammar?: number;
    pronunciation?: number;
    vocabulary?: number;
    fluency?: number;
    cohesion?: number;
  };
  cefrLevel?: string; // e.g., "B1", "A2"
  practiceTime?: string; // e.g., "2h 7m"
}

/**
 * Statistics types for class analytics
 */
export interface ClassStatistics {
  avgScore: number; // 0-100 percentage
  cefrLevel: string; // e.g., "B2"
  completionRate: number; // 0-100 percentage
  completionFraction: string; // e.g., "20/30"
  activeStudents: number;
  activeStudentsFraction: string; // e.g., "1/3"
  totalPracticeTime: string; // e.g., "245m"
}

export interface LeaderboardEntry {
  rank: number;
  studentId: string;
  studentName: string;
  studentPhoto?: string | null;
  score: number; // 0-100 percentage
  cefrLevel: string;
  completedCount: number;
  totalCount: number;
  practiceTime: string; // e.g., "245m" or "0m"
}

export interface AssignmentsChartData {
  labels: string[]; // Assignment names (abbreviated)
  datasets: Array<{
    label: string;
    data: number[];
    backgroundColor: string;
  }>;
}

export interface SkillsChartData {
  labels: string[]; // Skill names
  datasets: Array<{
    data: number[];
    backgroundColor: string[];
  }>;
}

export interface StudyTimeChartData {
  labels: string[]; // Dates
  datasets: Array<{
    label: string;
    data: number[];
    borderColor: string;
    backgroundColor: string;
    tension: number;
  }>;
}
