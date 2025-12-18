import type { AccountType } from "./enums";

export type AuthUser = {
  id: string;
  display: string;
  email: string;
  has_usable_password: boolean;
  username: string;
  onboarding_completed: boolean;
  email_verified: boolean;
};

export type AuthMethod = {
  method: string;
  email: string;
};

export type AuthMetadata = {
  is_authenticated: boolean;
  access_token: string;
  refresh_token: string;
  email_verified?: boolean;
};

export type AuthError = {
  message: string;
  code: string;
  param?: string;
};

export type AuthFlow = {
  id: string;
  is_pending?: boolean;
};

export type LoginResponse = {
  status: number;
  errors?: AuthError[];
  data: {
    user?: AuthUser;
    methods?: AuthMethod[];
    errors?: AuthError[];
    flows?: AuthFlow[];
  };
  meta: AuthMetadata;
};

export type RegisterResponse = {
  status: number;
  errors?: AuthError[];
  data?: {
    user?: AuthUser;
    errors?: AuthError[];
    form_errors?: Record<string, unknown>;
    non_field_errors?: unknown;
    detail?: string;
    message?: string;
  };
  meta?: AuthMetadata;
};

export type RegisterFormData = {
  firstName?: string;
  lastName?: string;
  email: string;
  password: string;
  password2: string;
};

export type LoginFormData = {
  email: string;
  password: string;
};

export type Institution = {
  id: string;
  publicId?: string;
  name: string;
  slug: string;
  description: string;
  website: string;
  contactEmail: string;
  contactPhone?: string | null;
  address: string;
  city: string;
  country: string;
  timezone: string;
  logo: string;
  isActive: boolean;
  settings?: string;
  createdAt?: string;
  updatedAt?: string;
  deletedAt?: string | null;
};

export type UserProfileComplete = {
  id: string;
  publicId: string;
  primaryRole: AccountType;
  firstName: string;
  lastName: string;
  phone?: string | null;
  photo: string;
  birthday: string | null;
  country?: string | null;
  languagePreference: string;
  timezone: string;
  isActive: boolean;
  user: {
    id: string;
    email: string;
  };
};
