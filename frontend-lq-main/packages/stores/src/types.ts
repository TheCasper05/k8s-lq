export type LanguagePreferences = {
  nativeLanguage: string;
  languageToLearn: string;
  country: string;
};

export type PersonalInfo = {
  firstName: string;
  lastName: string;
  birthday: Date | null;
  school?: string;
};

export type InstitutionInfo = {
  institutionName: string;
  description: string;
  logo: File | null;
  website: string;
  contactEmail: string;
  address: string;
  city: string;
  country: string;
};
