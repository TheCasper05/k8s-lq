/**
 * Locale persistence utilities for saving/loading user language preference
 */

import { LOCALE_STORAGE_KEY, LOCALE_COOKIE_KEY } from "../config";

/**
 * Save locale to localStorage
 */
export function saveLocale(locale: string): void {
  if (typeof window !== "undefined") {
    try {
      localStorage.setItem(LOCALE_STORAGE_KEY, locale);
    } catch (error) {
      console.warn("Failed to save locale to localStorage:", error);
    }
  }
}

/**
 * Load locale from localStorage
 */
export function loadLocale(): string | null {
  if (typeof window !== "undefined") {
    try {
      return localStorage.getItem(LOCALE_STORAGE_KEY);
    } catch (error) {
      console.warn("Failed to load locale from localStorage:", error);
      return null;
    }
  }
  return null;
}

/**
 * Clear saved locale
 */
export function clearLocale(): void {
  if (typeof window !== "undefined") {
    try {
      localStorage.removeItem(LOCALE_STORAGE_KEY);
    } catch (error) {
      console.warn("Failed to clear locale from localStorage:", error);
    }
  }
}

/**
 * Save locale to cookie (for SSR compatibility)
 */
export function saveLocaleToCookie(locale: string, days: number = 365): void {
  if (typeof document !== "undefined") {
    const expires = new Date();
    expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
    document.cookie = `${LOCALE_COOKIE_KEY}=${locale};expires=${expires.toUTCString()};path=/;SameSite=Lax`;
  }
}

/**
 * Load locale from cookie
 */
export function loadLocaleFromCookie(): string | null {
  if (typeof document !== "undefined") {
    const name = LOCALE_COOKIE_KEY + "=";
    const decodedCookie = decodeURIComponent(document.cookie);
    const ca = decodedCookie.split(";");
    for (let i = 0; i < ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) === " ") {
        c = c.substring(1);
      }
      if (c.indexOf(name) === 0) {
        return c.substring(name.length, c.length);
      }
    }
  }
  return null;
}
