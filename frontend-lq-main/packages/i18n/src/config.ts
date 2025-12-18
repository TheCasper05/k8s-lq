/**
 * Shared i18n configuration for all apps in the monorepo
 */

export interface LocaleConfig {
  code: string;
  name: string;
  dir: "ltr" | "rtl";
  flag: string;
  language?: string;
}

export const SUPPORTED_LOCALES: readonly LocaleConfig[] = [
  {
    code: "en",
    name: "English",
    dir: "ltr",
    flag: "flag:us-4x3",
    language: "en-US",
  },
  {
    code: "es",
    name: "Español",
    dir: "ltr",
    flag: "flag:es-4x3",
    language: "es-ES",
  },
  {
    code: "ar",
    name: "العربية",
    dir: "rtl",
    flag: "flag:sa-4x3",
    language: "ar-SA",
  },
  {
    code: "fr",
    name: "Français",
    dir: "ltr",
    flag: "flag:fr-4x3",
    language: "fr-FR",
  },
  {
    code: "de",
    name: "Deutsch",
    dir: "ltr",
    flag: "flag:de-4x3",
    language: "de-DE",
  },
  {
    code: "zh",
    name: "中文",
    dir: "ltr",
    flag: "flag:cn-4x3",
    language: "zh-CN",
  },
  {
    code: "it",
    name: "Italiano",
    dir: "ltr",
    flag: "flag:it-4x3",
    language: "it-IT",
  },
  {
    code: "pt",
    name: "Português",
    dir: "ltr",
    flag: "flag:br-4x3",
    language: "pt-BR",
  },
] as const;

export const DEFAULT_LOCALE = "en";
export const FALLBACK_LOCALE = "en";
export const LOCALE_COOKIE_KEY = "lq_locale";
export const LOCALE_STORAGE_KEY = "lq_locale";

export type SupportedLocale = (typeof SUPPORTED_LOCALES)[number]["code"];
