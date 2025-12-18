# Installation Guide

## Prerequisites

1. **Node.js**: Install Node.js 20.x or higher

   ```bash
   # Check version
   node --version  # Should be >= 20.0.0
   ```

2. **pnpm**: Install pnpm 9.x or higher

   ```bash
   # Install pnpm globally
   npm install -g pnpm

   # Check version
   pnpm --version  # Should be >= 9.0.0
   ```

3. **Git**: Make sure Git is installed
   ```bash
   git --version
   ```

## Setup Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd frontend-lq
```

### 2. Install Dependencies

```bash
pnpm install
```

This will install all dependencies for all apps and packages in the monorepo.

### 3. Set Up Environment Variables

Copy the example environment files and configure them:

```bash
# Student-Teacher app
cp apps/student-teacher/.env.example apps/student-teacher/.env

# Institutional app
cp apps/institutional/.env.example apps/institutional/.env
```

Edit the `.env` files with your configuration:

```env
# GraphQL endpoint (your backend)
NUXT_PUBLIC_GRAPHQL_ENDPOINT=http://localhost:4000/graphql
NUXT_PUBLIC_GRAPHQL_WS_ENDPOINT=ws://localhost:4000/graphql

# Sentry (optional)
NUXT_PUBLIC_SENTRY_DSN=
NUXT_PUBLIC_SENTRY_ENVIRONMENT=development
```

### 4. Set Up Git Hooks

```bash
pnpm prepare
```

This will set up Husky git hooks for pre-commit linting and commit message validation.

### 5. Generate GraphQL Types (Optional)

If you have a running GraphQL server:

```bash
pnpm graphql:codegen
```

### 6. Run Development Servers

```bash
# Run student-teacher app (port 3000)
pnpm dev:student-teacher

# Run institutional app (port 3001)
pnpm dev:institutional

# Or run both
pnpm dev
```

## Troubleshooting

### Port Already in Use

If ports 3000 or 3001 are already in use:

```bash
# Find process using the port
lsof -i :3000

# Kill the process
kill -9 <PID>
```

### Dependencies Installation Issues

Clear pnpm cache and reinstall:

```bash
pnpm clean:install
```

### TypeScript Errors

Run type checking to see detailed errors:

```bash
pnpm typecheck
```

### Build Errors

Try rebuilding:

```bash
pnpm clean
pnpm install
pnpm build
```

## Next Steps

- Read the [Development Guide](./DEVELOPMENT.md)
- Understand the [Architecture](./ARCHITECTURE.md)
- Set up your IDE (see [IDE Setup](./IDE_SETUP.md))
