/**
 * @lq/i18n - Shared i18n utilities and configuration for LingoQuesto monorepo
 *
 * This package provides:
 * - Shared locale configuration (SUPPORTED_LOCALES, DEFAULT_LOCALE, etc.)
 * - RTL support utilities for Arabic and other RTL languages
 * - Locale persistence helpers (localStorage + cookies)
 * - Composables for locale switching
 *
 * NOTE: Translation files are managed by each app individually.
 * This package does NOT contain translations due to bundler limitations.
 */

// Configuration
export {
  SUPPORTED_LOCALES,
  DEFAULT_LOCALE,
  FALLBACK_LOCALE,
  LOCALE_COOKIE_KEY,
  LOCALE_STORAGE_KEY,
  type LocaleConfig,
  type SupportedLocale,
} from "./config";

// Utilities
export { isRTL, setDocumentDir, getDirection } from "./utils/rtl";
export { saveLocale, loadLocale, clearLocale, saveLocaleToCookie, loadLocaleFromCookie } from "./utils/persistence";

// Composables
export { useLocaleSwitch } from "./composables/useLocaleSwitch";
