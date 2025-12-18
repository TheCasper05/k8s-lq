import { ref } from "vue";
import type { Student } from "./types";

/**
 * Mock data generator for students
 * Based on ClassroomMembershipType structure from GraphQL schema
 */
function getMockStudents(): Student[] {
  return [
    {
      id: "1",
      firstName: "Susana",
      lastName: "Casas",
      email: "susanacasas16@gmail.com",
      photo: "https://i.pravatar.cc/150?img=1",
      level: "A1",
      progress: 15,
      activitiesCompleted: 3,
      activitiesTotal: 20,
      studyTimeMinutes: 45,
      score: 68,
      enrolledAt: "2024-10-15T10:30:00.000Z",
      skills: {
        pronunciation: 65,
        vocabulary: 70,
        grammar: 68,
        fluency: 60,
      },
    },
    {
      id: "2",
      firstName: "Student",
      lastName: "LingoQuesto",
      email: "student@lingoquest.com",
      photo: "https://i.pravatar.cc/150?img=2",
      level: "A1",
      progress: 80,
      activitiesCompleted: 16,
      activitiesTotal: 20,
      studyTimeMinutes: 245,
      score: 92,
      enrolledAt: "2024-10-15T10:30:00.000Z",
      skills: {
        pronunciation: 74,
        vocabulary: 88,
        grammar: 74,
        fluency: 67,
      },
    },
    {
      id: "3",
      firstName: "David",
      lastName: "Garzon",
      email: "david010@gmail.com",
      photo: "https://i.pravatar.cc/150?img=3",
      level: "B1",
      progress: 45,
      activitiesCompleted: 9,
      activitiesTotal: 20,
      studyTimeMinutes: 180,
      score: 85,
      enrolledAt: "2024-09-20T14:00:00.000Z",
      skills: {
        pronunciation: 82,
        vocabulary: 86,
        grammar: 84,
        fluency: 80,
      },
    },
    {
      id: "4",
      firstName: "Valentina",
      lastName: "Castro",
      email: "angievalentina14@gmail.com",
      photo: "https://i.pravatar.cc/150?img=4",
      level: "B2",
      progress: 92,
      activitiesCompleted: 18,
      activitiesTotal: 20,
      studyTimeMinutes: 410,
      score: 95,
      enrolledAt: "2024-08-10T09:15:00.000Z",
      skills: {
        pronunciation: 93,
        vocabulary: 96,
        grammar: 95,
        fluency: 92,
      },
    },
    {
      id: "5",
      firstName: "Carlos",
      lastName: "Mendoza",
      email: "cmendoza@gmail.com",
      photo: "https://i.pravatar.cc/150?img=5",
      level: "C1",
      progress: 67,
      activitiesCompleted: 13,
      activitiesTotal: 20,
      studyTimeMinutes: 275,
      score: 88,
      enrolledAt: "2024-07-05T11:45:00.000Z",
      skills: {
        pronunciation: 87,
        vocabulary: 89,
        grammar: 88,
        fluency: 85,
      },
    },
    {
      id: "6",
      firstName: "Ana",
      lastName: "García",
      email: "anagarcia@gmail.com",
      photo: "https://i.pravatar.cc/150?img=6",
      level: "A2",
      progress: 35,
      activitiesCompleted: 7,
      activitiesTotal: 20,
      studyTimeMinutes: 135,
      score: 72,
      enrolledAt: "2024-11-01T16:20:00.000Z",
      skills: {
        pronunciation: 70,
        vocabulary: 75,
        grammar: 71,
        fluency: 68,
      },
    },
  ];
}

/**
 * Composable for managing students data
 */
export const useStudents = () => {
  const students = ref<Student[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const fetchStudents = () => {
    loading.value = true;
    error.value = null;

    try {
      // Mock data for now
      students.value = getMockStudents();
    } catch (err) {
      error.value = err instanceof Error ? err.message : "Error fetching students";
    } finally {
      loading.value = false;
    }
  };

  return {
    students,
    loading,
    error,
    fetchStudents,
  };
};
