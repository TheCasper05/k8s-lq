import type { Page } from "@playwright/test";

export async function waitForPageLoad(page: Page) {
  await page.waitForLoadState("networkidle");
  await page.waitForLoadState("domcontentloaded");
}

export async function takeScreenshot(page: Page, name: string) {
  await page.screenshot({ path: `test-results/screenshots/${name}-${Date.now()}.png`, fullPage: true });
}

export async function waitForElementToDisappear(page: Page, selector: string, timeout = 5000) {
  await page.waitForSelector(selector, { state: "hidden", timeout });
}

export function checkConsoleErrors(page: Page): string[] {
  const errors: string[] = [];

  page.on("console", (msg) => {
    if (msg.type() === "error") {
      errors.push(msg.text());
    }
  });

  return errors;
}

export async function clearStorage(page: Page) {
  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
  });
}

export async function waitForToast(page: Page, timeout = 5000) {
  const toast = page.locator('[role="alert"], .p-toast-message, .toast');
  await toast.first().waitFor({ state: "visible", timeout });
  await toast.first().waitFor({ state: "hidden", timeout: timeout * 2 });
}
