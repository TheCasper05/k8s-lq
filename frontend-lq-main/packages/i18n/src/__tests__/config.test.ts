import { describe, it, expect } from "vitest";
import {
  SUPPORTED_LOCALES,
  DEFAULT_LOCALE,
  FALLBACK_LOCALE,
  LOCALE_COOKIE_KEY,
  LOCALE_STORAGE_KEY,
  type LocaleConfig,
  type SupportedLocale,
} from "../config";

describe("i18n Configuration", () => {
  describe("SUPPORTED_LOCALES", () => {
    it("should contain 6 locales", () => {
      expect(SUPPORTED_LOCALES).toHaveLength(6);
    });

    it("should include English", () => {
      const en = SUPPORTED_LOCALES.find((l) => l.code === "en");
      expect(en).toBeDefined();
      expect(en?.name).toBe("English");
      expect(en?.dir).toBe("ltr");
      expect(en?.flag).toBe("🇺🇸");
      expect(en?.language).toBe("en-US");
    });

    it("should include Spanish", () => {
      const es = SUPPORTED_LOCALES.find((l) => l.code === "es");
      expect(es).toBeDefined();
      expect(es?.name).toBe("Español");
      expect(es?.dir).toBe("ltr");
      expect(es?.flag).toBe("🇪🇸");
      expect(es?.language).toBe("es-ES");
    });

    it("should include Arabic with RTL", () => {
      const ar = SUPPORTED_LOCALES.find((l) => l.code === "ar");
      expect(ar).toBeDefined();
      expect(ar?.name).toBe("العربية");
      expect(ar?.dir).toBe("rtl");
      expect(ar?.flag).toBe("🇸🇦");
      expect(ar?.language).toBe("ar-SA");
    });

    it("should include French", () => {
      const fr = SUPPORTED_LOCALES.find((l) => l.code === "fr");
      expect(fr).toBeDefined();
      expect(fr?.name).toBe("Français");
      expect(fr?.dir).toBe("ltr");
      expect(fr?.flag).toBe("🇫🇷");
      expect(fr?.language).toBe("fr-FR");
    });

    it("should include German", () => {
      const de = SUPPORTED_LOCALES.find((l) => l.code === "de");
      expect(de).toBeDefined();
      expect(de?.name).toBe("Deutsch");
      expect(de?.dir).toBe("ltr");
      expect(de?.flag).toBe("🇩🇪");
      expect(de?.language).toBe("de-DE");
    });

    it("should include Chinese", () => {
      const zh = SUPPORTED_LOCALES.find((l) => l.code === "zh");
      expect(zh).toBeDefined();
      expect(zh?.name).toBe("中文");
      expect(zh?.dir).toBe("ltr");
      expect(zh?.flag).toBe("🇨🇳");
      expect(zh?.language).toBe("zh-CN");
    });

    it("should have only one RTL locale (Arabic)", () => {
      const rtlLocales = SUPPORTED_LOCALES.filter((l) => l.dir === "rtl");
      expect(rtlLocales).toHaveLength(1);
      expect(rtlLocales[0].code).toBe("ar");
    });

    it("should have unique locale codes", () => {
      const codes = SUPPORTED_LOCALES.map((l) => l.code);
      const uniqueCodes = new Set(codes);
      expect(uniqueCodes.size).toBe(codes.length);
    });

    it("should have all required properties for each locale", () => {
      SUPPORTED_LOCALES.forEach((locale) => {
        expect(locale).toHaveProperty("code");
        expect(locale).toHaveProperty("name");
        expect(locale).toHaveProperty("dir");
        expect(locale).toHaveProperty("flag");
        expect(locale).toHaveProperty("language");

        expect(typeof locale.code).toBe("string");
        expect(typeof locale.name).toBe("string");
        expect(["ltr", "rtl"]).toContain(locale.dir);
        expect(typeof locale.flag).toBe("string");
        expect(typeof locale.language).toBe("string");
      });
    });
  });

  describe("DEFAULT_LOCALE", () => {
    it("should be English", () => {
      expect(DEFAULT_LOCALE).toBe("en");
    });

    it("should exist in SUPPORTED_LOCALES", () => {
      const exists = SUPPORTED_LOCALES.some((l) => l.code === DEFAULT_LOCALE);
      expect(exists).toBe(true);
    });
  });

  describe("FALLBACK_LOCALE", () => {
    it("should be English", () => {
      expect(FALLBACK_LOCALE).toBe("en");
    });

    it("should exist in SUPPORTED_LOCALES", () => {
      const exists = SUPPORTED_LOCALES.some((l) => l.code === FALLBACK_LOCALE);
      expect(exists).toBe(true);
    });

    it("should be the same as DEFAULT_LOCALE", () => {
      expect(FALLBACK_LOCALE).toBe(DEFAULT_LOCALE);
    });
  });

  describe("LOCALE_COOKIE_KEY", () => {
    it("should be defined", () => {
      expect(LOCALE_COOKIE_KEY).toBeDefined();
      expect(typeof LOCALE_COOKIE_KEY).toBe("string");
    });

    it("should have a meaningful name", () => {
      expect(LOCALE_COOKIE_KEY).toBe("lq_locale");
    });
  });

  describe("LOCALE_STORAGE_KEY", () => {
    it("should be defined", () => {
      expect(LOCALE_STORAGE_KEY).toBeDefined();
      expect(typeof LOCALE_STORAGE_KEY).toBe("string");
    });

    it("should have a meaningful name", () => {
      expect(LOCALE_STORAGE_KEY).toBe("lq_locale");
    });
  });

  describe("TypeScript Types", () => {
    it("should correctly type LocaleConfig", () => {
      const locale: LocaleConfig = {
        code: "en",
        name: "English",
        dir: "ltr",
        flag: "🇺🇸",
        language: "en-US",
      };

      expect(locale.code).toBe("en");
      expect(locale.dir).toBe("ltr");
    });

    it("should correctly type SupportedLocale", () => {
      const locales: SupportedLocale[] = ["en", "es", "ar", "fr", "de", "zh"];
      expect(locales).toHaveLength(6);
    });

    it("should enforce valid locale codes", () => {
      // This test verifies TypeScript compilation
      const validLocale: SupportedLocale = "en";
      expect(validLocale).toBe("en");

      // The following would cause TypeScript error:
      // const invalidLocale: SupportedLocale = "invalid";
    });
  });
});
