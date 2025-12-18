import { expect, type Page, type Locator } from "@playwright/test";

export class RegisterPage {
  readonly page: Page;
  readonly firstNameInput: Locator;
  readonly lastNameInput: Locator;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly confirmPasswordInput: Locator;
  readonly registerButton: Locator;
  readonly loginLink: Locator;
  readonly errorMessage: Locator;
  readonly successMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.firstNameInput = page.locator('input[id="firstName"]');
    this.lastNameInput = page.locator('input[id="lastName"]');
    this.emailInput = page.locator('input[type="email"]');
    this.passwordInput = page.locator('input[id="password"]').first();
    this.confirmPasswordInput = page.locator('input[id="confirmPassword"]');
    this.registerButton = page.locator('button[type="submit"]');
    this.loginLink = page.getByRole("link", { name: /login|iniciar/i });
    this.errorMessage = page.locator('[role="alert"], .p-toast-message-error, .error-message');
    this.successMessage = page.locator(
      '[role="alert"]:has-text("success|éxito"), .p-toast-message-success, .success-message',
    );
  }

  async goto() {
    await this.page.goto("/register");
  }

  async fillForm(data: {
    firstName: string;
    lastName: string;
    email: string;
    password: string;
    confirmPassword: string;
  }) {
    await this.firstNameInput.fill(data.firstName);
    await this.lastNameInput.fill(data.lastName);
    await this.emailInput.fill(data.email);
    await this.passwordInput.fill(data.password);
    await this.confirmPasswordInput.fill(data.confirmPassword);
  }

  async submit() {
    await this.registerButton.click();
  }

  async register(data: {
    firstName: string;
    lastName: string;
    email: string;
    password: string;
    confirmPassword: string;
  }) {
    await this.fillForm(data);
    await this.submit();
  }

  async expectFormVisible() {
    await this.firstNameInput.waitFor({ state: "visible" });
    await this.lastNameInput.waitFor({ state: "visible" });
    await this.emailInput.waitFor({ state: "visible" });
    await this.passwordInput.waitFor({ state: "visible" });
    await this.confirmPasswordInput.waitFor({ state: "visible" });
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
}
