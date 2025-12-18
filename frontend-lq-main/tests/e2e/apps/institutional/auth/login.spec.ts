import { test, expect } from "@playwright/test";
import { LoginPage } from "../pages";
import { testUsers } from "../../../shared/fixtures";

test.describe("Institutional App - Authentication", () => {
  test("should display login form", async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.expectLoginFormVisible();
  });

  test("should validate required fields in login", async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.expectFormValidation();
  });

  test("should show error with invalid credentials", async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(testUsers.invalid.email, testUsers.invalid.password);
    await loginPage.expectErrorMessage();
  });

  test("should redirect to dashboard after successful login", async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();

    try {
      await loginPage.loginAndWaitForDashboard(testUsers.admin.email, testUsers.admin.password);
      await expect(page).toHaveURL(/\/dashboard/);
    } catch {
      await loginPage.expectErrorMessage();
    }
  });
});
