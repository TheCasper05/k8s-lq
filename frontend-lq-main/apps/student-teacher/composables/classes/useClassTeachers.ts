import { ref } from "vue";
import { loadClassesFromStorage, saveClassesToStorage } from "./useClasses";
import type { Class } from "./types";

export interface Teacher {
  id: string;
  name: string;
  email: string;
  photo?: string | null;
  isOwner?: boolean;
}

/**
 * Mock teachers data
 */
function getMockTeachers(): Teacher[] {
  return [
    {
      id: "t1",
      name: "Michael Chen",
      email: "michael.chen@school.com",
      photo: "https://i.pravatar.cc/150?img=12",
    },
    {
      id: "t2",
      name: "Emma Wilson",
      email: "emma.wilson@school.com",
      photo: "https://i.pravatar.cc/150?img=13",
    },
    {
      id: "t3",
      name: "James Brown",
      email: "james.brown@school.com",
      photo: "https://i.pravatar.cc/150?img=14",
    },
    {
      id: "t4",
      name: "Sarah Anderson",
      email: "sarah.anderson@school.com",
      photo: "https://i.pravatar.cc/150?img=19",
    },
    {
      id: "t5",
      name: "Robert Taylor",
      email: "robert.taylor@school.com",
      photo: "https://i.pravatar.cc/150?img=20",
    },
  ];
}

/**
 * Composable for managing class teachers
 */
export const useClassTeachers = () => {
  const teachers = ref<Teacher[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const fetchClassTeachers = (classItem: Class) => {
    loading.value = true;
    error.value = null;

    try {
      const allMockTeachers = getMockTeachers();
      const teacherMap = new Map(allMockTeachers.map((t) => [t.id, t]));

      // Get owner as teacher
      const ownerTeacher: Teacher = {
        id: classItem.ownerId,
        name: classItem.ownerName || "Teacher",
        email: classItem.ownerEmail || "",
        isOwner: true,
      };

      // Get other teachers (excluding owner)
      const otherTeachers =
        classItem.teacherIds?.map((id) => teacherMap.get(id)).filter((t): t is Teacher => t !== undefined) || [];

      // Combine owner and other teachers
      teachers.value = [ownerTeacher, ...otherTeachers];
    } catch (err) {
      error.value = err instanceof Error ? err.message : "Error fetching class teachers";
    } finally {
      loading.value = false;
    }
  };

  const addTeacher = (classId: string, teacherId: string) => {
    try {
      const storedClasses = loadClassesFromStorage();
      const classItem = storedClasses?.find((c) => c.id === classId);

      if (classItem) {
        const currentTeacherIds = classItem.teacherIds || [];
        if (!currentTeacherIds.includes(teacherId) && teacherId !== classItem.ownerId) {
          // Add teacher ID (excluding owner)
          const updatedTeacherIds = [...currentTeacherIds, teacherId];
          const updatedClass = {
            ...classItem,
            teacherIds: updatedTeacherIds,
            updatedAt: new Date().toISOString(),
          };

          // Update in storage
          if (storedClasses) {
            const updatedClasses = storedClasses.map((c) => (c.id === classId ? updatedClass : c));
            saveClassesToStorage(updatedClasses);
          }

          // Update local teachers list
          const allMockTeachers = getMockTeachers();
          const teacher = allMockTeachers.find((t) => t.id === teacherId);
          if (teacher) {
            teachers.value = [...teachers.value, teacher];
          }
        }
      }
    } catch (err) {
      // Error handling: silently fail or implement proper error notification
      console.error("Error adding teacher to class:", err);
    }
  };

  const removeTeacher = (classId: string, teacherId: string) => {
    try {
      const storedClasses = loadClassesFromStorage();
      const classItem = storedClasses?.find((c) => c.id === classId);

      if (classItem && teacherId !== classItem.ownerId) {
        // Cannot remove owner
        const currentTeacherIds = classItem.teacherIds || [];
        const updatedTeacherIds = currentTeacherIds.filter((id) => id !== teacherId);
        const updatedClass = {
          ...classItem,
          teacherIds: updatedTeacherIds,
          updatedAt: new Date().toISOString(),
        };

        // Update in storage
        if (storedClasses) {
          const updatedClasses = storedClasses.map((c) => (c.id === classId ? updatedClass : c));
          saveClassesToStorage(updatedClasses);
        }

        // Update local teachers list
        teachers.value = teachers.value.filter((t) => t.id !== teacherId);
      }
    } catch (err) {
      // Error handling: silently fail or implement proper error notification
      console.error("Error removing teacher from class:", err);
    }
  };

  return {
    teachers,
    loading,
    error,
    fetchClassTeachers,
    addTeacher,
    removeTeacher,
  };
};
