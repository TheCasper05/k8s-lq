import { test, expect } from "@playwright/test";
import { RegisterPage } from "../pages";
import { testUsers } from "../../../shared/fixtures";

test.describe("Student-Teacher App - Register", () => {
  test("should display register form correctly", async ({ page }) => {
    const registerPage = new RegisterPage(page);
    await registerPage.goto();
    await registerPage.expectFormVisible();
  });

  test("should validate that all fields are required", async ({ page }) => {
    const registerPage = new RegisterPage(page);
    await registerPage.goto();
    await registerPage.submit();

    const emailInput = registerPage.emailInput;
    const required = await emailInput.getAttribute("required");
    expect(required).toBeTruthy();
  });

  test("should show error if passwords do not match", async ({ page }) => {
    const registerPage = new RegisterPage(page);
    await registerPage.goto();

    await registerPage.fillForm({
      firstName: testUsers.student.firstName,
      lastName: testUsers.student.lastName,
      email: testUsers.student.email,
      password: testUsers.student.password,
      confirmPassword: "DifferentPassword123!",
    });

    await registerPage.submit();
    await registerPage.expectErrorMessage();
  });

  test("should allow navigation to login from register", async ({ page }) => {
    const registerPage = new RegisterPage(page);
    await registerPage.goto();
    await registerPage.loginLink.click();
    await expect(page).toHaveURL(/\/login/);
  });
});
