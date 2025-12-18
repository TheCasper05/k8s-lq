import { ref } from "vue";
import type { Assignment } from "./types";

/**
 * Mock data generator for assignments by class
 * Includes variety: courses with sub-assignments, different types, some empty classes
 */
function getMockAssignments(classId: string): Assignment[] {
  const now = new Date();
  const oneWeekFromNow = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
  const twoWeeksFromNow = new Date(now.getTime() + 14 * 24 * 60 * 60 * 1000);
  const oneMonthFromNow = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000);

  // Class 1: Business English Advanced - Many assignments, including courses
  if (classId === "1") {
    return [
      {
        id: "a1",
        name: "Business Communication Course",
        type: "course",
        level: "C1",
        language: "en",
        description: "Complete course on business communication skills",
        dueDate: oneMonthFromNow.toISOString(),
        assignedStudents: 12,
        totalStudents: 12,
        progress: 75,
        isCourse: true,
        minutes: 180,
        viewTranscription: true,
        viewTranslation: false,
        viewHints: true,
        showScore: true,
        showProgress: true,
        subAssignments: [
          {
            id: "a1-1",
            name: "Email Writing Practice",
            type: "writing",
            level: "C1",
            language: "en",
            description: "Practice writing professional emails",
            dueDate: oneWeekFromNow.toISOString(),
            assignedStudents: 12,
            totalStudents: 12,
            progress: 85,
            parentId: "a1",
            minutes: 30,
            viewTranscription: false,
            viewTranslation: false,
            viewHints: true,
            showScore: true,
            showProgress: true,
          },
          {
            id: "a1-2",
            name: "Presentation Skills",
            type: "speaking",
            level: "C1",
            language: "en",
            description: "Practice giving business presentations",
            dueDate: twoWeeksFromNow.toISOString(),
            assignedStudents: 12,
            totalStudents: 12,
            progress: 70,
            parentId: "a1",
            minutes: 45,
            viewTranscription: true,
            viewTranslation: false,
            viewHints: true,
            showScore: true,
            showProgress: true,
          },
          {
            id: "a1-3",
            name: "Negotiation Vocabulary",
            type: "vocabulary",
            level: "C1",
            language: "en",
            description: "Learn key negotiation terms",
            dueDate: oneWeekFromNow.toISOString(),
            assignedStudents: 12,
            totalStudents: 12,
            progress: 90,
            parentId: "a1",
            minutes: 20,
            viewTranscription: false,
            viewTranslation: true,
            viewHints: true,
            showScore: true,
            showProgress: true,
          },
        ],
      },
      {
        id: "a2",
        name: "Listening: Conference Call",
        type: "listening",
        level: "C1",
        language: "en",
        description: "Practice understanding conference calls",
        dueDate: oneWeekFromNow.toISOString(),
        assignedStudents: 12,
        totalStudents: 12,
        progress: 68,
        minutes: 25,
        viewTranscription: true,
        viewTranslation: false,
        viewHints: false,
        showScore: true,
        showProgress: true,
      },
      {
        id: "a3",
        name: "Reading: Business Reports",
        type: "reading",
        level: "C1",
        language: "en",
        description: "Analyze and understand business reports",
        dueDate: twoWeeksFromNow.toISOString(),
        assignedStudents: 10,
        totalStudents: 12,
        progress: 45,
        minutes: 40,
        viewTranscription: false,
        viewTranslation: false,
        viewHints: true,
        showScore: true,
        showProgress: true,
      },
    ];
  }

  // Class 2: Conversational Spanish - Mix of activities
  if (classId === "2") {
    return [
      {
        id: "b1",
        name: "Daily Conversations",
        type: "activity",
        level: "B1",
        language: "es",
        description: "Practice everyday Spanish conversations",
        dueDate: oneWeekFromNow.toISOString(),
        assignedStudents: 8,
        totalStudents: 8,
        progress: 82,
        minutes: 30,
        viewTranscription: true,
        viewTranslation: true,
        viewHints: true,
        showScore: true,
        showProgress: true,
      },
      {
        id: "b2",
        name: "Spanish Vocabulary Builder",
        type: "vocabulary",
        level: "B1",
        language: "es",
        description: "Expand your Spanish vocabulary",
        dueDate: twoWeeksFromNow.toISOString(),
        assignedStudents: 6,
        totalStudents: 8,
        progress: 55,
        minutes: 20,
        viewTranscription: false,
        viewTranslation: true,
        viewHints: true,
        showScore: true,
        showProgress: true,
      },
    ];
  }

  // Class 3: French for Beginners - Many assignments
  if (classId === "3") {
    return [
      {
        id: "c1",
        name: "French Basics Course",
        type: "course",
        level: "A2",
        language: "fr",
        description: "Complete beginner French course",
        dueDate: oneMonthFromNow.toISOString(),
        assignedStudents: 15,
        totalStudents: 15,
        progress: 35,
        isCourse: true,
        minutes: 240,
        viewTranscription: true,
        viewTranslation: true,
        viewHints: true,
        showScore: true,
        showProgress: true,
        subAssignments: [
          {
            id: "c1-1",
            name: "Greetings and Introductions",
            type: "speaking",
            level: "A2",
            language: "fr",
            description: "Learn basic greetings",
            dueDate: oneWeekFromNow.toISOString(),
            assignedStudents: 15,
            totalStudents: 15,
            progress: 60,
            parentId: "c1",
            minutes: 15,
            viewTranscription: true,
            viewTranslation: true,
            viewHints: true,
            showScore: true,
            showProgress: true,
          },
          {
            id: "c1-2",
            name: "Numbers and Colors",
            type: "vocabulary",
            level: "A2",
            language: "fr",
            description: "Learn numbers and colors",
            dueDate: oneWeekFromNow.toISOString(),
            assignedStudents: 12,
            totalStudents: 15,
            progress: 40,
            parentId: "c1",
            minutes: 20,
            viewTranscription: false,
            viewTranslation: true,
            viewHints: true,
            showScore: true,
            showProgress: true,
          },
        ],
      },
      {
        id: "c2",
        name: "French Listening Practice",
        type: "listening",
        level: "A2",
        language: "fr",
        description: "Practice understanding spoken French",
        dueDate: twoWeeksFromNow.toISOString(),
        assignedStudents: 10,
        totalStudents: 15,
        progress: 25,
        minutes: 30,
        viewTranscription: true,
        viewTranslation: true,
        viewHints: true,
        showScore: true,
        showProgress: true,
      },
    ];
  }

  // Class 4: German Grammar Intensive - Few but focused assignments
  if (classId === "4") {
    return [
      {
        id: "d1",
        name: "Advanced German Grammar",
        type: "activity",
        level: "B2",
        language: "de",
        description: "Master complex German grammar structures",
        dueDate: oneWeekFromNow.toISOString(),
        assignedStudents: 6,
        totalStudents: 6,
        progress: 95,
        minutes: 60,
        viewTranscription: true,
        viewTranslation: false,
        viewHints: true,
        showScore: true,
        showProgress: true,
      },
      {
        id: "d2",
        name: "German Writing Practice",
        type: "writing",
        level: "B2",
        language: "de",
        description: "Practice writing in German",
        dueDate: twoWeeksFromNow.toISOString(),
        assignedStudents: 5,
        totalStudents: 6,
        progress: 88,
        minutes: 45,
        viewTranscription: false,
        viewTranslation: false,
        viewHints: true,
        showScore: true,
        showProgress: true,
      },
    ];
  }

  // Class 5: Italian Culture & Language - Many assignments for large class
  if (classId === "5") {
    return [
      {
        id: "e1",
        name: "Italian Greetings",
        type: "speaking",
        level: "A1",
        language: "it",
        description: "Learn basic Italian greetings",
        dueDate: oneWeekFromNow.toISOString(),
        assignedStudents: 20,
        totalStudents: 20,
        progress: 30,
        minutes: 20,
        viewTranscription: true,
        viewTranslation: true,
        viewHints: true,
        showScore: true,
        showProgress: true,
      },
      {
        id: "e2",
        name: "Italian Alphabet",
        type: "activity",
        level: "A1",
        language: "it",
        description: "Learn the Italian alphabet",
        dueDate: oneWeekFromNow.toISOString(),
        assignedStudents: 15,
        totalStudents: 20,
        progress: 20,
        minutes: 15,
        viewTranscription: true,
        viewTranslation: true,
        viewHints: true,
        showScore: true,
        showProgress: true,
      },
    ];
  }

  // Class 7: Portuguese Conversation - Few assignments
  if (classId === "7") {
    return [
      {
        id: "f1",
        name: "Basic Portuguese Phrases",
        type: "activity",
        level: "A2",
        language: "pt",
        description: "Learn essential Portuguese phrases",
        dueDate: oneWeekFromNow.toISOString(),
        assignedStudents: 3,
        totalStudents: 3,
        progress: 18,
        minutes: 25,
        viewTranscription: true,
        viewTranslation: true,
        viewHints: true,
        showScore: true,
        showProgress: true,
      },
    ];
  }

  // Class 8: Spanish Literature - Advanced assignments
  if (classId === "8") {
    return [
      {
        id: "g1",
        name: "Literary Analysis: Don Quixote",
        type: "reading",
        level: "C2",
        language: "es",
        description: "Analyze excerpts from Don Quixote",
        dueDate: twoWeeksFromNow.toISOString(),
        assignedStudents: 4,
        totalStudents: 4,
        progress: 98,
        minutes: 90,
        viewTranscription: false,
        viewTranslation: false,
        viewHints: false,
        showScore: true,
        showProgress: true,
      },
      {
        id: "g2",
        name: "Essay Writing: Spanish Literature",
        type: "writing",
        level: "C2",
        language: "es",
        description: "Write an essay on Spanish literature",
        dueDate: oneMonthFromNow.toISOString(),
        assignedStudents: 3,
        totalStudents: 4,
        progress: 75,
        minutes: 120,
        viewTranscription: false,
        viewTranslation: false,
        viewHints: false,
        showScore: true,
        showProgress: true,
      },
    ];
  }

  // Class 10: English Pronunciation - Focused assignments
  if (classId === "10") {
    return [
      {
        id: "h1",
        name: "Pronunciation Practice: Vowels",
        type: "speaking",
        level: "B1",
        language: "en",
        description: "Practice English vowel sounds",
        dueDate: oneWeekFromNow.toISOString(),
        assignedStudents: 7,
        totalStudents: 7,
        progress: 62,
        minutes: 30,
        viewTranscription: true,
        viewTranslation: false,
        viewHints: true,
        showScore: true,
        showProgress: true,
      },
      {
        id: "h2",
        name: "Listening: Accent Training",
        type: "listening",
        level: "B1",
        language: "en",
        description: "Train your ear to different English accents",
        dueDate: twoWeeksFromNow.toISOString(),
        assignedStudents: 5,
        totalStudents: 7,
        progress: 45,
        minutes: 35,
        viewTranscription: true,
        viewTranslation: false,
        viewHints: true,
        showScore: true,
        showProgress: true,
      },
    ];
  }

  // Classes 6 and 9: No assignments (empty classes)
  return [];
}

/**
 * Composable for managing class assignments
 */
export const useClassAssignments = () => {
  const assignments = ref<Assignment[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const fetchAssignments = (classId: string) => {
    loading.value = true;
    error.value = null;

    try {
      // TODO: Connect to GraphQL API
      // Mock data for now
      assignments.value = getMockAssignments(classId);
    } catch (err) {
      error.value = err instanceof Error ? err.message : "Error fetching assignments";
    } finally {
      loading.value = false;
    }
  };

  const addAssignment = (_assignment: Partial<Assignment>) => {
    // TODO: Implement add assignment
  };

  const updateAssignment = (_assignmentId: string, _updates: Partial<Assignment>) => {
    // TODO: Implement update assignment
  };

  const deleteAssignment = (_assignmentId: string) => {
    // TODO: Implement delete assignment
  };

  const duplicateAssignment = (_assignmentId: string) => {
    // TODO: Implement duplicate assignment
  };

  return {
    assignments,
    loading,
    error,
    fetchAssignments,
    addAssignment,
    updateAssignment,
    deleteAssignment,
    duplicateAssignment,
  };
};
