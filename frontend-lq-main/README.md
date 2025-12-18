# LingoQuesto Frontend Monorepo

Professional monorepo for LingoQuesto's frontend applications, built with modern tooling and best practices.

## Overview

This monorepo contains:

- **Apps**:
  - `student-teacher`: Nuxt 4 app for students and teachers
  - `institutional`: Vue 3 + Vite app for institutional administration

- **Packages**:
  - `@lq/ui`: Shared UI components (Atomic Design)
  - `@lq/graphql`: GraphQL client with Apollo
  - `@lq/stores`: Pinia stores
  - `@lq/utils`: Utility functions & role-based routing
  - `@lq/types`: TypeScript types & enums
  - `@lq/composables`: Shared composables
  - `@lq/i18n`: Internationalization utilities

## Tech Stack

- **Monorepo**: pnpm workspaces
- **Framework**: Nuxt 4, Vue 3 + Vite
- **Language**: TypeScript
- **State**: Pinia
- **API**: Apollo Client + GraphQL
- **UI**: PrimeVue + TailwindCSS
- **i18n**: Vue I18n / Nuxt I18n
- **Testing**: Vitest, Playwright
- **Linting**: ESLint + Prettier
- **Git Hooks**: Husky
- **CI/CD**: GitHub Actions

## Prerequisites

- Node.js >= 20.0.0
- pnpm >= 9.0.0

## Quick Start

```bash
corepack enable pnpm

# Install dependencies
pnpm install

# Run student-teacher app
pnpm dev:student-teacher

# Run institutional app
pnpm dev:institutional

# Run both apps
pnpm dev
```

## Project Structure

```
frontend-lq/
├── apps/
│   ├── student-teacher/          # Nuxt 4 app
│   │   ├── pages/                # Pages & routes
│   │   ├── components/           # App-specific components
│   │   ├── composables/          # Composables
│   │   ├── middleware/           # Route middleware
│   │   ├── plugins/              # Nuxt plugins
│   │   ├── layouts/              # Layouts
│   │   ├── locales/              # i18n translations
│   │   └── nuxt.config.ts        # Nuxt configuration
│   │
│   └── institutional/            # Vue 3 + Vite app
│       ├── src/
│       │   ├── views/            # Pages
│       │   ├── components/       # Components
│       │   ├── router/           # Vue Router
│       │   ├── plugins/          # Plugins
│       │   ├── locales/          # i18n translations
│       │   └── main.ts           # Entry point
│       └── vite.config.ts        # Vite configuration
│
├── packages/
│   ├── ui/                       # UI component library
│   │   └── src/
│   │       ├── atoms/            # Atomic components
│   │       ├── molecules/        # Molecule components
│   │       ├── organisms/        # Organism components
│   │       └── types/            # TypeScript types
│   │
│   ├── graphql/                  # GraphQL client
│   │   └── src/
│   │       ├── apollo-client.ts  # Apollo setup
│   │       ├── cache-policies.ts # Cache configuration
│   │       ├── queries/          # GraphQL queries
│   │       ├── mutations/        # GraphQL mutations
│   │       └── subscriptions/    # GraphQL subscriptions
│   │
│   ├── stores/                   # Pinia stores
│   │   └── src/
│   │       ├── auth.ts           # Auth store
│   │       ├── user.ts           # User store
│   │       └── notification.ts   # Notification store
│   │
│   ├── utils/                    # Utility functions
│   │   └── src/
│   │       ├── role-routes.ts    # Role-based routing utilities
│   │       ├── validators.ts     # Validation functions
│   │       ├── formatters.ts     # Formatting functions
│   │       └── date.ts           # Date utilities
│   │
│   ├── types/                    # TypeScript types
│   │   └── src/
│   │       ├── enums.ts          # AccountType & other enums
│   │       ├── auth.ts           # Auth types
│   │       └── roles.ts          # Role permissions
│   │
│   ├── composables/              # Shared composables
│   │   └── src/
│   │       └── useRoleNavigation.ts  # Role navigation
│   │
│   └── i18n/                     # i18n utilities
│       └── src/
│           └── index.ts          # i18n helpers
│
├── tests/
│   ├── unit/                     # Unit tests
│   └── e2e/                      # E2E tests
│
├── scripts/                      # Build & utility scripts
│   ├── validate-i18n.mjs         # i18n validation
│   └── extract-i18n-keys.mjs     # i18n key extraction
│
└── .github/
    └── workflows/                # CI/CD workflows
```

## Available Scripts

### Development

```bash
pnpm dev                          # Run all apps
pnpm dev:student-teacher          # Run student-teacher app
pnpm dev:institutional            # Run institutional app
```

### Build

```bash
pnpm build                        # Build all apps
pnpm build:student-teacher        # Build student-teacher app
pnpm build:institutional          # Build institutional app
```

### Testing

```bash
pnpm test                         # Run all tests
pnpm test:unit                    # Run unit tests
pnpm test:e2e                     # Run E2E tests
```

### Code Quality

```bash
pnpm lint                         # Run ESLint
pnpm lint:fix                     # Fix ESLint issues
pnpm format                       # Format with Prettier
pnpm format:check                 # Check formatting
pnpm typecheck                    # Run TypeScript checks
```

### GraphQL

```bash
pnpm graphql:codegen              # Generate TypeScript types
pnpm graphql:watch                # Watch and generate types
```

### i18n

```bash
pnpm i18n:validate                # Validate translations
pnpm i18n:extract                 # Extract i18n keys
```

### Utilities

```bash
pnpm clean                        # Clean all dependencies
pnpm clean:install                # Clean and reinstall
```

## Documentation

- [Installation Guide](./docs/INSTALLATION.md)
- [Development Guide](./docs/DEVELOPMENT.md)
- [Contributing Guide](./docs/CONTRIBUTING.md)
- [Testing Guide](./docs/TESTING.md)
- [Deployment Guide](./docs/DEPLOYMENT.md)
- [Architecture](./docs/ARCHITECTURE.md)

## Key Features

### GraphQL Integration

- Apollo Client with HTTP and WebSocket support
- Automatic reconnection with exponential backoff
- Advanced caching with type policies
- Auto-generated TypeScript types
- Centralized error handling

### i18n System

- Automated key extraction
- Translation validation
- Duplicate key detection
- Orphaned key detection
- Support for nested messages

### Security

- Route guards and middleware
- Role-based access control
- Secure token management
- CSP headers
- XSS protection

### Testing

- Unit tests with Vitest
- Component tests with Vue Testing Library
- E2E tests with Playwright
- Code coverage reporting

### Code Quality

- ESLint configuration
- Prettier formatting
- Husky git hooks
- Commitlint for conventional commits
- Pre-commit linting

### CI/CD

- Automated testing
- Type checking
- Build validation
- i18n validation
- Deployment automation

## Environment Variables

### Student-Teacher App

```env
NUXT_PUBLIC_GRAPHQL_ENDPOINT=http://localhost:4000/graphql
NUXT_PUBLIC_GRAPHQL_WS_ENDPOINT=ws://localhost:4000/graphql
NUXT_PUBLIC_SENTRY_DSN=your-sentry-dsn
NUXT_PUBLIC_SENTRY_ENVIRONMENT=development
```

### Institutional App

```env
VITE_GRAPHQL_ENDPOINT=http://localhost:4000/graphql
VITE_GRAPHQL_WS_ENDPOINT=ws://localhost:4000/graphql
VITE_SENTRY_DSN=your-sentry-dsn
VITE_ENVIRONMENT=development
```

## Contributing

Please read [CONTRIBUTING.md](./docs/CONTRIBUTING.md) for details on our code of conduct and the process for submitting
pull requests.

## License

This project is proprietary and confidential.

## Support

For support, please contact the development team or create an issue in the repository.
