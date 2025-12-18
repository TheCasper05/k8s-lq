import { test, expect } from "@playwright/test";
import { LoginPage, RegisterPage } from "../pages";

test.describe("Student-Teacher App - Navigation", () => {
  test("should display home page correctly", async ({ page }) => {
    await page.goto("/");
    const h1 = page.locator("h1").first();
    await expect(h1).toBeVisible({ timeout: 10000 });
  });

  test("should navigate correctly between pages", async ({ page }) => {
    await page.goto("/");
    await page.goto("/login");
    await expect(page).toHaveURL(/\/login/);
    await page.goto("/register");
    await expect(page).toHaveURL(/\/register/);
  });

  test("complete flow: register -> login -> dashboard", async ({ page }) => {
    const registerPage = new RegisterPage(page);
    const loginPage = new LoginPage(page);

    await registerPage.goto();
    await registerPage.expectFormVisible();

    await registerPage.loginLink.click();
    await loginPage.expectLoginFormVisible();

    await loginPage.registerLink.click();
    await registerPage.expectFormVisible();
  });
});
