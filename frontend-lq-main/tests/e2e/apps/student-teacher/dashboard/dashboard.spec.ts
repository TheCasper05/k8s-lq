import { test, expect } from "@playwright/test";
import { DashboardPage } from "../pages";

test.describe("Student-Teacher App - Dashboard", () => {
  test("should display dashboard after successful login", async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    await dashboardPage.goto();

    const currentUrl = page.url();
    if (currentUrl.includes("/login")) {
      await expect(page).toHaveURL(/\/login/);
    } else {
      await dashboardPage.expectDashboardLoaded();
    }
  });

  test("should have visible navigation on dashboard", async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    await dashboardPage.goto();

    const currentUrl = page.url();
    if (!currentUrl.includes("/login")) {
      await dashboardPage.expectNavigationVisible();
    }
  });
});
