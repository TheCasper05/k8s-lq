# E2E Test Setup Guide

## Initial Installation

### 1. Install project dependencies

```bash
pnpm install
```

### 2. Install Playwright browsers

```bash
pnpm test:e2e:install
```

This command downloads the necessary browsers (Chromium, Firefox, WebKit) that Playwright needs to run tests.

### 3. (Optional) Install system dependencies

If you have issues with system dependencies (especially on Linux), run:

```bash
pnpm test:e2e:install-deps
```

## Verify Installation

To verify everything is correctly installed:

```bash
pnpm test:e2e --list
```

This will show all available tests without running them.

## First Test

Run a simple test to verify everything works:

```bash
pnpm test:e2e apps/institutional/auth/login.spec.ts --project=chromium
```

## Troubleshooting

### Error: "Executable doesn't exist"

Run `pnpm test:e2e:install` to install browsers.

### Error: "Port already in use"

Make sure ports 3000 and 3001 are not in use, or stop any development servers that might be running.

### Error: "Cannot find module '@playwright/test'"

Run `pnpm install` to install all dependencies.

### Tests are very slow

- Verify that development servers are responding quickly
- Reduce the number of workers in `playwright.config.ts`
- Use `--project=chromium` to run only in one browser

## Next Steps

1. Review `tests/e2e/README.md` for complete documentation
2. Run `pnpm test:e2e:ui` for the interactive interface
3. Add more tests as needed
