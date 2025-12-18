import { ref } from "vue";
import type { Class } from "./types";

/**
 * Mock data generator for classes
 * Includes variety: some with students, some empty, different progress levels
 */
export function getMockClasses(): Class[] {
  const now = new Date();
  const oneMonthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
  const twoWeeksAgo = new Date(now.getTime() - 14 * 24 * 60 * 60 * 1000);
  const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

  return [
    {
      id: "1",
      name: "Business English Advanced",
      level: "C1",
      language: "English",
      languageCode: "us",
      description:
        "Advanced business English course focusing on professional communication, presentations, and negotiations",
      schedule: "Mon, Wed 10:00 AM",
      coverImage: "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=400",
      students: 12,
      avgProgress: 87,
      status: "active",
      ownerId: "owner1",
      ownerName: "Sarah Johnson",
      ownerEmail: "sarah.johnson@school.com",
      studentIds: ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10", "s11", "s12"],
      teacherIds: [],
      createdAt: oneMonthAgo.toISOString(),
      updatedAt: oneWeekAgo.toISOString(),
    },
    {
      id: "2",
      name: "Conversational Spanish",
      level: "B1",
      language: "Spanish",
      languageCode: "es",
      description: "Conversational Spanish practice for intermediate learners",
      schedule: "Tue, Thu 2:00 PM",
      coverImage: "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=400",
      students: 8,
      avgProgress: 65,
      status: "active",
      ownerId: "owner1",
      ownerName: "Sarah Johnson",
      ownerEmail: "sarah.johnson@school.com",
      studentIds: ["s13", "s14", "s15", "s16", "s17", "s18", "s19", "s20"],
      teacherIds: [],
      createdAt: twoWeeksAgo.toISOString(),
      updatedAt: oneWeekAgo.toISOString(),
    },
    {
      id: "3",
      name: "French for Beginners",
      level: "A2",
      language: "French",
      languageCode: "fr",
      description: "Introduction to French language and culture",
      schedule: "Mon, Wed, Fri 4:00 PM",
      coverImage: "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=400",
      students: 15,
      avgProgress: 42,
      status: "active",
      ownerId: "owner1",
      ownerName: "Sarah Johnson",
      ownerEmail: "sarah.johnson@school.com",
      studentIds: [
        "s21",
        "s22",
        "s23",
        "s24",
        "s25",
        "s26",
        "s27",
        "s28",
        "s29",
        "s30",
        "s31",
        "s32",
        "s33",
        "s34",
        "s35",
      ],
      teacherIds: [],
      createdAt: oneMonthAgo.toISOString(),
      updatedAt: twoWeeksAgo.toISOString(),
    },
    {
      id: "4",
      name: "German Grammar Intensive",
      level: "B2",
      language: "German",
      languageCode: "de",
      description: "Intensive German grammar course for advanced learners",
      schedule: "Wed 6:00 PM",
      coverImage: "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=400",
      students: 6,
      avgProgress: 91,
      status: "active",
      ownerId: "owner1",
      ownerName: "Sarah Johnson",
      ownerEmail: "sarah.johnson@school.com",
      studentIds: ["s36", "s37", "s38", "s39", "s40", "s41"],
      teacherIds: [],
      createdAt: oneMonthAgo.toISOString(),
      updatedAt: oneWeekAgo.toISOString(),
    },
    {
      id: "5",
      name: "Italian Culture & Language",
      level: "A1",
      language: "Italian",
      languageCode: "it",
      description: "Italian language and culture for complete beginners",
      schedule: "Sat 11:00 AM",
      coverImage: "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=400",
      students: 20,
      avgProgress: 28,
      status: "active",
      ownerId: "owner1",
      ownerName: "Sarah Johnson",
      ownerEmail: "sarah.johnson@school.com",
      studentIds: [
        "s42",
        "s43",
        "s44",
        "s45",
        "s46",
        "s47",
        "s48",
        "s49",
        "s50",
        "s51",
        "s52",
        "s53",
        "s54",
        "s55",
        "s56",
        "s57",
      ],
      teacherIds: [],
      createdAt: twoWeeksAgo.toISOString(),
      updatedAt: oneWeekAgo.toISOString(),
    },
    {
      id: "6",
      name: "English Writing Workshop",
      level: "B2",
      language: "English",
      languageCode: "us",
      description: "Advanced writing skills for academic and professional contexts",
      schedule: "Thu 3:00 PM",
      coverImage: "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=400",
      students: 0,
      avgProgress: 0,
      status: "no-students",
      ownerId: "owner1",
      ownerName: "Sarah Johnson",
      ownerEmail: "sarah.johnson@school.com",
      studentIds: [],
      teacherIds: [],
      createdAt: oneWeekAgo.toISOString(),
      updatedAt: oneWeekAgo.toISOString(),
    },
    {
      id: "7",
      name: "Portuguese Conversation",
      level: "A2",
      language: "Portuguese",
      languageCode: "pt",
      description: "Basic Portuguese conversation practice",
      schedule: "Flexible",
      coverImage: "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=400",
      students: 3,
      avgProgress: 15,
      status: "active",
      ownerId: "owner1",
      ownerName: "Sarah Johnson",
      ownerEmail: "sarah.johnson@school.com",
      studentIds: ["s58", "s59", "s60"],
      teacherIds: [],
      createdAt: oneWeekAgo.toISOString(),
      updatedAt: oneWeekAgo.toISOString(),
    },
    {
      id: "8",
      name: "Spanish Literature",
      level: "C2",
      language: "Spanish",
      languageCode: "es",
      description: "Advanced Spanish literature and analysis",
      schedule: "Tue 5:00 PM",
      coverImage: "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=400",
      students: 4,
      avgProgress: 95,
      status: "active",
      ownerId: "owner1",
      ownerName: "Sarah Johnson",
      ownerEmail: "sarah.johnson@school.com",
      studentIds: ["s61", "s62", "s63", "s64"],
      teacherIds: [],
      createdAt: oneMonthAgo.toISOString(),
      updatedAt: oneWeekAgo.toISOString(),
    },
    {
      id: "9",
      name: "Japanese Basics",
      level: "A1",
      language: "Japanese",
      languageCode: "jp",
      description: "Introduction to Japanese language and writing systems",
      schedule: "Mon, Fri 6:00 PM",
      coverImage: "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=400",
      students: 0,
      avgProgress: 0,
      status: "no-students",
      ownerId: "owner1",
      ownerName: "Sarah Johnson",
      ownerEmail: "sarah.johnson@school.com",
      studentIds: [],
      teacherIds: [],
      createdAt: oneWeekAgo.toISOString(),
      updatedAt: oneWeekAgo.toISOString(),
    },
    {
      id: "10",
      name: "English Pronunciation Mastery",
      level: "B1",
      language: "English",
      languageCode: "us",
      description: "Focus on improving pronunciation and accent reduction",
      schedule: "Wed 4:00 PM",
      coverImage: "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=400",
      students: 7,
      avgProgress: 58,
      status: "active",
      ownerId: "owner1",
      ownerName: "Sarah Johnson",
      ownerEmail: "sarah.johnson@school.com",
      studentIds: ["s65", "s66", "s67", "s68", "s69", "s70", "s71"],
      teacherIds: [],
      createdAt: twoWeeksAgo.toISOString(),
      updatedAt: oneWeekAgo.toISOString(),
    },
  ];
}

const STORAGE_KEY = "lq-classes";

/**
 * Load classes from localStorage
 */
export const loadClassesFromStorage = (): Class[] | null => {
  if (typeof window === "undefined") return null;

  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored) as Class[];
    }
  } catch (err) {
    // Failed to load from localStorage, return null
    console.error("Error loading classes from localStorage:", err);
  }
  return null;
};

/**
 * Save classes to localStorage
 */
export const saveClassesToStorage = (classesToSave: Class[]) => {
  if (typeof window === "undefined") return;

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(classesToSave));
  } catch (err) {
    // Failed to save to localStorage, silently fail
    console.error("Error saving classes to localStorage:", err);
  }
};

/**
 * Composable for managing classes data
 */
export const useClasses = () => {
  const classes = ref<Class[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const fetchClasses = () => {
    loading.value = true;
    error.value = null;

    try {
      // Try to load from localStorage first
      const storedClasses = loadClassesFromStorage();

      if (storedClasses && storedClasses.length > 0) {
        // Ensure all classes have studentIds and teacherIds initialized
        const normalizedClasses = storedClasses.map((cls) => ({
          ...cls,
          studentIds: cls.studentIds || [],
          teacherIds: cls.teacherIds || [],
          // Update students count based on studentIds length
          students: cls.studentIds?.length || cls.students || 0,
        }));
        classes.value = normalizedClasses;
        // Save normalized classes back to storage
        saveClassesToStorage(normalizedClasses);
      } else {
        // No stored data, use mock data and save it
        const mockClasses = getMockClasses();
        classes.value = mockClasses;
        saveClassesToStorage(mockClasses);
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : "Error fetching classes";
      // Fallback to mock data on error
      classes.value = getMockClasses();
    } finally {
      loading.value = false;
    }
  };

  const addClass = (newClass: Class) => {
    // Add the new class at the beginning of the array
    classes.value.unshift(newClass);
    // Save to localStorage
    saveClassesToStorage(classes.value);
  };

  const updateClass = (updatedClass: Class) => {
    // Always load from localStorage first to ensure we have the latest data
    const storedClasses = loadClassesFromStorage();
    if (storedClasses) {
      const storedIndex = storedClasses.findIndex((c) => c.id === updatedClass.id);
      if (storedIndex !== -1) {
        // Preserve existing studentIds and teacherIds if not provided
        const existingClass = storedClasses[storedIndex];
        const finalClass: Class = {
          ...updatedClass,
          studentIds: updatedClass.studentIds ?? existingClass.studentIds ?? [],
          teacherIds: updatedClass.teacherIds ?? existingClass.teacherIds ?? [],
          // Update students count based on studentIds length
          students: updatedClass.studentIds?.length ?? existingClass.studentIds?.length ?? updatedClass.students ?? 0,
          updatedAt: new Date().toISOString(),
        };
        storedClasses[storedIndex] = finalClass;
        // Save to localStorage
        saveClassesToStorage(storedClasses);
        // Update local state if it exists
        if (classes.value.length > 0) {
          const localIndex = classes.value.findIndex((c) => c.id === updatedClass.id);
          if (localIndex !== -1) {
            classes.value[localIndex] = finalClass;
          } else {
            // If not in local state, update the whole array
            classes.value = storedClasses;
          }
        }
      } else {
        // Class not found in storage, add it
        const finalClass: Class = {
          ...updatedClass,
          studentIds: updatedClass.studentIds ?? [],
          teacherIds: updatedClass.teacherIds ?? [],
          students: updatedClass.studentIds?.length ?? updatedClass.students ?? 0,
          updatedAt: new Date().toISOString(),
        };
        storedClasses.push(finalClass);
        saveClassesToStorage(storedClasses);
        if (classes.value.length > 0) {
          classes.value = storedClasses;
        }
      }
    } else {
      // No stored classes, create new array with just this class
      const finalClass: Class = {
        ...updatedClass,
        studentIds: updatedClass.studentIds ?? [],
        teacherIds: updatedClass.teacherIds ?? [],
        students: updatedClass.studentIds?.length ?? updatedClass.students ?? 0,
        updatedAt: new Date().toISOString(),
      };
      const newClasses = [finalClass];
      saveClassesToStorage(newClasses);
      if (classes.value.length > 0) {
        classes.value = newClasses;
      }
    }
  };

  return {
    classes,
    loading,
    error,
    fetchClasses,
    addClass,
    updateClass,
  };
};
