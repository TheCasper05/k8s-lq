export interface HelpCategory {
  id: string;
  title: string;
  description: string;
  icon: string;
  iconColor: string;
  articleCount: number;
}

export interface PopularArticle {
  id: string;
  title: string;
  category: string;
  readTime: number;
  rank: number;
}

export interface VideoTutorial {
  id: string;
  title: string;
  description: string;
  duration: string;
  thumbnail?: string;
}

export interface FAQ {
  id: string;
  question: string;
  answer?: string;
}

export interface QuickLink {
  id: string;
  label: string;
  icon: string;
  url: string;
  external: boolean;
}

export const useHelpCenterData = () => {
  // Mock data - will be replaced with API calls
  const categories = ref<HelpCategory[]>([
    {
      id: "getting-started",
      title: "Getting Started",
      description: "Learn the basics of Lingoquesto",
      icon: "solar:book-line-duotone",
      iconColor: "success",
      articleCount: 8,
    },
    {
      id: "creating-scenarios",
      title: "Creating Scenarios",
      description: "How to create and manage scenarios",
      icon: "solar:chat-round-dots-line-duotone",
      iconColor: "primary",
      articleCount: 12,
    },
    {
      id: "managing-classes",
      title: "Managing Classes",
      description: "Class setup and student management",
      icon: "solar:users-group-rounded-line-duotone",
      iconColor: "warning",
      articleCount: 10,
    },
    {
      id: "ai-tools",
      title: "AI Tools",
      description: "Using AI to enhance teaching",
      icon: "solar:star-line-duotone",
      iconColor: "secondary",
      articleCount: 6,
    },
    {
      id: "grading-feedback",
      title: "Grading & Feedback",
      description: "Review student work effectively",
      icon: "solar:document-text-line-duotone",
      iconColor: "danger",
      articleCount: 9,
    },
    {
      id: "settings-account",
      title: "Settings & Account",
      description: "Manage your account preferences",
      icon: "solar:settings-line-duotone",
      iconColor: "surface",
      articleCount: 7,
    },
  ]);

  const popularArticles = ref<PopularArticle[]>([
    {
      id: "1",
      title: "How to create your first AI scenario",
      category: "AI Tools",
      readTime: 5,
      rank: 1,
    },
    {
      id: "2",
      title: "Setting up your first class",
      category: "Managing Classes",
      readTime: 8,
      rank: 2,
    },
    {
      id: "3",
      title: "Understanding student progress reports",
      category: "Grading & Feedback",
      readTime: 6,
      rank: 3,
    },
    {
      id: "4",
      title: "Customizing your profile and preferences",
      category: "Settings & Account",
      readTime: 4,
      rank: 4,
    },
    {
      id: "5",
      title: "Best practices for scenario creation",
      category: "Creating Scenarios",
      readTime: 10,
      rank: 5,
    },
  ]);

  const videoTutorials = ref<VideoTutorial[]>([
    {
      id: "1",
      title: "Lingoquesto Platform Overview",
      description: "Learn the essentials in this step-by-step guide",
      duration: "8:32",
    },
    {
      id: "2",
      title: "Creating Your First Scenario",
      description: "A comprehensive guide to scenario creation",
      duration: "12:15",
    },
    {
      id: "3",
      title: "Managing Students and Classes",
      description: "Tips and tricks for effective class management",
      duration: "6:45",
    },
  ]);

  const faqs = ref<FAQ[]>([
    {
      id: "1",
      question: "How do I create a new scenario?",
    },
    {
      id: "2",
      question: "Can I customize my class settings?",
    },
    {
      id: "3",
      question: "How do I invite students to my class?",
    },
    {
      id: "4",
      question: "What AI features are available?",
    },
    {
      id: "5",
      question: "How do I export student progress reports?",
    },
  ]);

  const quickLinks = ref<QuickLink[]>([
    {
      id: "1",
      label: "Release Notes",
      icon: "solar:document-text-line-duotone",
      url: "#",
      external: true,
    },
    {
      id: "2",
      label: "API Documentation",
      icon: "solar:book-line-duotone",
      url: "#",
      external: true,
    },
    {
      id: "3",
      label: "Community Forum",
      icon: "solar:users-group-rounded-line-duotone",
      url: "#",
      external: true,
    },
    {
      id: "4",
      label: "Download Resources",
      icon: "solar:download-line-duotone",
      url: "#",
      external: true,
    },
  ]);

  return {
    categories,
    popularArticles,
    videoTutorials,
    faqs,
    quickLinks,
  };
};
