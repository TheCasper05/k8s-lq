# Cross-Role Pages Pattern

## 📋 Table of Contents

- [Concept](#concept)
- [File Structure](#file-structure)
- [Implementation Pattern](#implementation-pattern)
- [Examples](#examples)
- [Best Practices](#best-practices)

---

## Concept

**Cross-role pages** are pages that share the same functionality and UI across all roles (Student, Teacher, Admin), but
maintain role-specific URLs for better organization and clarity.

### Features

- ✅ **Shared Code**: Single component for all roles
- ✅ **Prefixed URLs**: `/student/profile`, `/teacher/profile`, `/admin/profile`
- ✅ **Zero Duplication**: Centralized maintenance
- ✅ **Extensible**: Allows role-specific sections when needed

---

## File Structure

```
apps/student-teacher/
├── components/
│   └── pages/                          ← Shared page components
│       ├── ProfilePage.vue             ← Cross-role component
│       ├── SettingsPage.vue            ← Cross-role component
│       └── NotificationsPage.vue       ← Cross-role component
│
├── pages/
│   ├── profile/
│   │   └── index.vue                   ← Redirect to prefixed route
│   │
│   ├── student/
│   │   ├── dashboard.vue               ← Role-specific
│   │   ├── profile.vue                 ← ProfilePage wrapper
│   │   ├── settings.vue                ← SettingsPage wrapper
│   │   └── courses.vue                 ← Role-specific
│   │
│   ├── teacher/
│   │   ├── dashboard.vue               ← Role-specific
│   │   ├── profile.vue                 ← ProfilePage wrapper
│   │   ├── settings.vue                ← SettingsPage wrapper
│   │   └── classes.vue                 ← Role-specific
│   │
│   └── admin/
│       ├── dashboard.vue               ← Role-specific
│       ├── profile.vue                 ← ProfilePage wrapper
│       ├── settings.vue                ← SettingsPage wrapper
│       └── users.vue                   ← Role-specific
│
└── docs/
    └── CROSS_ROLE_PAGES.md            ← This document
```

---

## Implementation Pattern

### 1. Create the Shared Component

**Location**: `components/pages/[PageName]Page.vue`

```vue
<!-- components/pages/ProfilePage.vue -->
<script setup lang="ts">
  import { computed } from "vue";
  import ProfileHeader from "~/components/profile/ProfileHeader.vue";
  import PersonalInfoSection from "~/components/profile/PersonalInfoSection.vue";
  import ContactInfoSection from "~/components/profile/ContactInfoSection.vue";
  import SecuritySection from "~/components/profile/SecuritySection.vue";
  import { useProfileEditor } from "~/composables/useProfileEditor";

  // Shared composable for profile editing logic
  const { localProfile, isEditing, startEditing, cancelEditing, saveProfile, updateLocalProfile } = useProfileEditor();
</script>

<template>
  <div class="py-8 space-y-6">
    <!-- Profile Header -->
    <ProfileHeader />

    <!-- Profile Sections (common for all roles) -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <div class="lg:col-span-4">
        <PersonalInfoSection :profile="localProfile" :is-editing="isEditing" @update="updateLocalProfile" />
      </div>

      <div class="lg:col-span-8 space-y-6">
        <ContactInfoSection :profile="localProfile" :is-editing="isEditing" @update="updateLocalProfile" />

        <SecuritySection />

        <!-- Slot for role-specific content (optional) -->
        <slot name="role-specific" />
      </div>
    </div>
  </div>
</template>
```

### 2. Create Role-Specific Wrapper Pages

**Location**: `pages/[role]/[page-name].vue`

```vue
<!-- pages/student/profile.vue -->
<template>
  <ProfilePage />
</template>

<script setup lang="ts">
  import ProfilePage from "~/components/pages/ProfilePage.vue";

  definePageMeta({
    layout: "app", // Automatically adapts to role
  });
</script>
```

```vue
<!-- pages/teacher/profile.vue -->
<template>
  <ProfilePage />
</template>

<script setup lang="ts">
  import ProfilePage from "~/components/pages/ProfilePage.vue";

  definePageMeta({
    layout: "app",
  });
</script>
```

```vue
<!-- pages/admin/profile.vue -->
<template>
  <ProfilePage />
</template>

<script setup lang="ts">
  import ProfilePage from "~/components/pages/ProfilePage.vue";

  definePageMeta({
    layout: "app",
  });
</script>
```

> **Note**: All three wrapper pages are identical in this case since the Profile page doesn't require role-specific
> content. The slot `#role-specific` is available if needed in the future.

### 3. Create Redirect from Non-Prefixed Route (Optional)

**Location**: `pages/[page-name]/index.vue`

Use the `useRoleNavigation` composable from `@lq/composables`:

```vue
<!-- pages/profile/index.vue -->
<template>
  <div />
</template>

<script setup lang="ts">
  import { useRoleNavigation } from "@lq/composables";
  import { useRoleLayout } from "~/composables/useRoleLayout";

  definePageMeta({
    layout: false,
    middleware: [
      function () {
        const { currentRole } = useRoleLayout();
        const { redirectToRolePage } = useRoleNavigation(() => currentRole.value);
        return redirectToRolePage("/profile");
      },
    ],
  });
</script>
```

**`useRoleNavigation` Composable** (located in `packages/composables/src/useRoleNavigation.ts`):

The composable is centralized in `@lq/composables` and receives a `getCurrentRole` function as a parameter. This allows
it to be reusable across different apps in the monorepo.

```typescript
import type { UserRole } from "@lq/types";

export const useRoleNavigation = (getCurrentRole: () => UserRole | null) => {
  const router = useRouter();

  const getRolePrefix = (): string => {
    const role = getCurrentRole();
    const prefixes: Record<UserRole, string> = {
      STUDENT: "/student",
      TEACHER: "/teacher",
      ADMIN_INSTITUCIONAL: "/admin",
    };
    return role ? prefixes[role] : "";
  };

  const getRoleRoute = (page: string): string => {
    const prefix = getRolePrefix();
    const cleanPage = page.startsWith("/") ? page : `/${page}`;
    return `${prefix}${cleanPage}`;
  };

  const navigateToRolePage = async (page: string) => {
    const route = getRoleRoute(page);
    return router.push(route);
  };

  const redirectToRolePage = (page: string) => {
    const route = getRoleRoute(page);
    return navigateTo(route, { replace: true });
  };

  return {
    getRolePrefix,
    getRoleRoute,
    navigateToRolePage,
    redirectToRolePage,
  };
};
```

### 4. Update Sidebars with `withRolePrefix()`

Use the `withRolePrefix()` utility from `useRoleLayout` for automatic prefix handling:

```typescript
// components/layout-providers/Sidebars/StudentSidebar.vue
import { useRoleLayout } from "~/composables/useRoleLayout";

const { withRolePrefix } = useRoleLayout();

const studentMenuItems: MenuItem[] = [
  { label: "Dashboard", icon: "solar:home-2-linear", to: withRolePrefix("/dashboard") },
  { label: "Profile", icon: "solar:user-linear", to: withRolePrefix("/profile") }, // ✅
  { label: "Settings", icon: "solar:settings-linear", to: withRolePrefix("/settings") }, // ✅
];

// components/layout-providers/Sidebars/TeacherSidebar.vue
const { withRolePrefix } = useRoleLayout();

const teacherMenuGroups = [
  {
    label: "Account",
    items: [
      { label: "Profile", icon: "solar:user-linear", to: "/teacher/profile" }, // ✅
      { label: "Settings", icon: "solar:settings-linear", to: "/teacher/settings" }, // ✅
    ],
  },
];
```

---

## Examples

### Example 1: Profile (Implemented)

**Component**: `components/pages/ProfilePage.vue` **URLs**:

- `/student/profile` → Uses `ProfilePage`
- `/teacher/profile` → Uses `ProfilePage`
- `/admin/profile` → Uses `ProfilePage`
- `/profile` → Redirects based on role

**Features**:

- Shared profile form
- Shared security section
- Slot for role-specific content

### Example 2: Settings (Pending)

**Component**: `components/pages/SettingsPage.vue` **URLs**:

- `/student/settings`
- `/teacher/settings`
- `/admin/settings`

**Features**:

- Language preferences
- Theme (light/dark)
- Notifications
- Slot for role-specific settings

### Example 3: Notifications (Pending)

**Component**: `components/pages/NotificationsPage.vue` **URLs**:

- `/student/notifications`
- `/teacher/notifications`
- `/admin/notifications`

**Features**:

- Notifications list
- Shared filters
- Different notification types per role

### Example 4: Using the `useRoleNavigation` Composable

**In components for navigation:**

```vue
<template>
  <!-- Using getRoleRoute in NuxtLink -->
  <NuxtLink :to="getRoleRoute('/profile')">My Profile</NuxtLink>

  <!-- Programmatic navigation -->
  <Button @click="goToSettings">Settings</Button>
</template>

<script setup lang="ts">
  import { useRoleNavigation } from "@lq/composables";
  import { useRoleLayout } from "~/composables/useRoleLayout";

  const { currentRole } = useRoleLayout();
  const { getRoleRoute, navigateToRolePage } = useRoleNavigation(() => currentRole.value);

  const goToSettings = async () => {
    await navigateToRolePage("/settings");
  };
</script>
```

**In redirect pages:**

```vue
<!-- pages/settings/index.vue -->
<template>
  <div />
</template>

<script setup lang="ts">
  import { useRoleNavigation } from "@lq/composables";
  import { useRoleLayout } from "~/composables/useRoleLayout";

  definePageMeta({
    layout: false,
    middleware: [
      function () {
        const { currentRole } = useRoleLayout();
        const { redirectToRolePage } = useRoleNavigation(() => currentRole.value);
        return redirectToRolePage("/settings");
      },
    ],
  });
</script>
```

---

## Best Practices

### ✅ DO

1. **Use shared components** to avoid duplication

   ```vue
   <!-- ✅ CORRECT -->
   <template>
     <ProfilePage />
   </template>
   ```

2. **Maintain role-prefixed URLs**

   ```typescript
   // ✅ CORRECT
   {
     to: "/student/profile";
   }
   {
     to: "/teacher/profile";
   }
   {
     to: "/admin/profile";
   }
   ```

3. **Use slots for role-specific content**

   ```vue
   <!-- ✅ CORRECT -->
   <ProfilePage>
     <template #role-specific>
       <StudentSpecificSection />
     </template>
   </ProfilePage>
   ```

4. **Document cross-role pages** in this file

5. **Use i18n** for all translations
   ```vue
   <!-- ✅ CORRECT -->
   <h1>{{ $t('profile.title') }}</h1>
   ```

### ❌ DON'T

1. **DO NOT duplicate code** across roles

   ```vue
   <!-- ❌ INCORRECT -->
   <!-- pages/student/profile.vue -->
   <template>
     <div>
       <!-- 100 lines of duplicated code -->
     </div>
   </template>

   <!-- pages/teacher/profile.vue -->
   <template>
     <div>
       <!-- Same 100 duplicated lines -->
     </div>
   </template>
   ```

2. **DO NOT use non-prefixed routes** in menus

   ```typescript
   // ❌ INCORRECT
   {
     to: "/profile";
   }

   // ✅ CORRECT
   {
     to: "/student/profile";
   }
   ```

3. **DO NOT hardcode text** in components

   ```vue
   <!-- ❌ INCORRECT -->
   <h1>Profile</h1>

   <!-- ✅ CORRECT -->
   <h1>{{ $t('profile.title') }}</h1>
   ```

---

## Current Cross-Role Pages

| Page              | Component               | Status         | URLs                                                                           |
| ----------------- | ----------------------- | -------------- | ------------------------------------------------------------------------------ |
| **Profile**       | `ProfilePage.vue`       | ✅ Implemented | `/student/profile`<br>`/teacher/profile`<br>`/admin/profile`                   |
| **Design System** | N/A                     | ✅ No prefix   | `/design-system`                                                               |
| Settings          | `SettingsPage.vue`      | ⏳ Pending     | `/student/settings`<br>`/teacher/settings`<br>`/admin/settings`                |
| Notifications     | `NotificationsPage.vue` | ⏳ Pending     | `/student/notifications`<br>`/teacher/notifications`<br>`/admin/notifications` |

---

## Role-Specific Pages

These pages are **NOT** cross-role and should remain separate:

| Role        | Specific Pages                                              |
| ----------- | ----------------------------------------------------------- |
| **Student** | `dashboard`, `courses`, `assignments`, `progress`           |
| **Teacher** | `dashboard`, `classes`, `grading`, `materials`, `analytics` |
| **Admin**   | `dashboard`, `users`, `institutions`, `courses`, `logs`     |

---

## Navigation Flow

```
User clicks "Profile" in the menu
  ↓
Sidebar has the route with current role prefix
  ↓
Navigates to /student/profile (or /teacher/profile, /admin/profile)
  ↓
Wrapper page loads shared ProfilePage
  ↓
ProfilePage renders common content
  ↓
Slot #role-specific renders specific content (if exists)
```

---

## Maintenance

### To add a new cross-role page:

1. **Create shared component** in `components/pages/`
2. **Create wrappers** in `pages/student/`, `pages/teacher/`, `pages/admin/`
3. **Create redirect** in `pages/[name]/index.vue` (optional)
4. **Update sidebars** with prefixed routes
5. **Add translations** in i18n
6. **Document** in this file

### To modify a cross-role page:

1. **Edit only** the component in `components/pages/`
2. Changes are automatically reflected in all roles
3. If you need role-specific changes, use the `#role-specific` slot

---

## Centralized Routing System

### Overview

Cross-role pages integrate with the **centralized role-based routing system** from `@lq/utils` for automatic prefix
handling.

### Core Utilities

All role-to-route mappings are centralized in `packages/utils/src/role-routes.ts`:

```typescript
import { AccountType } from "@lq/types";

export const ROLE_ROUTE_PREFIXES: Record<AccountType, string> = {
  [AccountType.STUDENT]: "/student",
  [AccountType.TEACHER]: "/teacher",
  [AccountType.ADMIN_INSTITUCIONAL]: "/admin",
};

export function getRoleRoutePrefix(role: AccountType): string {
  return ROLE_ROUTE_PREFIXES[role] || "";
}
```

### `withRolePrefix()` Utility

The `useRoleLayout` composable provides `withRolePrefix()` for automatic route prefixing:

```typescript
import { useRoleLayout } from "~/composables/useRoleLayout";

const { withRolePrefix } = useRoleLayout();

// Automatically adds role prefix based on current user
const menuItems = [
  { label: "Profile", to: withRolePrefix("/profile") },
  // For student: "/student/profile"
  // For teacher: "/teacher/profile"
  // For admin: "/admin/profile"
];
```

### Benefits

1. **No Hardcoded Prefixes**: Routes are clean and maintainable
2. **Single Source of Truth**: All prefixes defined in `@lq/utils`
3. **Type Safety**: Full TypeScript support with `AccountType` enum
4. **Automatic Updates**: Change prefix in one place, updates everywhere

### Migration Example

**Before** (hardcoded):

```typescript
const studentMenuItems = [
  { label: "Profile", to: "/student/profile" },
  { label: "Settings", to: "/student/settings" },
];
```

**After** (automatic):

```typescript
const { withRolePrefix } = useRoleLayout();

const studentMenuItems = [
  { label: "Profile", to: withRolePrefix("/profile") },
  { label: "Settings", to: withRolePrefix("/settings") },
];
```

---

## Related Resources

- [Layout Architecture](./LAYOUT_ARCHITECTURE.md) - Complete layout system documentation
- [Main Architecture](../../docs/ARCHITECTURE.md) - Project-wide architecture including routing system
- `packages/utils/README.md` - Documentation for `@lq/utils` routing utilities
- `packages/utils/src/role-routes.ts` - Source code for routing utilities

---

**Last Updated**: December 3, 2025  
**Maintained by**: LingoQuesto Development Team
