# E2E Tests with Playwright

This directory contains end-to-end (E2E) tests for LingoQuesto applications using Playwright.

## Quick Start

```bash
# Install dependencies
pnpm install
pnpm test:e2e:install

# Run all tests
pnpm test:e2e

# Run tests with UI (recommended)
pnpm test:e2e:ui
```

## Structure

```
tests/e2e/
├── apps/                    # Tests organized by application
│   ├── student-teacher/    # Student-Teacher app tests
│   └── institutional/      # Institutional app tests
├── shared/                  # Shared resources
│   ├── fixtures.ts        # Test data and fixtures
│   ├── env.ts             # Environment variables
│   ├── test-data.ts       # Data factories
│   └── utils.ts           # Utilities
├── config/                 # Global configuration
│   ├── global-setup.ts
│   └── global-teardown.ts
└── docs/                   # Documentation
```

## Current Configuration

- **Environment:** Staging (`https://app-qa.lingoquesto.com`)
- **Browsers:** Chromium, Firefox, WebKit, Mobile
- **Credentials:** Configured in `shared/env.ts`

## Main Commands

```bash
# Run all tests
pnpm test:e2e

# Visual interface (recommended)
pnpm test:e2e:ui

# Headed mode
pnpm test:e2e:headed

# Debug mode
pnpm test:e2e:debug

# View report
pnpm test:e2e:report

# Run specific test
pnpm test:e2e apps/student-teacher/auth/login.spec.ts
```

## Documentation

Detailed documentation is in the [`docs/`](./docs/) folder:

- **[SETUP.md](./docs/SETUP.md)** - Installation and setup guide
- **[STRUCTURE.md](./docs/STRUCTURE.md)** - Project structure explanation

## Page Object Model

Each application has its own Page Objects:

```typescript
import { LoginPage } from "../pages";
import { testUsers } from "../../../shared/fixtures";

test("login test", async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login(testUsers.student.email, testUsers.student.password);
});
```

## Environment Variables

URLs and credentials are configured in `shared/env.ts`. You can override them:

```bash
STUDENT_TEACHER_URL=https://app-qa.lingoquesto.com pnpm test:e2e
```

## Best Practices

1. **Use Page Objects** - Always use Page Objects instead of direct selectors
2. **Centralized data** - Use `testUsers` from `shared/fixtures.ts`
3. **Tests by feature** - Group related tests in feature files
4. **Descriptive names** - Use clear names for tests and selectors

## Help

- See full documentation in [`docs/`](./docs/)
- Run `pnpm test:e2e:ui` for visual interface
- Review `playwright.config.ts` for advanced configuration
