import { test, expect } from "@playwright/test";

test.describe("Institutional App - Navigation", () => {
  test("should display home page correctly", async ({ page }) => {
    await page.goto("/");
    const h1 = page.locator("h1").first();
    await expect(h1).toBeVisible({ timeout: 10000 });
  });

  test("should show navigation on home page", async ({ page }) => {
    await page.goto("/");
    const nav = page.locator("nav");
    await expect(nav).toBeVisible({ timeout: 10000 });
  });

  test("should navigate correctly between pages", async ({ page }) => {
    await page.goto("/");
    await page.goto("/login");
    await expect(page).toHaveURL(/\/login/);
    await page.goto("/");
    await expect(page).toHaveURL(/\//);
  });

  test("should handle not found routes", async ({ page }) => {
    await page.goto("/ruta-inexistente-12345");

    const currentUrl = page.url();
    const pageContent = await page.textContent("body");

    expect(
      currentUrl.includes("404") ||
        currentUrl.includes("not-found") ||
        currentUrl === "http://localhost:3001/" ||
        pageContent?.toLowerCase().includes("not found"),
    ).toBeTruthy();
  });

  test("should work on mobile devices", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto("/");

    const body = page.locator("body");
    await expect(body).toBeVisible();

    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const viewportWidth = page.viewportSize()?.width || 375;
    expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 20);
  });
});
