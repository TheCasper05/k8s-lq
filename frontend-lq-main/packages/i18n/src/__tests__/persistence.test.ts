import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { saveLocale, loadLocale, clearLocale, saveLocaleToCookie, loadLocaleFromCookie } from "../utils/persistence";
import { LOCALE_STORAGE_KEY, LOCALE_COOKIE_KEY } from "../config";

describe("Persistence Utilities", () => {
  beforeEach(() => {
    // Clear localStorage and cookies before each test
    localStorage.clear();
    document.cookie.split(";").forEach((c) => {
      document.cookie = c.replace(/^ +/, "").replace(/=.*/, `=;expires=${new Date().toUTCString()};path=/`);
    });
  });

  afterEach(() => {
    // Clean up after each test
    localStorage.clear();
    document.cookie.split(";").forEach((c) => {
      document.cookie = c.replace(/^ +/, "").replace(/=.*/, `=;expires=${new Date().toUTCString()};path=/`);
    });
  });

  describe("LocalStorage", () => {
    describe("saveLocale", () => {
      it("should save locale to localStorage", () => {
        saveLocale("es");
        expect(localStorage.getItem(LOCALE_STORAGE_KEY)).toBe("es");
      });

      it("should overwrite existing locale", () => {
        saveLocale("en");
        expect(localStorage.getItem(LOCALE_STORAGE_KEY)).toBe("en");

        saveLocale("fr");
        expect(localStorage.getItem(LOCALE_STORAGE_KEY)).toBe("fr");
      });

      it("should handle different locales", () => {
        const locales = ["en", "es", "ar", "fr", "de", "zh"];
        locales.forEach((locale) => {
          saveLocale(locale);
          expect(localStorage.getItem(LOCALE_STORAGE_KEY)).toBe(locale);
        });
      });
    });

    describe("loadLocale", () => {
      it("should load saved locale from localStorage", () => {
        localStorage.setItem(LOCALE_STORAGE_KEY, "es");
        expect(loadLocale()).toBe("es");
      });

      it("should return null if no locale is saved", () => {
        expect(loadLocale()).toBeNull();
      });

      it("should return the correct locale after saving", () => {
        saveLocale("ar");
        expect(loadLocale()).toBe("ar");
      });
    });

    describe("clearLocale", () => {
      it("should remove locale from localStorage", () => {
        saveLocale("en");
        expect(localStorage.getItem(LOCALE_STORAGE_KEY)).toBe("en");

        clearLocale();
        expect(localStorage.getItem(LOCALE_STORAGE_KEY)).toBeNull();
      });

      it("should not throw error if no locale exists", () => {
        expect(() => clearLocale()).not.toThrow();
      });

      it("should clear locale completely", () => {
        saveLocale("fr");
        clearLocale();
        expect(loadLocale()).toBeNull();
      });
    });
  });

  describe("Cookies", () => {
    describe("saveLocaleToCookie", () => {
      it("should save locale to cookie", () => {
        saveLocaleToCookie("es");
        const cookie = loadLocaleFromCookie();
        expect(cookie).toBe("es");
      });

      it("should save locale with custom expiry days", () => {
        saveLocaleToCookie("fr", 30);
        const cookie = loadLocaleFromCookie();
        expect(cookie).toBe("fr");
      });

      it("should overwrite existing cookie", () => {
        saveLocaleToCookie("en");
        expect(loadLocaleFromCookie()).toBe("en");

        saveLocaleToCookie("de");
        expect(loadLocaleFromCookie()).toBe("de");
      });

      it("should handle different locales", () => {
        const locales = ["en", "es", "ar", "fr", "de", "zh"];
        locales.forEach((locale) => {
          saveLocaleToCookie(locale);
          expect(loadLocaleFromCookie()).toBe(locale);
        });
      });
    });

    describe("loadLocaleFromCookie", () => {
      it("should load saved locale from cookie", () => {
        saveLocaleToCookie("es");
        expect(loadLocaleFromCookie()).toBe("es");
      });

      it("should return null if no cookie exists", () => {
        expect(loadLocaleFromCookie()).toBeNull();
      });

      it("should return the correct locale after saving", () => {
        saveLocaleToCookie("zh");
        expect(loadLocaleFromCookie()).toBe("zh");
      });

      it("should handle cookie with spaces", () => {
        // Manually set cookie with spaces
        document.cookie = `${LOCALE_COOKIE_KEY}=ar; path=/`;
        expect(loadLocaleFromCookie()).toBe("ar");
      });
    });
  });

  describe("Integration", () => {
    it("should work independently for localStorage and cookies", () => {
      saveLocale("en");
      saveLocaleToCookie("es");

      expect(loadLocale()).toBe("en");
      expect(loadLocaleFromCookie()).toBe("es");
    });

    it("should clear localStorage without affecting cookies", () => {
      saveLocale("fr");
      saveLocaleToCookie("de");

      clearLocale();

      expect(loadLocale()).toBeNull();
      expect(loadLocaleFromCookie()).toBe("de");
    });

    it("should handle switching between storage methods", () => {
      // Save to localStorage
      saveLocale("en");
      expect(loadLocale()).toBe("en");

      // Save to cookie
      saveLocaleToCookie("es");
      expect(loadLocaleFromCookie()).toBe("es");

      // localStorage should still have original value
      expect(loadLocale()).toBe("en");
    });
  });
});
