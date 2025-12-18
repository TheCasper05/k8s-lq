import { describe, it, expect } from "vitest";
import { isValidEmail, isStrongPassword, isRequired, minLength, maxLength } from "@lq/utils";

describe("Validators", () => {
  describe("isValidEmail", () => {
    it("should validate email addresses", () => {
      expect(isValidEmail("test@example.com")).toBe(true);
      expect(isValidEmail("user.name+tag@example.co.uk")).toBe(true);
      expect(isValidEmail("invalid")).toBe(false);
      expect(isValidEmail("missing@domain")).toBe(false);
      expect(isValidEmail("@example.com")).toBe(false);
    });
  });

  describe("isStrongPassword", () => {
    it("should validate password strength", () => {
      expect(isStrongPassword("Password1")).toBe(true);
      expect(isStrongPassword("MyP@ssw0rd")).toBe(true);
      expect(isStrongPassword("weak")).toBe(false);
      expect(isStrongPassword("noupppercase1")).toBe(false);
      expect(isStrongPassword("NOLOWERCASE1")).toBe(false);
      expect(isStrongPassword("NoNumbers")).toBe(false);
    });
  });

  describe("isRequired", () => {
    it("should validate required fields", () => {
      expect(isRequired("text")).toBe(true);
      expect(isRequired("")).toBe(false);
      expect(isRequired("   ")).toBe(false);
      expect(isRequired(null)).toBe(false);
      expect(isRequired(undefined)).toBe(false);
      expect(isRequired([])).toBe(false);
      expect(isRequired(["item"])).toBe(true);
    });
  });

  describe("minLength", () => {
    it("should validate minimum length", () => {
      expect(minLength("hello", 3)).toBe(true);
      expect(minLength("hi", 3)).toBe(false);
    });
  });

  describe("maxLength", () => {
    it("should validate maximum length", () => {
      expect(maxLength("hello", 10)).toBe(true);
      expect(maxLength("this is too long", 5)).toBe(false);
    });
  });
});
