/**
 * RTL (Right-to-Left) utilities for handling Arabic and other RTL languages
 */

/**
 * Check if a locale uses RTL direction
 */
export function isRTL(locale: string): boolean {
  return locale === "ar";
}

/**
 * Set document direction based on locale
 */
export function setDocumentDir(locale: string): void {
  if (typeof document !== "undefined") {
    const dir = isRTL(locale) ? "rtl" : "ltr";
    document.documentElement.dir = dir;
    document.documentElement.lang = locale;
  }
}

/**
 * Get direction for a locale
 */
export function getDirection(locale: string): "ltr" | "rtl" {
  return isRTL(locale) ? "rtl" : "ltr";
}
