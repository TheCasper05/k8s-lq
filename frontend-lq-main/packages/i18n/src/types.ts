/**
 * Type definitions for i18n
 * These types will be augmented by generated types from scripts/generate-types.ts
 */

import type { SupportedLocale } from "./config";

export type { SupportedLocale };

// This will be augmented by generated types
export interface TranslationSchema {
  common: Record<string, string>;
  auth: Record<string, string>;
  nav: Record<string, string>;
  home: Record<string, string>;
  dashboard: Record<string, string>;
  teacher: Record<string, unknown>;
  student: Record<string, unknown>;
  errors: Record<string, string>;
  users: Record<string, string>;
}

// Placeholder for generated translation keys
// Will be replaced by scripts/generate-types.ts
export type TranslationKey = string;
