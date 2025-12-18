# E2E Test Structure - Organization Guide

## Organized Structure

The structure follows industry best practices for scalable E2E tests.

## Complete Structure

```
tests/e2e/
├── apps/                                    # Tests organized by application
│   ├── student-teacher/                    # Student-Teacher app
│   │   ├── auth/                           # Feature: Authentication
│   │   │   ├── login.spec.ts              # Login tests
│   │   │   └── register.spec.ts           # Register tests
│   │   ├── dashboard/                      # Feature: Dashboard
│   │   │   └── dashboard.spec.ts
│   │   ├── navigation/                     # Feature: Navigation
│   │   │   └── navigation.spec.ts
│   │   └── pages/                          # Page Objects for this app
│   │       ├── LoginPage.ts
│   │       ├── RegisterPage.ts
│   │       ├── DashboardPage.ts
│   │       └── index.ts                    # Exports
│   │
│   └── institutional/                      # Institutional app
│       ├── auth/                           # Feature: Authentication
│       │   └── login.spec.ts
│       ├── navigation/                      # Feature: Navigation
│       │   └── navigation.spec.ts
│       └── pages/                           # Page Objects for this app
│           ├── LoginPage.ts
│           └── index.ts
│
├── shared/                                  # Shared resources
│   ├── fixtures.ts                         # Test data and fixtures
│   └── utils.ts                            # Test utilities
│
└── config/                                  # Global configuration
    ├── global-setup.ts                     # Setup before all tests
    └── global-teardown.ts                  # Teardown after all tests
```

## Advantages

### 1. Scalability

- Easy to add new apps: create `apps/{new-app}/`
- Easy to add new features: create a new folder
- No growth limit

### 2. Maintainability

- Tests organized by functionality
- Easy to find specific tests
- Page Objects separated by app

### 3. Clarity

- Clear separation between apps
- Clear separation between features
- Shared resources in one place

### 4. Reusability

- Page Objects per app (can differ)
- Shared data and utilities
- No unnecessary duplication

### 5. Professional

- Follows Playwright best practices
- Industry standard structure
- Easy for new developers to understand

## Organization Rules

### Tests (`.spec.ts`)

- One file per feature/functionality
- Grouped in feature folders
- Descriptive names: `login.spec.ts`, `dashboard.spec.ts`

### Page Objects

- One file per page
- Separated by application (each app can have differences)
- Located in `apps/{app}/pages/`

### Shared Resources

- Test data in `shared/fixtures.ts`
- Utilities in `shared/utils.ts`
- Only what is actually shared

### Configuration

- Global setup/teardown in `config/`
- Playwright configuration in project root

## How to Use This Structure

### Add a New Test

1. **Identify app and feature:**
   - Is it for `student-teacher` or `institutional`?
   - Is it `auth`, `dashboard`, `navigation`, or another feature?

2. **Locate or create file:**
   - If feature exists: add test to existing `.spec.ts`
   - If not: create `apps/{app}/{feature}/{feature}.spec.ts`

3. **Use Page Objects:**

   ```typescript
   import { LoginPage } from "../pages";
   ```

4. **Use shared data:**
   ```typescript
   import { testUsers } from "../../../shared/fixtures";
   ```

### Add a New Page Object

1. **Create file in correct app:**
   - `apps/{app}/pages/{PageName}Page.ts`

2. **Export in index:**
   - Add to `apps/{app}/pages/index.ts`

3. **Use in tests:**
   ```typescript
   import { NewPage } from "../pages";
   ```

## Statistics

- **Organized tests**: 14+ tests in small focused files
- **Page Objects**: Separated by application
- **Features**: 3 main features (auth, dashboard, navigation)
- **Apps**: 2 applications (student-teacher, institutional)
