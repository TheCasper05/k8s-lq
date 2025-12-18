# Quick Start Guide

Get up and running with LingoQuesto Frontend in 5 minutes.

## Prerequisites

- Node.js 20+
- pnpm 9+

## Installation

```bash
# 1. Install pnpm (if not installed)
npm install -g pnpm

# 2. Clone repository
git clone <repository-url>
cd frontend-lq

# 3. Install dependencies
pnpm install

# 4. Set up environment variables
cp apps/student-teacher/.env.example apps/student-teacher/.env
cp apps/institutional/.env.example apps/institutional/.env

# 5. Set up git hooks
pnpm prepare
```

## Run Apps

```bash
# Run student-teacher app (http://localhost:3000)
pnpm dev:student-teacher

# Run institutional app (http://localhost:3001)
pnpm dev:institutional

# Or run both
pnpm dev
```

## Project Structure

```
apps/
├── student-teacher/    # Nuxt 4 app for students/teachers
└── institutional/      # Vue 3 app for admin

packages/
├── ui/                 # Shared UI components
├── graphql/            # GraphQL client
├── stores/             # Pinia stores
└── utils/              # Utility functions
```

## Common Commands

```bash
# Development
pnpm dev                    # Run all apps
pnpm dev:student-teacher    # Run student-teacher app
pnpm dev:institutional      # Run institutional app

# Testing
pnpm test                   # Run all tests
pnpm test:unit              # Run unit tests
pnpm test:e2e               # Run E2E tests

# Building
pnpm build                  # Build all apps

# Code Quality
pnpm lint                   # Run linter
pnpm format                 # Format code
pnpm typecheck              # Check types
```

## Making Your First Change

### 1. Create a Component

```vue
<!-- packages/ui/src/atoms/MyButton.vue -->
<template>
  <button class="my-button">
    <slot />
  </button>
</template>

<script setup lang="ts">
  // Component logic here
</script>

<style scoped>
  .my-button {
    /* Styles here */
  }
</style>
```

### 2. Export Component

```typescript
// packages/ui/src/index.ts
export { default as MyButton } from "./atoms/MyButton.vue";
```

### 3. Use in App

```vue
<!-- apps/student-teacher/pages/index.vue -->
<template>
  <MyButton>Click me</MyButton>
</template>

<script setup lang="ts">
  import { MyButton } from "@lq/ui";
</script>
```

## Adding a GraphQL Query

### 1. Create Query

```typescript
// packages/graphql/src/queries/courses.ts
import { gql } from "@apollo/client/core";

export const GET_COURSES = gql`
  query GetCourses {
    courses {
      id
      title
      description
    }
  }
`;
```

### 2. Export Query

```typescript
// packages/graphql/src/queries/index.ts
export * from "./courses";
```

### 3. Use in Component

```vue
<template>
  <div v-if="loading">Loading...</div>
  <div v-else-if="error">Error: {{ error.message }}</div>
  <div v-else>
    <div v-for="course in result?.courses" :key="course.id">
      {{ course.title }}
    </div>
  </div>
</template>

<script setup lang="ts">
  import { useQuery } from "@lq/graphql";
  import { GET_COURSES } from "@lq/graphql/queries";

  const { result, loading, error } = useQuery(GET_COURSES);
</script>
```

## Next Steps

- Read the [full documentation](./README.md)
- Explore the [architecture](./docs/ARCHITECTURE.md)
- Review [contributing guidelines](./docs/CONTRIBUTING.md)
- Check out example code in the apps

## Need Help?

- Documentation: `/docs`
- Examples: `apps/` and `packages/`
- Issues: GitHub Issues
- Team: Ask in team chat

Happy coding!
