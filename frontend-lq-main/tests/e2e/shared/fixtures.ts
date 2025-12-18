import { test as base, expect, type Page } from "@playwright/test";
import { ENV } from "./env";

export const testUsers = {
  student: {
    email: ENV.TEST_STUDENT_EMAIL,
    password: ENV.TEST_STUDENT_PASSWORD,
    firstName: "Student",
    lastName: "Test",
  },
  teacher: {
    email: ENV.TEST_TEACHER_EMAIL,
    password: ENV.TEST_TEACHER_PASSWORD,
    firstName: "Teacher",
    lastName: "Test",
  },
  admin: {
    email: ENV.TEST_ADMIN_EMAIL,
    password: ENV.TEST_ADMIN_PASSWORD,
    firstName: "Admin",
    lastName: "Test",
  },
  invalid: {
    email: "invalid@test.com",
    password: "WrongPassword123!",
  },
};

export const test = base.extend<{
  authenticatedPage: Page;
  studentPage: Page;
  teacherPage: Page;
}>({
  authenticatedPage: async ({ page }, use) => {
    await use(page);
  },

  studentPage: async ({ page, baseURL: _baseURL }, use) => {
    if (_baseURL) {
      await page.goto(`${_baseURL}/login`);
    }
    await use(page);
  },

  teacherPage: async ({ page, baseURL: _baseURL }, use) => {
    if (_baseURL) {
      await page.goto(`${_baseURL}/login`);
    }
    await use(page);
  },
});

export { expect };
