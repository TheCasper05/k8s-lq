/**
 * Types for Student Management Module
 * Based on ClassroomMembershipType from GraphQL schema
 */

export interface Student {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  photo?: string | null;
  // Mock fields (not in current GraphQL schema)
  level: string; // A1, A2, B1, B2, C1, C2
  progress: number; // 0-100 percentage
  activitiesCompleted: number;
  activitiesTotal: number;
  studyTimeMinutes: number;
  score: number; // 0-100
  enrolledAt?: string; // ISO date string
  skills?: {
    pronunciation?: number;
    vocabulary?: number;
    grammar?: number;
    fluency?: number;
    discourse?: number;
  };
}

export interface StudentStats {
  totalStudents: number;
  totalStudyHours: number;
  totalStudyMinutes: number;
  averageProgress: number;
  monthlyChangePercent: number;
  monthlyHoursChangePercent: number;
}

export interface StudentFilters {
  level: string | null;
  search: string;
}
