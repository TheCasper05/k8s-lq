import { expect, type Page, type Locator } from "@playwright/test";

export class DashboardPage {
  readonly page: Page;
  readonly title: Locator;
  readonly teacherCard: Locator;
  readonly studentCard: Locator;
  readonly navigation: Locator;

  constructor(page: Page) {
    this.page = page;
    this.title = page.locator("h1");
    this.teacherCard = page.locator("text=/teacher|profesor/i").first();
    this.studentCard = page.locator("text=/student|estudiante/i").first();
    this.navigation = page.locator("nav");
  }

  async goto() {
    await this.page.goto("/dashboard");
  }

  async expectDashboardLoaded() {
    await this.title.waitFor({ state: "visible", timeout: 10000 });
  }

  async goToTeacherPortal() {
    await this.teacherCard.click();
    await this.page.waitForURL(/\/teacher/, { timeout: 10000 });
  }

  async goToStudentPortal() {
    await this.studentCard.click();
    await this.page.waitForURL(/\/student/, { timeout: 10000 });
  }

  async expectNavigationVisible() {
    await expect(this.navigation).toBeVisible();
  }
}
