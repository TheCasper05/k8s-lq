import { defineConfig, devices } from "@playwright/test";
import { ENV } from "./tests/e2e/shared/env";

export default defineConfig({
  testDir: "./tests/e2e/apps",
  timeout: ENV.TEST_TIMEOUT,
  expect: {
    timeout: 5000,
  },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI
    ? [
        ["html"],
        ["json", { outputFile: "test-results/results.json" }],
        ["junit", { outputFile: "test-results/junit.xml" }],
      ]
    : [["html"], ["list"], ["json", { outputFile: "test-results/results.json" }]],
  use: {
    baseURL: ENV.STUDENT_TEACHER_URL,
    trace: process.env.CI ? "on-first-retry" : "retain-on-failure",
    screenshot: "only-on-failure",
    video: process.env.CI ? "retain-on-failure" : "off",
    actionTimeout: ENV.ACTION_TIMEOUT,
    navigationTimeout: 60000, // Increased for staging environment
    ...(ENV.SLOW_MO > 0 && { launchOptions: { slowMo: ENV.SLOW_MO } }),
  },
  projects: [
    // Student-Teacher App - Desktop browsers
    {
      name: "student-teacher-chromium",
      use: {
        ...devices["Desktop Chrome"],
        baseURL: ENV.STUDENT_TEACHER_URL,
      },
      testMatch: "**/student-teacher/**/*.spec.ts",
    },
    {
      name: "student-teacher-firefox",
      use: {
        ...devices["Desktop Firefox"],
        baseURL: ENV.STUDENT_TEACHER_URL,
      },
      testMatch: "**/student-teacher/**/*.spec.ts",
    },
    {
      name: "student-teacher-webkit",
      use: {
        ...devices["Desktop Safari"],
        baseURL: ENV.STUDENT_TEACHER_URL,
      },
      testMatch: "**/student-teacher/**/*.spec.ts",
    },
    // Institutional App - Desktop browsers
    {
      name: "institutional-chromium",
      use: {
        ...devices["Desktop Chrome"],
        baseURL: ENV.INSTITUTIONAL_URL,
      },
      testMatch: "**/institutional/**/*.spec.ts",
    },
    {
      name: "institutional-firefox",
      use: {
        ...devices["Desktop Firefox"],
        baseURL: ENV.INSTITUTIONAL_URL,
      },
      testMatch: "**/institutional/**/*.spec.ts",
    },
    // Student-Teacher App - Mobile devices
    {
      name: "student-teacher-mobile-chrome",
      use: {
        ...devices["Pixel 5"],
        baseURL: ENV.STUDENT_TEACHER_URL,
      },
      testMatch: "**/student-teacher/**/*.spec.ts",
    },
    {
      name: "student-teacher-mobile-safari",
      use: {
        ...devices["iPhone 12"],
        baseURL: ENV.STUDENT_TEACHER_URL,
      },
      testMatch: "**/student-teacher/**/*.spec.ts",
    },
  ],
  globalSetup: "./tests/e2e/config/global-setup.ts",
  globalTeardown: "./tests/e2e/config/global-teardown.ts",
});
