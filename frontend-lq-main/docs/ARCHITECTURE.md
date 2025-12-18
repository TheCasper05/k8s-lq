# Architecture Overview

## Monorepo Structure

LingoQuesto frontend uses a monorepo architecture managed by pnpm workspaces. This allows code sharing while maintaining
separation of concerns.

```
frontend-lq/
├── apps/           # Applications
├── packages/       # Shared packages
├── shared/         # Shared configuration
└── tests/          # Tests
```

## Applications

### Student-Teacher App (Nuxt 4)

**Technology**: Nuxt 4, Vue 3, TypeScript

**Purpose**: Application for students and teachers to create and consume educational content.

**Key Features**:

- Server-side rendering (SSR)
- File-based routing
- Auto-imports
- Built-in i18n
- Nuxt modules ecosystem

**Structure**:

```
apps/student-teacher/
├── pages/          # Auto-routed pages
├── components/     # Vue components
├── composables/    # Composition functions
├── middleware/     # Route middleware
├── plugins/        # Nuxt plugins
├── layouts/        # Page layouts
└── locales/        # Translations
```

### Institutional App (Vue 3 + Vite)

**Technology**: Vue 3, Vite, TypeScript

**Purpose**: Administrative portal for institutional management.

**Key Features**:

- Fast development with Vite
- Single Page Application (SPA)
- Vue Router for routing
- Lightweight and fast

**Structure**:

```
apps/institutional/
└── src/
    ├── views/      # Pages
    ├── components/ # Vue components
    ├── router/     # Vue Router
    ├── plugins/    # Vue plugins
    └── locales/    # Translations
```

## Shared Packages

### UI Package (@lq/ui)

**Atomic Design System**

Following Brad Frost's Atomic Design methodology:

1. **Atoms**: Basic building blocks
   - Buttons, Inputs, Badges, Spinners
   - Self-contained, reusable
   - No dependencies on other components

2. **Molecules**: Simple combinations
   - Cards, Modals, SearchBars
   - Combine atoms
   - Single responsibility

3. **Organisms**: Complex components
   - DataTables, Navbars
   - Combine molecules and atoms
   - Feature-complete sections

4. **Templates**: Page layouts
   - Wireframes for pages
   - No real content

5. **Pages**: Full pages
   - Real content
   - App-specific

**Why Atomic Design?**

- Consistency across apps
- Easier to maintain
- Reusable components
- Clear component hierarchy

### Cross-Framework UI Architecture

**Problem**: Components in `@lq/ui` need to work in both **Nuxt 4** (student-teacher) and **Vue 3 SPA** (institutional),
but each framework has specific components (NuxtLink vs RouterLink, Nuxt Icon vs Iconify).

**Solution**: Framework-agnostic base components + app-specific wrappers

#### Architecture Pattern

```
@lq/ui (Base Components)
    ↓
App Wrappers (Framework-specific)
    ↓
App Usage (Clean API)
```

#### Base Components (`@lq/ui`)

Components are **UI-only** and receive framework-specific implementations via props/slots:

```vue
<!-- packages/ui/src/atoms/SidebarNavItem.vue -->
<template>
  <component :is="linkComponent" :to="to" :class="linkClasses">
    <!-- Framework provides icon implementation -->
    <slot name="icon" :icon="icon" :icon-class="iconSize">
      <span>{{ icon }}</span>
    </slot>
    <span v-if="label">{{ label }}</span>
  </component>
</template>

<script setup>
  defineProps({
    to: String,
    icon: String,
    label: String,
    linkComponent: { type: [Object, String], default: "a" },
    currentPath: String, // For active state
  });
</script>
```

**Key Principles**:

- No framework-specific imports
- Accept components via props
- Use slots for customization
- Pure UI logic only

#### App Wrappers

Each app creates wrappers that inject framework-specific implementations:

**Nuxt Wrapper** (`apps/student-teacher/components/NavItem.vue`):

```vue
<template>
  <SidebarNavItem v-bind="$attrs" :link-component="NuxtLink" :current-path="route.path">
    <template #icon="{ icon, iconClass }">
      <Icon :name="icon" :class="iconClass" />
    </template>
  </SidebarNavItem>
</template>

<script setup>
  import { SidebarNavItem } from "@lq/ui";
  const NuxtLink = resolveComponent("NuxtLink");
  const route = useRoute();
</script>
```

**Vue SPA Wrapper** (`apps/institutional/src/components/NavItem.vue`):

```vue
<template>
  <SidebarNavItem v-bind="$attrs" :link-component="RouterLink" :current-path="route.path">
    <template #icon="{ icon, iconClass }">
      <span v-if="icon.includes(':')" class="iconify" :data-icon="icon" :class="iconClass" />
      <i v-else :class="[icon, iconClass]" />
    </template>
  </SidebarNavItem>
</template>

<script setup>
  import { SidebarNavItem } from "@lq/ui";
  import { RouterLink, useRoute } from "vue-router";
  const route = useRoute();
</script>
```

#### Usage in Apps

**Same API, different implementations**:

```vue
<!-- Nuxt App -->
<NavItem to="/dashboard" icon="solar:home-2-linear" label="Dashboard" />

<!-- Vue SPA -->
<NavItem to="/dashboard" icon="solar:home-2-linear" label="Dashboard" />
```

#### Benefits

| Approach                 | Result                       |
| ------------------------ | ---------------------------- |
| ✅ **No Adapters**       | Simple, explicit code        |
| ✅ **No Plugins**        | Zero configuration needed    |
| ✅ **No provide/inject** | Easy to debug                |
| ✅ **Type Safe**         | Full TypeScript support      |
| ✅ **Maintainable**      | Clear separation of concerns |
| ✅ **Flexible**          | Easy to add new frameworks   |

#### File Structure

```
packages/ui/
└── src/
    ├── atoms/
    │   └── SidebarNavItem.vue    # Framework-agnostic
    └── utils/
        └── routing.ts             # Shared utilities

apps/student-teacher/
└── components/
    └── NavItem.vue                # Nuxt wrapper

apps/institutional/
└── src/
    └── components/
        └── NavItem.vue            # Vue SPA wrapper
```

#### Guidelines

**✅ Do**:

- Keep base components framework-agnostic
- Accept components via props
- Use slots for customization
- Create thin wrappers per app

**❌ Don't**:

- Import framework-specific components in `@lq/ui`
- Use provide/inject for framework adapters
- Create complex plugin systems
- Duplicate UI logic in wrappers

### GraphQL Package (@lq/graphql)

**Apollo Client Configuration**

**Features**:

- HTTP link for queries/mutations
- WebSocket link for subscriptions
- Authentication integration
- Error handling
- Cache management
- Type generation

**Architecture**:

```typescript
                    ┌─────────────────┐
                    │  Apollo Client  │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │   Split Link    │
                    └────────┬────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
        ┌───────┴──────┐          ┌──────┴──────┐
        │  HTTP Link   │          │  WS Link    │
        │ (Query/Mut)  │          │   (Subs)    │
        └───────┬──────┘          └──────┬──────┘
                │                        │
        ┌───────┴──────┐          ┌──────┴──────┐
        │  Auth Link   │          │  WS Client  │
        └───────┬──────┘          └─────────────┘
                │
        ┌───────┴──────┐
        │  Error Link  │
        └──────────────┘
```

**Cache Policies**:

- Type-based caching
- Field-level policies
- Merge strategies
- Eviction helpers

### Stores Package (@lq/stores)

**Pinia Stores**

**Stores**:

1. **Auth Store**
   - User authentication
   - Token management
   - Role-based access

2. **User Store**
   - User profile
   - Preferences
   - Settings

3. **Notification Store**
   - In-app notifications
   - Toast messages
   - Notification history

4. **Metrics Store**
   - Analytics tracking
   - Page views
   - User events

**Store Pattern**:

```typescript
export const useMyStore = defineStore("my-store", () => {
  // State (reactive)
  const data = ref<Data | null>(null);
  const loading = ref(false);
  const error = ref<Error | null>(null);

  // Getters (computed)
  const hasData = computed(() => !!data.value);

  // Actions (functions)
  async function fetchData() {
    loading.value = true;
    try {
      // Fetch data
      data.value = await api.getData();
    } catch (err) {
      error.value = err;
    } finally {
      loading.value = false;
    }
  }

  return {
    data,
    loading,
    error,
    hasData,
    fetchData,
  };
});
```

### Utils Package (@lq/utils)

**Utility Functions**

**Modules**:

- Validators: Email, password, phone, etc.
- Formatters: Currency, numbers, dates, text
- Date utilities: Formatting, relative time, calculations
- Storage: localStorage/sessionStorage wrappers
- Metrics: Analytics tracking
- Debounce/Throttle: Performance utilities

## Data Flow

### Request Flow

```
User Action
    ↓
Component Event
    ↓
Store Action
    ↓
GraphQL Mutation/Query
    ↓
Apollo Client
    ↓
Backend API
    ↓
Response
    ↓
Cache Update
    ↓
Store State Update
    ↓
Component Re-render
```

### State Management

```
                     ┌──────────────┐
                     │  Backend API │
                     └──────┬───────┘
                            │
                    ┌───────┴────────┐
                    │ Apollo Cache   │
                    └───────┬────────┘
                            │
                    ┌───────┴────────┐
                    │ Pinia Stores   │
                    └───────┬────────┘
                            │
                    ┌───────┴────────┐
                    │  Components    │
                    └────────────────┘
```

## Security

### Authentication Flow

```
1. User logs in → Login mutation
2. Backend returns JWT + refresh token
3. Store tokens in auth store + localStorage
4. Apollo client adds token to headers
5. All requests include auth header
6. On 401 error → refresh token
7. If refresh fails → logout user
```

### Route Protection

```
Navigation
    ↓
Global Guard (middleware)
    ↓
Check Authentication
    ↓
┌───────┴──────┐
│ Authenticated │ Not Authenticated
↓               ↓
Check Roles     Redirect to Login
↓
Has Role / No Role
↓              ↓
Continue    Redirect to Unauthorized
```

## Performance

### Code Splitting

- Route-based splitting
- Component lazy loading
- Dynamic imports

```typescript
// Route-based
const Dashboard = () => import("./views/Dashboard.vue");

// Component lazy loading
const HeavyComponent = defineAsyncComponent(() => import("./components/HeavyComponent.vue"));
```

### Caching Strategy

1. **Apollo Cache**: Normalized cache for GraphQL
2. **Route Cache**: Nuxt page caching
3. **Component Cache**: Keep-alive for frequently used components

### Build Optimization

- Tree shaking
- Code splitting
- Asset optimization
- Compression (gzip/brotli)

## Testing Strategy

### Test Pyramid

```
         E2E Tests
       (Playwright)
          /\
         /  \
        /    \
       /------\
      / Integr \
     /   Tests  \
    /------------\
   /              \
  /  Unit Tests    \
 /   (Vitest)      \
/------------------\
```

### Coverage Goals

- Unit: 80%+ coverage
- Integration: Critical flows
- E2E: Main user journeys

## Deployment

### Build Process

```
1. Install dependencies → pnpm install
2. Lint code → pnpm lint
3. Type check → pnpm typecheck
4. Run tests → pnpm test
5. Build apps → pnpm build
6. Deploy to hosting
```

### Environments

- **Development**: Local development
- **Staging**: Pre-production testing
- **Production**: Live environment

Each environment has separate:

- API endpoints
- Sentry configuration
- Feature flags
- Environment variables

## Monitoring

### Error Tracking

- **Sentry**: Error tracking and monitoring
- Per-app configuration
- Source maps for debugging
- Performance monitoring

### Analytics

- Page view tracking
- User event tracking
- Session duration
- Custom metrics

## Best Practices

1. **Component Design**
   - Keep components small
   - Single responsibility
   - Reusable and composable

2. **State Management**
   - Use stores for shared state
   - Keep local state in components
   - Avoid prop drilling

3. **Type Safety**
   - Define types for all data
   - Use TypeScript strictly
   - Generate types from GraphQL

4. **Performance**
   - Lazy load routes
   - Optimize images
   - Minimize bundle size

5. **Testing**
   - Test user behavior, not implementation
   - Write tests first (TDD)
   - Keep tests simple

6. **Security**
   - Validate all inputs
   - Sanitize user content
   - Use CSP headers
   - Keep dependencies updated

## Role-Based Routing System

### Overview

LingoQuesto implements a centralized role-based routing system that automatically handles route prefixes and access
control based on user roles.

### Architecture

```
@lq/types (Enums & Types)
    ↓
@lq/utils (Routing Utilities)
    ↓
App Composables (useRoleLayout)
    ↓
Middleware & Components
```

### Core Components

#### 1. AccountType Enum (`@lq/types`)

Single source of truth for user roles:

```typescript
export enum AccountType {
  STUDENT = "STUDENT",
  TEACHER = "TEACHER",
  ADMIN_INSTITUCIONAL = "ADMIN_INSTITUCIONAL",
}
```

#### 2. Role-Routes Utilities (`@lq/utils`)

Centralized route mappings and helpers:

```typescript
// Route prefix mapping
export const ROLE_ROUTE_PREFIXES: Record<AccountType, string> = {
  [AccountType.STUDENT]: "/student",
  [AccountType.TEACHER]: "/teacher",
  [AccountType.ADMIN_INSTITUCIONAL]: "/admin",
};

// Dashboard route mapping
export const ROLE_DASHBOARD_ROUTES: Record<AccountType, string> = {
  [AccountType.STUDENT]: "/student/dashboard",
  [AccountType.TEACHER]: "/teacher/dashboard",
  [AccountType.ADMIN_INSTITUCIONAL]: "/admin/dashboard",
};

// Helper functions
export function getRoleRoutePrefix(role: AccountType): string;
export function getRoleDashboardRoute(role: AccountType): string;
```

#### 3. useRoleLayout Composable

Provides `withRolePrefix()` for automatic prefix handling:

```typescript
const { withRolePrefix } = useRoleLayout();

// Automatically adds role prefix based on current user
const menuItems = [
  { label: "Dashboard", to: withRolePrefix("/dashboard") },
  { label: "Courses", to: withRolePrefix("/courses") },
];

// For a student: "/dashboard" → "/student/dashboard"
// For a teacher: "/dashboard" → "/teacher/dashboard"
```

#### 4. Role Guard Middleware

Protects routes and redirects unauthorized access:

```typescript
// Automatically checks if user can access route
// Redirects to appropriate dashboard if unauthorized
export default defineNuxtRouteMiddleware((to) => {
  const userRolePrefix = getRoleRoutePrefix(userRole);
  const roleSpecificPrefixes = Object.values(ROLE_ROUTE_PREFIXES);

  if (isRoleSpecificRoute && !to.path.startsWith(userRolePrefix)) {
    return navigateTo(getRoleDashboardRoute(userRole));
  }
});
```

### Benefits

1. **Single Source of Truth**: All role-route mappings in one place
2. **Type Safety**: Full TypeScript support with enums
3. **DRY Principle**: No route prefix duplication
4. **Automatic Prefixing**: Routes automatically get correct prefix
5. **Centralized Logic**: Easy to maintain and update
6. **SSR Compatible**: Works with Nuxt's server-side rendering

### Usage Examples

#### Sidebar Configuration

```typescript
// Clean routes without hardcoded prefixes
const { withRolePrefix } = useRoleLayout();

const menuItems = [
  { label: "Dashboard", to: withRolePrefix("/dashboard") },
  { label: "Profile", to: withRolePrefix("/profile") },
  { label: "Settings", to: withRolePrefix("/settings") },
];
```

#### Programmatic Navigation

```typescript
import { getRoleDashboardRoute } from "@lq/utils";

// Redirect to user's dashboard
const userRole = authStore.userProfile?.primaryRole;
await navigateTo(getRoleDashboardRoute(userRole));
```

#### Route Protection

```typescript
// Middleware automatically handles protection
// No manual checks needed in components
```

### File Structure

```
packages/
├── types/
│   └── src/
│       ├── enums.ts              # AccountType enum
│       └── auth.ts               # User types with AccountType
├── utils/
│   └── src/
│       └── role-routes.ts        # Routing utilities
└── composables/
    └── src/
        └── useRoleNavigation.ts  # Navigation helpers

apps/student-teacher/
├── composables/
│   └── useRoleLayout.ts          # withRolePrefix()
├── middleware/
│   ├── role-guard.global.ts      # Route protection
│   └── onboarding.global.ts      # Onboarding flow
└── components/
    └── layout-providers/
        └── Sidebars/             # Role-specific sidebars
```

### Migration Guide

When adding new routes:

1. **Don't** hardcode role prefixes:

   ```typescript
   // ❌ Bad
   {
     to: "/student/new-feature";
   }
   ```

2. **Do** use `withRolePrefix()`:

   ```typescript
   // ✅ Good
   {
     to: withRolePrefix("/new-feature");
   }
   ```

3. **Don't** create custom route mappings:

   ```typescript
   // ❌ Bad
   const routes = {
     STUDENT: "/student/page",
     TEACHER: "/teacher/page",
   };
   ```

4. **Do** use centralized utilities:
   ```typescript
   // ✅ Good
   import { getRoleRoutePrefix } from "@lq/utils";
   const route = `${getRoleRoutePrefix(role)}/page`;
   ```
