import { expect, type Page, type Locator } from "@playwright/test";

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly loginButton: Locator;
  readonly registerLink: Locator;
  readonly forgotPasswordLink: Locator;
  readonly errorMessage: Locator;
  readonly successMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.locator('input[type="email"]');
    this.passwordInput = page.locator('input[type="password"]');
    this.loginButton = page.locator('button[type="submit"]');
    this.registerLink = page.getByRole("link", { name: /registr|sign up/i });
    this.forgotPasswordLink = page.getByRole("link", { name: /forgot|olvid/i });
    this.errorMessage = page.locator('[role="alert"], .p-toast-message-error, .error-message');
    this.successMessage = page.locator(
      '[role="alert"]:has-text("success|éxito"), .p-toast-message-success, .success-message',
    );
  }

  async goto() {
    await this.page.goto("/login");
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }

  async expectLoginFormVisible() {
    await this.emailInput.waitFor({ state: "visible" });
    await this.passwordInput.waitFor({ state: "visible" });
    await this.loginButton.waitFor({ state: "visible" });
  }

  async expectErrorMessage(message?: string) {
    if (message) {
      await expect(this.errorMessage).toContainText(message, { timeout: 5000 });
    } else {
      await expect(this.errorMessage.first()).toBeVisible({ timeout: 5000 });
    }
  }

  async expectSuccessMessage(message?: string) {
    if (message) {
      await expect(this.successMessage).toContainText(message, { timeout: 5000 });
    } else {
      await expect(this.successMessage.first()).toBeVisible({ timeout: 5000 });
    }
  }

  async loginAndWaitForDashboard(email: string, password: string) {
    await this.login(email, password);
    await this.page.waitForURL(/\/dashboard/, { timeout: 10000 });
  }

  async expectFormValidation() {
    await this.loginButton.click();
    const emailRequired = await this.emailInput.getAttribute("required");
    expect(emailRequired).toBeTruthy();
  }
}
