import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { isRTL, setDocumentDir, getDirection } from "../utils/rtl";

describe("RTL Utilities", () => {
  // Save original document properties
  let originalDir: string;
  let originalLang: string;

  beforeEach(() => {
    // Save original values
    originalDir = document.documentElement.dir;
    originalLang = document.documentElement.lang;
  });

  afterEach(() => {
    // Restore original values
    document.documentElement.dir = originalDir;
    document.documentElement.lang = originalLang;
  });

  describe("isRTL", () => {
    it("should return true for Arabic locale", () => {
      expect(isRTL("ar")).toBe(true);
    });

    it("should return false for English locale", () => {
      expect(isRTL("en")).toBe(false);
    });

    it("should return false for Spanish locale", () => {
      expect(isRTL("es")).toBe(false);
    });

    it("should return false for French locale", () => {
      expect(isRTL("fr")).toBe(false);
    });

    it("should return false for German locale", () => {
      expect(isRTL("de")).toBe(false);
    });

    it("should return false for Chinese locale", () => {
      expect(isRTL("zh")).toBe(false);
    });

    it("should return false for unknown locale", () => {
      expect(isRTL("unknown")).toBe(false);
    });

    it("should handle empty string", () => {
      expect(isRTL("")).toBe(false);
    });
  });

  describe("getDirection", () => {
    it("should return 'rtl' for Arabic", () => {
      expect(getDirection("ar")).toBe("rtl");
    });

    it("should return 'ltr' for English", () => {
      expect(getDirection("en")).toBe("ltr");
    });

    it("should return 'ltr' for Spanish", () => {
      expect(getDirection("es")).toBe("ltr");
    });

    it("should return 'ltr' for unknown locale", () => {
      expect(getDirection("unknown")).toBe("ltr");
    });
  });

  describe("setDocumentDir", () => {
    it("should set document direction to rtl for Arabic", () => {
      setDocumentDir("ar");
      expect(document.documentElement.dir).toBe("rtl");
      expect(document.documentElement.lang).toBe("ar");
    });

    it("should set document direction to ltr for English", () => {
      setDocumentDir("en");
      expect(document.documentElement.dir).toBe("ltr");
      expect(document.documentElement.lang).toBe("en");
    });

    it("should set document direction to ltr for Spanish", () => {
      setDocumentDir("es");
      expect(document.documentElement.dir).toBe("ltr");
      expect(document.documentElement.lang).toBe("es");
    });

    it("should handle switching from LTR to RTL", () => {
      setDocumentDir("en");
      expect(document.documentElement.dir).toBe("ltr");

      setDocumentDir("ar");
      expect(document.documentElement.dir).toBe("rtl");
    });

    it("should handle switching from RTL to LTR", () => {
      setDocumentDir("ar");
      expect(document.documentElement.dir).toBe("rtl");

      setDocumentDir("es");
      expect(document.documentElement.dir).toBe("ltr");
    });

    it("should set lang attribute correctly", () => {
      setDocumentDir("fr");
      expect(document.documentElement.lang).toBe("fr");

      setDocumentDir("de");
      expect(document.documentElement.lang).toBe("de");
    });
  });
});
