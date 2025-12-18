import { computed } from "vue";
import type { Student } from "../students/types";
import type {
  Assignment,
  AssignmentGrade,
  ClassStatistics,
  LeaderboardEntry,
  AssignmentsChartData,
  SkillsChartData,
  StudyTimeChartData,
} from "./types";

/**
 * Composable for calculating class statistics
 */
export const useClassStatistics = (students: Student[], assignments: Assignment[], grades: AssignmentGrade[]) => {
  // Helper function to parse practice time string to minutes
  const parsePracticeTime = (timeStr?: string): number => {
    if (!timeStr) return 0;
    const hourMatch = timeStr.match(/(\d+)h/);
    const minMatch = timeStr.match(/(\d+)m/);
    const hours = hourMatch ? Number.parseInt(hourMatch[1]) : 0;
    const minutes = minMatch ? Number.parseInt(minMatch[1]) : 0;
    return hours * 60 + minutes;
  };

  // Helper function to format minutes to time string
  const formatPracticeTime = (minutes: number): string => {
    if (minutes === 0) return "0m";
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0 && mins > 0) {
      return `${hours}h ${mins}m`;
    } else if (hours > 0) {
      return `${hours}h`;
    } else {
      return `${mins}m`;
    }
  };

  // Helper function to get CEFR level from score
  const getCefrLevel = (score: number): string => {
    if (score >= 95) return "C2";
    if (score >= 85) return "C1";
    if (score >= 75) return "B2";
    if (score >= 65) return "B1";
    if (score >= 55) return "A2";
    return "A1";
  };

  // Calculate overall class statistics
  const statistics = computed<ClassStatistics>(() => {
    // Calculate average score from graded assignments
    const gradedGrades = grades.filter((g) => g.score !== null && g.score !== undefined);
    const avgScore =
      gradedGrades.length > 0
        ? Math.round(gradedGrades.reduce((sum, g) => sum + (g.score || 0), 0) / gradedGrades.length)
        : 0;

    // Calculate completion rate
    const totalAssignments = students.length * assignments.length;
    const completedAssignments = grades.filter((g) => g.status === "completed" || g.status === "graded").length;
    const completionRate = totalAssignments > 0 ? Math.round((completedAssignments / totalAssignments) * 100) : 0;

    // Calculate active students (students with at least one completed/graded assignment in last 30 days)
    const activeStudentIds = new Set(
      grades.filter((g) => g.status === "completed" || g.status === "graded").map((g) => g.studentId),
    );

    // Calculate total practice time
    const totalMinutes = grades.reduce((sum, g) => sum + parsePracticeTime(g.practiceTime), 0);

    return {
      avgScore,
      cefrLevel: getCefrLevel(avgScore),
      completionRate,
      completionFraction: `${completedAssignments}/${totalAssignments}`,
      activeStudents: activeStudentIds.size,
      activeStudentsFraction: `${activeStudentIds.size}/${students.length}`,
      totalPracticeTime: formatPracticeTime(totalMinutes),
    };
  });

  // Calculate leaderboard data
  const leaderboard = computed<LeaderboardEntry[]>(() => {
    const studentStats = students.map((student) => {
      // Get all grades for this student
      const studentGrades = grades.filter((g) => g.studentId === student.id);
      const gradedGrades = studentGrades.filter((g) => g.score !== null && g.score !== undefined);

      // Calculate average score
      const score =
        gradedGrades.length > 0
          ? Math.round(gradedGrades.reduce((sum, g) => sum + (g.score || 0), 0) / gradedGrades.length)
          : 0;

      // Calculate completed count
      const completedCount = studentGrades.filter((g) => g.status === "completed" || g.status === "graded").length;

      // Calculate total practice time
      const totalMinutes = studentGrades.reduce((sum, g) => sum + parsePracticeTime(g.practiceTime), 0);

      return {
        studentId: student.id,
        studentName: `${student.firstName} ${student.lastName}`,
        studentPhoto: student.photo || null,
        score,
        cefrLevel: getCefrLevel(score),
        completedCount,
        totalCount: assignments.length,
        practiceTime: formatPracticeTime(totalMinutes),
        practiceMinutes: totalMinutes, // For sorting
      };
    });

    // Sort by score (descending), then by practice time (descending)
    const sorted = studentStats.sort((a, b) => {
      if (b.score !== a.score) return b.score - a.score;
      return (b.practiceMinutes || 0) - (a.practiceMinutes || 0);
    });

    // Add rank
    return sorted.map((entry, index) => ({
      rank: index + 1,
      studentId: entry.studentId,
      studentName: entry.studentName,
      studentPhoto: entry.studentPhoto,
      score: entry.score,
      cefrLevel: entry.cefrLevel,
      completedCount: entry.completedCount,
      totalCount: entry.totalCount,
      practiceTime: entry.practiceTime,
    }));
  });

  // Generate assignments chart data
  const assignmentsChartData = computed<AssignmentsChartData>(() => {
    const labels = assignments.map((a) => {
      // Abbreviate long names
      const name = a.name;
      if (name.length > 15) {
        const words = name.split(" ");
        if (words.length > 1) {
          return words.map((w) => w.substring(0, 4)).join(". ");
        }
        return name.substring(0, 12) + "...";
      }
      return name;
    });

    const data = assignments.map((assignment) => {
      const assignmentGrades = grades.filter((g) => g.assignmentId === assignment.id);
      const completed = assignmentGrades.filter((g) => g.status === "completed" || g.status === "graded").length;
      const total = students.length;
      return total > 0 ? completed / total : 0;
    });

    return {
      labels,
      datasets: [
        {
          label: "Completion Rate",
          data,
          backgroundColor: "#8b5cf6", // Purple color matching the mockup
        },
      ],
    };
  });

  // Generate skills chart data
  const skillsChartData = computed<SkillsChartData>(() => {
    // Aggregate skills from all graded assignments
    const skillTotals = {
      pronunciation: 0,
      vocabulary: 0,
      grammar: 0,
      fluency: 0,
    };
    const skillCounts = {
      pronunciation: 0,
      vocabulary: 0,
      grammar: 0,
      fluency: 0,
    };

    grades.forEach((grade) => {
      if (grade.skills) {
        if (grade.skills.pronunciation !== undefined) {
          skillTotals.pronunciation += grade.skills.pronunciation;
          skillCounts.pronunciation++;
        }
        if (grade.skills.vocabulary !== undefined) {
          skillTotals.vocabulary += grade.skills.vocabulary;
          skillCounts.vocabulary++;
        }
        if (grade.skills.grammar !== undefined) {
          skillTotals.grammar += grade.skills.grammar;
          skillCounts.grammar++;
        }
        if (grade.skills.fluency !== undefined) {
          skillTotals.fluency += grade.skills.fluency;
          skillCounts.fluency++;
        }
      }
    });

    const skillAverages = {
      pronunciation:
        skillCounts.pronunciation > 0 ? Math.round(skillTotals.pronunciation / skillCounts.pronunciation) : 75,
      vocabulary: skillCounts.vocabulary > 0 ? Math.round(skillTotals.vocabulary / skillCounts.vocabulary) : 89,
      grammar: skillCounts.grammar > 0 ? Math.round(skillTotals.grammar / skillCounts.grammar) : 75,
      fluency: skillCounts.fluency > 0 ? Math.round(skillTotals.fluency / skillCounts.fluency) : 67,
    };

    return {
      labels: ["Pronun.", "Gram.", "Vocab.", "Fluency"],
      datasets: [
        {
          data: [skillAverages.pronunciation, skillAverages.grammar, skillAverages.vocabulary, skillAverages.fluency],
          backgroundColor: [
            "#3b82f6", // Blue
            "#f59e0b", // Orange
            "#10b981", // Green
            "#ef4444", // Red
          ],
        },
      ],
    };
  });

  // Generate study time chart data (mock data for timeline)
  const studyTimeChartData = computed<StudyTimeChartData>(() => {
    // Mock data for the last 3 dates showing study time trend
    // In a real implementation, this would aggregate actual practice sessions by date
    return {
      labels: ["11/20", "11/25", "11/28"],
      datasets: [
        {
          label: "Study Time (minutes)",
          data: [80, 85, 90],
          borderColor: "#f59e0b", // Orange color
          backgroundColor: "rgba(245, 158, 11, 0.1)",
          tension: 0.4,
        },
      ],
    };
  });

  return {
    statistics,
    leaderboard,
    assignmentsChartData,
    skillsChartData,
    studyTimeChartData,
  };
};
