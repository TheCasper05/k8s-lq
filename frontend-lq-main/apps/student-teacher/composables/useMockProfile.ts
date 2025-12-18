export interface MockUserProfile {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  avatar?: string;
  nativeLanguage: string;
  learningLanguages: string[];
  bio: string;
  phone?: string;
  location?: string;
  institution?: string;
  memberSince?: string;
  grade: string;
  classrooms: string[];
  twoFactorEnabled: boolean;
}

export const mockUserProfile: MockUserProfile = {
  id: "STU-2024-156",
  firstName: "Carlos",
  lastName: "Rodríguez",
  email: "carlos.rodriguez@estudiante.lingoquest.com",
  avatar: undefined, // null para usar iniciales
  nativeLanguage: "English",
  learningLanguages: ["English", "Aleman"],
  bio: "Estudiante apasionado por aprender idiomas. Me encanta la cultura inglesa y francesa, y aspiro a ser políglota. En mi tiempo libre disfruto viendo series en inglés y practicando conversación con amigos.",
  phone: "+34 655 789 123",
  location: "Barcelona, España",
  institution: "Colegio x o independiente",
  memberSince: "julio de 2024",
  grade: "3° ESO",
  classrooms: ["Aula B-13", "Aula B-12", "Aula B-15"],
  twoFactorEnabled: false,
};

export function useMockProfile() {
  const profile = ref<MockUserProfile>({ ...mockUserProfile });

  const updateProfile = (updates: Partial<MockUserProfile>) => {
    profile.value = { ...profile.value, ...updates };
  };

  return {
    profile,
    updateProfile,
  };
}
