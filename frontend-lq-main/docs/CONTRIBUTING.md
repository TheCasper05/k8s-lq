# Contributing Guide

Thank you for contributing to LingoQuesto! This guide will help you get started.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## Getting Started

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Commit with conventional commits
5. Push and create a pull request

## Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes
- `build`: Build system changes

### Scopes

- `student-teacher`: Student-teacher app
- `institutional`: Institutional app
- `ui`: UI package
- `graphql`: GraphQL package
- `stores`: Stores package
- `utils`: Utils package
- `deps`: Dependencies
- `config`: Configuration files

### Examples

```bash
feat(student-teacher): add course creation page
fix(ui): resolve button loading state issue
docs(graphql): update Apollo Client documentation
refactor(stores): simplify auth store logic
test(utils): add tests for date formatters
```

## Branch Naming

Use descriptive branch names:

```
feature/user-authentication
fix/navbar-responsive-issue
refactor/simplify-apollo-config
docs/update-readme
```

## Code Style

### TypeScript

- Use TypeScript for all new code
- Define types for all functions and components
- Avoid `any` type unless absolutely necessary
- Use interfaces for object shapes

### Vue Components

- Use Composition API with `<script setup>`
- Define props with TypeScript types
- Use `defineEmits` for events
- Keep components small and focused

```vue
<template>
  <div>{{ message }}</div>
</template>

<script setup lang="ts">
  interface Props {
    message: string;
  }

  const props = defineProps<Props>();
  const emit = defineEmits<{
    click: [id: string];
  }>();
</script>
```

### File Naming

- Components: PascalCase (`UserProfile.vue`)
- Utilities: camelCase (`formatDate.ts`)
- Types: PascalCase (`User.ts`)
- Constants: UPPER_SNAKE_CASE (`API_URL.ts`)

## Testing

### Writing Tests

- Write tests for all new features
- Update tests when changing existing code
- Aim for high code coverage
- Test edge cases and error scenarios

### Running Tests

```bash
# Unit tests
pnpm test:unit

# E2E tests
pnpm test:e2e

# Watch mode
pnpm test:unit --watch
```

## Pull Request Process

1. **Before Creating PR**:
   - Run linting: `pnpm lint`
   - Run tests: `pnpm test`
   - Run type check: `pnpm typecheck`
   - Update documentation if needed

2. **PR Title**: Use conventional commit format

   ```
   feat(ui): add dark mode support
   ```

3. **PR Description**:
   - Describe what changed and why
   - Reference related issues
   - Add screenshots for UI changes
   - List breaking changes

4. **Review Process**:
   - Address review comments
   - Keep commits clean and organized
   - Squash commits if requested

## Adding a New Package

1. Create package directory:

   ```bash
   mkdir -p packages/my-package/src
   ```

2. Add `package.json`:

   ```json
   {
     "name": "@lq/my-package",
     "version": "1.0.0",
     "private": true,
     "type": "module",
     "main": "./src/index.ts"
   }
   ```

3. Add to workspace (already configured in `pnpm-workspace.yaml`)

4. Install in apps:
   ```bash
   cd apps/student-teacher
   pnpm add @lq/my-package@workspace:*
   ```

## Adding a New Component

1. Create component file in appropriate package:

   ```bash
   # For shared UI component
   packages/ui/src/atoms/MyComponent.vue

   # For app-specific component
   apps/student-teacher/components/MyComponent.vue
   ```

2. Follow atomic design principles:
   - **Atoms**: Basic building blocks (Button, Input)
   - **Molecules**: Simple combinations (SearchBar, Card)
   - **Organisms**: Complex components (DataTable, Navbar)
   - **Templates**: Page templates
   - **Pages**: Full pages

3. Export from package index:

   ```typescript
   // packages/ui/src/index.ts
   export { default as MyComponent } from "./atoms/MyComponent.vue";
   ```

4. Write tests:

   ```typescript
   // tests/unit/components/MyComponent.test.ts
   import { describe, it, expect } from "vitest";
   import { mount } from "@vue/test-utils";
   import { MyComponent } from "@lq/ui";

   describe("MyComponent", () => {
     it("renders correctly", () => {
       const wrapper = mount(MyComponent);
       expect(wrapper.exists()).toBe(true);
     });
   });
   ```

## Adding GraphQL Operations

1. Create operation file:

   ```typescript
   // packages/graphql/src/queries/users.ts
   import { gql } from "@apollo/client/core";

   export const GET_USERS = gql`
     query GetUsers {
       users {
         id
         email
         name
       }
     }
   `;
   ```

2. Export from index:

   ```typescript
   // packages/graphql/src/queries/index.ts
   export * from "./users";
   ```

3. Generate types:
   ```bash
   pnpm graphql:codegen
   ```

## Questions?

- Check existing documentation
- Ask in team chat
- Create an issue for bugs
- Request features through issues

Thank you for contributing!
