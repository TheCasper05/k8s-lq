# @lq/utils

Shared utility functions and helpers for LingoQuesto applications.

## Installation

This package is part of the LingoQuesto monorepo and is automatically available to all apps via workspace dependencies.

```json
{
  "dependencies": {
    "@lq/utils": "workspace:*"
  }
}
```

## Utilities

### Role-Based Routing

Centralized utilities for handling role-based route prefixes and navigation.

#### Constants

##### `ROLE_ROUTE_PREFIXES`

Maps user roles to their route prefixes:

```typescript
import { ROLE_ROUTE_PREFIXES } from "@lq/utils";

ROLE_ROUTE_PREFIXES[AccountType.STUDENT]; // "/student"
ROLE_ROUTE_PREFIXES[AccountType.TEACHER]; // "/teacher"
ROLE_ROUTE_PREFIXES[AccountType.ADMIN_INSTITUCIONAL]; // "/admin"
```

##### `ROLE_DASHBOARD_ROUTES`

Maps user roles to their dashboard routes:

```typescript
import { ROLE_DASHBOARD_ROUTES } from "@lq/utils";

ROLE_DASHBOARD_ROUTES[AccountType.STUDENT]; // "/student/dashboard"
ROLE_DASHBOARD_ROUTES[AccountType.TEACHER]; // "/teacher/dashboard"
ROLE_DASHBOARD_ROUTES[AccountType.ADMIN_INSTITUCIONAL]; // "/admin/dashboard"
```

#### Functions

##### `getRoleRoutePrefix(role)`

Returns the route prefix for a given role.

**Parameters:**

- `role: AccountType | string | null | undefined` - User role

**Returns:** `string` - Route prefix (e.g., "/student") or empty string if role is invalid

**Example:**

```typescript
import { getRoleRoutePrefix, AccountType } from "@lq/utils";

const prefix = getRoleRoutePrefix(AccountType.STUDENT);
console.log(prefix); // "/student"

const route = `${prefix}/courses`;
console.log(route); // "/student/courses"
```

##### `getRoleDashboardRoute(role)`

Returns the dashboard route for a given role.

**Parameters:**

- `role: AccountType | string | null | undefined` - User role

**Returns:** `string` - Dashboard route (e.g., "/student/dashboard") or "/" if role is invalid

**Example:**

```typescript
import { getRoleDashboardRoute } from "@lq/utils";

// Redirect to user's dashboard
const userRole = authStore.userProfile?.primaryRole;
await navigateTo(getRoleDashboardRoute(userRole));
```

### Other Utilities

#### Validators

Form validation helpers:

```typescript
import { isValidEmail, isValidPhone } from "@lq/utils";

isValidEmail("user@example.com"); // true
isValidPhone("+1234567890"); // true
```

#### Formatters

Data formatting utilities:

```typescript
import { formatDate, formatCurrency } from "@lq/utils";

formatDate(new Date(), "es"); // "3 de diciembre de 2025"
formatCurrency(1234.56, "USD", "es"); // "$1,234.56"
```

#### Debounce

Function debouncing utility:

```typescript
import { debounce } from "@lq/utils";

const debouncedSearch = debounce((query: string) => {
  // Search logic
}, 300);
```

#### Storage

LocalStorage helpers with type safety:

```typescript
import { storage } from "@lq/utils";

storage.set("user", { name: "John" });
const user = storage.get<User>("user");
storage.remove("user");
```

## Usage in Apps

### Nuxt App (student-teacher)

```typescript
// In composables
import { getRoleDashboardRoute, getRoleRoutePrefix } from "@lq/utils";

export const useRoleLayout = () => {
  const withRolePrefix = (path: string): string => {
    const role = currentRole.value;
    const prefix = getRoleRoutePrefix(role);
    return `${prefix}/${path}`;
  };

  return { withRolePrefix };
};
```

### Vue SPA (institutional)

```typescript
// In router guards
import { getRoleDashboardRoute } from "@lq/utils";

router.beforeEach((to, from, next) => {
  const userRole = store.state.auth.userRole;
  const dashboard = getRoleDashboardRoute(userRole);

  if (to.path === "/") {
    next(dashboard);
  } else {
    next();
  }
});
```

## Best Practices

### ✅ Do

- Use centralized utilities for role-based routing
- Import only what you need for better tree-shaking
- Use TypeScript types from `@lq/types` with these utilities

```typescript
import { getRoleRoutePrefix } from "@lq/utils";
import { AccountType } from "@lq/types";

const prefix = getRoleRoutePrefix(AccountType.STUDENT);
```

### ❌ Don't

- Hardcode route prefixes or dashboard routes
- Create custom role-to-route mappings
- Duplicate routing logic across files

```typescript
// ❌ Bad
const prefix = role === "STUDENT" ? "/student" : "/teacher";

// ✅ Good
const prefix = getRoleRoutePrefix(role);
```

## Development

### Adding New Utilities

1. Create a new file in `src/` (e.g., `src/my-utility.ts`)
2. Export your utility functions
3. Add exports to `src/index.ts`
4. Update this README with documentation
5. Add TypeScript types if needed

### Testing

```bash
# Run type checking
pnpm typecheck

# Build the package
pnpm build
```

## Dependencies

- `@lq/types` - Type definitions and enums
- `vue` - Vue 3 reactivity

## License

Private - LingoQuesto Internal Use Only
