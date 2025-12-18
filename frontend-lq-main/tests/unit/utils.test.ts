import { describe, it, expect } from "vitest";
import { formatCurrency, formatNumber, slugify, truncate } from "@lq/utils";

describe("Formatters", () => {
  describe("formatCurrency", () => {
    it("should format currency correctly", () => {
      expect(formatCurrency(1234.56)).toBe("$1,234.56");
      expect(formatCurrency(1234.56, "EUR", "de-DE")).toBe("1.234,56 €");
    });
  });

  describe("formatNumber", () => {
    it("should format numbers with thousands separator", () => {
      expect(formatNumber(1234567)).toBe("1,234,567");
    });
  });

  describe("slugify", () => {
    it("should convert text to slug", () => {
      expect(slugify("Hello World")).toBe("hello-world");
      expect(slugify("This is a Test!")).toBe("this-is-a-test");
      expect(slugify("  Multiple   Spaces  ")).toBe("multiple-spaces");
    });
  });

  describe("truncate", () => {
    it("should truncate long text", () => {
      expect(truncate("This is a long text", 10)).toBe("This is...");
      expect(truncate("Short", 10)).toBe("Short");
    });
  });
});
