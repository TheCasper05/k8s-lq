import { test, expect } from "@playwright/test";
import { LoginPage } from "../pages";
import { testUsers } from "../../../shared/fixtures";

test.describe("Student-Teacher App - Login", () => {
  test("should display login form correctly", async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.expectLoginFormVisible();
  });

  test("should validate required fields in login form", async ({ page }) => {
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

  test("should allow navigation to register page from login", async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.registerLink.click();
    await expect(page).toHaveURL(/\/register/);
  });

  test("should allow navigation to forgot password", async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();

    if (await loginPage.forgotPasswordLink.isVisible()) {
      await loginPage.forgotPasswordLink.click();
      await expect(page).toHaveURL(/\/forgot-password/);
    }
  });
});
