# Guia de Desarrollo

## indice

1. [Flujo de Trabajo](#flujo-de-trabajo)
2. [Estructura del Proyecto](#estructura-del-proyecto)
3. [Desarrollo de Componentes](#desarrollo-de-componentes)
4. [Estado y Stores](#estado-y-stores)
5. [GraphQL](#graphql)
6. [Rutas y Navegacion](#rutas-y-navegacion)
7. [Internacionalizacion (i18n)](#internacionalizacion-i18n)
8. [Estilado](#estilado)
9. [Testing](#testing)
10. [Debugging](#debugging)
11. [Mejores Practicas](#mejores-practicas)

## Flujo de Trabajo

### Desarrollo Diario

1. **Inicio del Dia**:

   ```bash
   # Actualizar dependencias si es necesario
   git pull
   pnpm install

   # Iniciar servidor de desarrollo
   pnpm dev:student-teacher
   ```

2. **Mientras Desarrollas**:
   - Usa hot reload automatico (cambios se reflejan instantaneamente)
   - Ejecuta lint al guardar (configurado en VSCode)
   - Revisa la consola del navegador para errores

3. **Antes de Commitear**:

   ```bash
   # Lint y fix
   pnpm lint:fix

   # Type check
   pnpm typecheck

   # Run tests
   pnpm test

   # Commit con conventional commits
   git commit -m "feat(scope): descripcion"
   ```

### Trabajar con Turborepo

```bash
# Ejecutar solo la app que necesitas
pnpm dev:student-teacher

# Build solo un paquete y sus dependientes
turbo run build --filter=@lq/ui...

# Test solo lo que cambio
turbo run test --filter=[main]

# Ver que se ejecutaria sin ejecutarlo
turbo run build --dry-run

# Mas informacion en docs/TURBO.md
```

## Estructura del Proyecto

### Apps

#### Student-Teacher (Nuxt 4)

```
apps/student-teacher/
├── assets/              # Assets estaticos (CSS, imagenes)
├── components/          # Componentes de la app
├── composables/         # Composables de Vue
├── i18n/                # Traducciones
│   └── locales/
│       ├── en/
│       └── es/
├── layouts/             # Layouts de paginas
├── middleware/          # Middlewares de ruta
├── pages/               # Paginas (file-based routing)
├── plugins/             # Plugins de Nuxt
├── public/              # Assets publicos
├── app.vue              # Componente raiz
└── nuxt.config.ts       # Configuracion de Nuxt
```

#### Institutional (Vue 3 + Vite)

```
apps/institutional/
└── src/
    ├── assets/          # Assets estaticos
    ├── components/      # Componentes de la app
    ├── locales/         # Traducciones
    ├── plugins/         # Plugins de Vue
    ├── router/          # Vue Router
    ├── views/           # Paginas/Vistas
    ├── App.vue          # Componente raiz
    └── main.ts          # Entry point
```

### Packages

```
packages/
├── ui/                  # Componentes compartidos
│   └── src/
│       ├── atoms/       # Componentes basicos
│       ├── molecules/   # Componentes simples
│       ├── organisms/   # Componentes complejos
│       └── types/       # Tipos TypeScript
├── graphql/             # Cliente GraphQL
│   └── src/
│       ├── queries/     # Queries
│       ├── mutations/   # Mutations
│       └── subscriptions/ # Subscriptions
├── stores/              # Pinia stores
│   └── src/
│       ├── auth.ts
│       ├── user.ts
│       └── notification.ts
└── utils/               # Utilidades
    └── src/
        ├── validators.ts
        ├── formatters.ts
        └── date.ts
```

## Desarrollo de Componentes

### Atomic Design

Seguimos el principio de Atomic Design:

#### Atoms (Componentes Basicos)

```vue
<!-- packages/ui/src/atoms/Button.vue -->
<template>
  <button :class="buttonClasses" :disabled="disabled || loading" @click="handleClick">
    <span v-if="loading" class="spinner"></span>
    <slot v-else />
  </button>
</template>

<script setup lang="ts">
  interface Props {
    variant?: "primary" | "secondary" | "danger";
    disabled?: boolean;
    loading?: boolean;
  }

  const props = withDefaults(defineProps<Props>(), {
    variant: "primary",
    disabled: false,
    loading: false,
  });

  const emit = defineEmits<{
    click: [event: MouseEvent];
  }>();

  const buttonClasses = computed(() => ({
    "btn": true,
    [`btn-${props.variant}`]: true,
    "btn-disabled": props.disabled,
    "btn-loading": props.loading,
  }));

  function handleClick(event: MouseEvent) {
    if (!props.disabled && !props.loading) {
      emit("click", event);
    }
  }
</script>
```

#### Molecules (Componentes Compuestos)

```vue
<!-- packages/ui/src/molecules/SearchBar.vue -->
<template>
  <div class="search-bar">
    <Input v-model="searchQuery" :placeholder="placeholder" @keyup.enter="handleSearch" />
    <Button @click="handleSearch">Buscar</Button>
  </div>
</template>

<script setup lang="ts">
  import { ref } from "vue";
  import { Input, Button } from "../atoms";

  interface Props {
    placeholder?: string;
    modelValue?: string;
  }

  const props = withDefaults(defineProps<Props>(), {
    placeholder: "Buscar...",
    modelValue: "",
  });

  const emit = defineEmits<{
    "search": [query: string];
    "update:modelValue": [value: string];
  }>();

  const searchQuery = computed({
    get: () => props.modelValue,
    set: (value) => emit("update:modelValue", value),
  });

  function handleSearch() {
    emit("search", searchQuery.value);
  }
</script>
```

#### Organisms (Componentes Complejos)

```vue
<!-- packages/ui/src/organisms/DataTable.vue -->
<template>
  <div class="data-table">
    <SearchBar v-model="searchQuery" @search="handleSearch" />

    <table>
      <thead>
        <tr>
          <th v-for="column in columns" :key="column.key">
            {{ column.label }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in filteredData" :key="row.id">
          <td v-for="column in columns" :key="column.key">
            {{ row[column.key] }}
          </td>
        </tr>
      </tbody>
    </table>

    <Pagination v-model="currentPage" :total-pages="totalPages" />
  </div>
</template>

<script setup lang="ts">
  // Implementation...
</script>
```

### Composables

Los composables son funciones reutilizables que encapsulan logica:

```typescript
// apps/student-teacher/composables/useAuth.ts
export function useAuth() {
  const authStore = useAuthStore();
  const router = useRouter();

  const isAuthenticated = computed(() => authStore.isAuthenticated);
  const user = computed(() => authStore.userProfile);

  async function login(email: string, password: string) {
    try {
      await authStore.login(email, password);
      await router.push("/dashboard");
    } catch (error) {
      console.error("Login failed:", error);
      throw error;
    }
  }

  async function logout() {
    await authStore.logout();
    await router.push("/login");
  }

  return {
    isAuthenticated,
    user,
    login,
    logout,
  };
}
```

Uso:

```vue
<script setup lang="ts">
  const { isAuthenticated, user, logout } = useAuth();
</script>
```

## Estado y Stores

### Pinia Stores

#### Definir un Store

```typescript
// packages/stores/src/course.ts
import { defineStore } from "pinia";
import { ref, computed } from "vue";

export interface Course {
  id: string;
  title: string;
  description: string;
}

export const useCourseStore = defineStore("course", () => {
  // State
  const courses = ref<Course[]>([]);
  const loading = ref(false);
  const error = ref<Error | null>(null);

  // Getters
  const courseCount = computed(() => courses.value.length);
  const activeCourses = computed(() => courses.value.filter((c) => c.isActive));

  // Actions
  async function fetchCourses() {
    loading.value = true;
    error.value = null;

    try {
      // GraphQL query
      const { data } = await apolloClient.query({
        query: GET_COURSES,
      });
      courses.value = data.courses;
    } catch (e) {
      error.value = e as Error;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function createCourse(input: CreateCourseInput) {
    loading.value = true;

    try {
      const { data } = await apolloClient.mutate({
        mutation: CREATE_COURSE,
        variables: { input },
      });
      courses.value.push(data.createCourse);
      return data.createCourse;
    } catch (e) {
      error.value = e as Error;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  function $reset() {
    courses.value = [];
    loading.value = false;
    error.value = null;
  }

  return {
    // State
    courses,
    loading,
    error,
    // Getters
    courseCount,
    activeCourses,
    // Actions
    fetchCourses,
    createCourse,
    $reset,
  };
});
```

#### Usar un Store

```vue
<script setup lang="ts">
  import { useCourseStore } from "@lq/stores";

  const courseStore = useCourseStore();

  onMounted(() => {
    courseStore.fetchCourses();
  });
</script>

<template>
  <div>
    <div v-if="courseStore.loading">Cargando...</div>
    <div v-else-if="courseStore.error">Error: {{ courseStore.error.message }}</div>
    <div v-else>
      <div v-for="course in courseStore.courses" :key="course.id">
        {{ course.title }}
      </div>
    </div>
  </div>
</template>
```

## GraphQL

### Queries

```typescript
// packages/graphql/src/queries/courses.ts
import { gql } from "@apollo/client/core";

export const GET_COURSES = gql`
  query GetCourses($limit: Int, $offset: Int) {
    courses(limit: $limit, offset: $offset) {
      id
      title
      description
      createdAt
      updatedAt
    }
  }
`;

export const GET_COURSE = gql`
  query GetCourse($id: ID!) {
    course(id: $id) {
      id
      title
      description
      lessons {
        id
        title
        order
      }
    }
  }
`;
```

### Mutations

```typescript
// packages/graphql/src/mutations/courses.ts
import { gql } from "@apollo/client/core";

export const CREATE_COURSE = gql`
  mutation CreateCourse($input: CreateCourseInput!) {
    createCourse(input: $input) {
      id
      title
      description
    }
  }
`;

export const UPDATE_COURSE = gql`
  mutation UpdateCourse($id: ID!, $input: UpdateCourseInput!) {
    updateCourse(id: $id, input: $input) {
      id
      title
      description
    }
  }
`;
```

### Subscriptions

```typescript
// packages/graphql/src/subscriptions/courses.ts
import { gql } from "@apollo/client/core";

export const COURSE_UPDATED = gql`
  subscription CourseUpdated($courseId: ID!) {
    courseUpdated(courseId: $courseId) {
      id
      title
      description
      updatedAt
    }
  }
`;
```

### Usar GraphQL en Componentes

```vue
<script setup lang="ts">
  import { useQuery, useMutation } from "@vue/apollo-composable";
  import { GET_COURSES, CREATE_COURSE } from "@lq/graphql";

  // Query
  const { result, loading, error, refetch } = useQuery(GET_COURSES, {
    limit: 10,
    offset: 0,
  });

  const courses = computed(() => result.value?.courses ?? []);

  // Mutation
  const { mutate: createCourse, loading: creating } = useMutation(CREATE_COURSE);

  async function handleCreate() {
    await createCourse({
      input: {
        title: "Nuevo Curso",
        description: "Descripcion",
      },
    });

    // Refrescar la lista
    await refetch();
  }
</script>
```

### Generar Tipos TypeScript

```bash
# Generar tipos desde el schema GraphQL
pnpm graphql:codegen

# Modo watch (regenera al cambiar)
pnpm graphql:watch
```

#### Configuracion

**Archivo `.env` (root del monorepo)**:

```shell
# GraphQL Codegen - Endpoint para generar tipos
GRAPHQL_ENDPOINT=http://localhost:4000/graphql

# GraphQL Runtime - Endpoints para las apps
NUXT_PUBLIC_GRAPHQL_ENDPOINT=http://localhost:4000/graphql
NUXT_PUBLIC_GRAPHQL_WS_ENDPOINT=ws://localhost:4000/graphql
```

**Importante**:

- `GRAPHQL_ENDPOINT`: Usado por GraphQL Codegen en **build time** para introspección del schema
- `NUXT_PUBLIC_GRAPHQL_ENDPOINT`: Usado por las apps en **runtime** para queries/mutations
- Ambas variables deben apuntar al mismo backend pero sirven propósitos diferentes

**Archivo `codegen.yml`**:

```yaml
overwrite: true
schema:
  ${GRAPHQL_ENDPOINT}:
    headers:
      X-Requested-With: XMLHttpRequest
documents:
  - "packages/graphql/src/**/*.ts"
  - "apps/**/graphql/**/*.ts"
  - "apps/**/graphql/**/*.graphql"
generates:
  packages/graphql/src/generated/graphql.ts:
    plugins:
      - typescript
      - typescript-operations
      - typescript-vue-apollo
    config:
      withCompositionFunctions: false
      vueCompositionApiImportFrom: vue
      useTypeImports: true
      strictScalars: true
```

#### Troubleshooting

**Error: "Failed to load schema from undefined"**

- Verifica que `GRAPHQL_ENDPOINT` esté definido en `.env` del root
- Asegúrate de que el backend GraphQL esté corriendo
- Prueba acceder manualmente a la URL en el navegador

**Error: "Unable to find any GraphQL type definitions"**

- Verifica que existan archivos `.graphql` o queries/mutations en TypeScript
- Revisa que los paths en `documents` sean correctos

## Rutas y Navegacion

### Nuxt (Student-Teacher)

File-based routing automatico:

```
pages/
├── index.vue           → /
├── login.vue           → /login
├── dashboard.vue       → /dashboard
├── courses/
│   ├── index.vue       → /courses
│   ├── [id].vue        → /courses/:id
│   └── create.vue      → /courses/create
```

#### Parametros de Ruta

```vue
<!-- pages/courses/[id].vue -->
<script setup lang="ts">
  const route = useRoute();
  const courseId = computed(() => route.params.id as string);

  const { result } = useQuery(GET_COURSE, { id: courseId });
</script>
```

#### Navegacion Programatica

```typescript
const router = useRouter();

// Navegar
await router.push("/courses");

// Con parametros
await router.push({ path: `/courses/${id}` });

// Con query
await router.push({ path: "/courses", query: { page: 1 } });

// Reemplazar (no agrega al historial)
await router.replace("/login");

// Ir atras
router.back();
```

#### Middlewares

```typescript
// middleware/auth.global.ts
export default defineNuxtRouteMiddleware((to, from) => {
  const authStore = useAuthStore();

  // Rutas publicas
  const publicRoutes = ["/login", "/register"];

  if (!authStore.isAuthenticated && !publicRoutes.includes(to.path)) {
    return navigateTo("/login");
  }

  // Check roles
  if (to.meta.requiresRole && !authStore.hasRole(to.meta.requiresRole)) {
    return navigateTo("/unauthorized");
  }
});
```

### Vue Router (Institutional)

```typescript
// apps/institutional/src/router/index.ts
import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/",
    name: "Home",
    component: () => import("../views/Home.vue"),
  },
  {
    path: "/dashboard",
    name: "Dashboard",
    component: () => import("../views/Dashboard.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/courses/:id",
    name: "CourseDetail",
    component: () => import("../views/CourseDetail.vue"),
    props: true,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Global guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next("/login");
  } else {
    next();
  }
});

export default router;
```

## Internacionalizacion (i18n)

### Estructura de Traducciones

```
i18n/locales/
├── en/
│   ├── index.ts
│   ├── common.ts
│   ├── auth.ts
│   └── courses.ts
└── es/
    ├── index.ts
    ├── common.ts
    ├── auth.ts
    └── courses.ts
```

### Definir Traducciones

```typescript
// i18n/locales/es/auth.ts
export default {
  title: "Autenticacion",
  login: {
    title: "Iniciar Sesion",
    email: "Correo electronico",
    password: "Contraseña",
    submit: "Entrar",
    error: "Credenciales invalidas",
  },
  register: {
    title: "Registrarse",
    // ...
  },
};
```

```typescript
// i18n/locales/es/index.ts
import common from "./common";
import auth from "./auth";
import courses from "./courses";

export default {
  common,
  auth,
  courses,
};
```

### Usar Traducciones

```vue
<template>
  <div>
    <h1>{{ $t("auth.login.title") }}</h1>
    <input :placeholder="$t('auth.login.email')" />
    <button>{{ $t("auth.login.submit") }}</button>

    <!-- Con interpolacion -->
    <p>{{ $t("common.welcome", { name: user.name }) }}</p>

    <!-- Pluralizacion -->
    <p>{{ $t("courses.count", courseCount) }}</p>
  </div>
</template>

<script setup lang="ts">
  const { t, locale } = useI18n();

  // En JavaScript
  const message = t("auth.login.title");

  // Cambiar idioma
  locale.value = "es";
</script>
```

### Validar Traducciones

```bash
# Validar que todas las claves esten en todos los idiomas
pnpm i18n:validate

# Extraer claves usadas en el codigo
pnpm i18n:extract
```

## Estilado

### TailwindCSS

```vue
<template>
  <div class="container mx-auto px-4">
    <h1 class="text-3xl font-bold text-primary-600">Titulo</h1>

    <button class="btn btn-primary hover:bg-primary-700 transition">Click</button>
  </div>
</template>
```

### Configuracion de Tailwind

```typescript
// tailwind.config.ts
export default {
  content: ["./components/**/*.{vue,js,ts}", "./layouts/**/*.vue", "./pages/**/*.vue"],
  theme: {
    extend: {
      colors: {
        primary: {
          500: "#0ea5e9",
          600: "#0284c7",
          // ...
        },
      },
    },
  },
};
```

### PrimeVue

```vue
<template>
  <div>
    <Button label="Click me" severity="primary" />
    <DataTable :value="data" />
    <Dialog v-model:visible="showDialog">
      <template #header>Titulo</template>
      Contenido
    </Dialog>
  </div>
</template>

<script setup lang="ts">
  import { Button, DataTable, Dialog } from "primevue";
</script>
```

### CSS Modules (Opcional)

```vue
<template>
  <div :class="$style.container">
    <h1 :class="$style.title">Titulo</h1>
  </div>
</template>

<style module>
  .container {
    padding: 1rem;
  }

  .title {
    font-size: 2rem;
    color: var(--primary-color);
  }
</style>
```

## Testing

### Unit Tests (Vitest)

```typescript
// tests/unit/utils/formatters.test.ts
import { describe, it, expect } from "vitest";
import { formatCurrency } from "@lq/utils";

describe("formatCurrency", () => {
  it("formats USD correctly", () => {
    expect(formatCurrency(1000, "USD")).toBe("$1,000.00");
  });

  it("formats EUR correctly", () => {
    expect(formatCurrency(1000, "EUR")).toBe("\u20ac1,000.00");
  });
});
```

### Component Tests

```typescript
// tests/unit/components/Button.test.ts
import { describe, it, expect, vi } from "vitest";
import { mount } from "@vue/test-utils";
import { Button } from "@lq/ui";

describe("Button", () => {
  it("renders slot content", () => {
    const wrapper = mount(Button, {
      slots: {
        default: "Click me",
      },
    });

    expect(wrapper.text()).toBe("Click me");
  });

  it("emits click event", async () => {
    const wrapper = mount(Button);
    await wrapper.trigger("click");

    expect(wrapper.emitted("click")).toBeTruthy();
  });

  it("disables when loading", () => {
    const wrapper = mount(Button, {
      props: { loading: true },
    });

    expect(wrapper.find("button").attributes("disabled")).toBeDefined();
  });
});
```

### E2E Tests (Playwright)

```typescript
// tests/e2e/auth.spec.ts
import { test, expect } from "@playwright/test";

test.describe("Authentication", () => {
  test("user can login", async ({ page }) => {
    await page.goto("/login");

    await page.fill('[name="email"]', "test@example.com");
    await page.fill('[name="password"]', "password123");
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL("/dashboard");
    await expect(page.locator("h1")).toContainText("Dashboard");
  });

  test("shows error on invalid credentials", async ({ page }) => {
    await page.goto("/login");

    await page.fill('[name="email"]', "invalid@example.com");
    await page.fill('[name="password"]', "wrong");
    await page.click('button[type="submit"]');

    await expect(page.locator(".error")).toBeVisible();
  });
});
```

### Ejecutar Tests

```bash
# Unit tests
pnpm test:unit

# Watch mode
pnpm test:unit --watch

# E2E tests
pnpm test:e2e

# E2E con UI
pnpm test:e2e --ui

# Coverage
pnpm test:unit --coverage
```

## Debugging

### Vue DevTools

1. Instala Vue DevTools en tu navegador
2. Abre DevTools (F12)
3. Ve a la pestaña "Vue"

### Nuxt DevTools

```bash
# Ya viene habilitado en nuxt.config.ts
# Presiona Shift + Alt + D en el navegador
```

### VSCode Debugger

`.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "chrome",
      "request": "launch",
      "name": "Client: Chrome",
      "url": "http://localhost:3000",
      "webRoot": "${workspaceFolder}/apps/student-teacher"
    }
  ]
}
```

### Console Debugging

```typescript
// Breakpoint con debugger
function myFunction() {
  debugger; // Pausa ejecucion aqui
  console.log("Debug info");
}

// Console groups
console.group("User Info");
console.log("Name:", user.name);
console.log("Email:", user.email);
console.groupEnd();

// Performance timing
console.time("fetch");
await fetchData();
console.timeEnd("fetch"); // fetch: 234ms
```

## Mejores Practicas

### 1. Componentes

- Manten componentes pequeños (< 200 lineas)
- Una responsabilidad por componente
- Usa props para entrada, eventos para salida
- Define tipos para todas las props

### 2. Estado

- Usa stores para estado compartido
- Manten estado local en componentes cuando sea posible
- No mutes el estado directamente, usa acciones

### 3. Performance

- Lazy load rutas y componentes pesados
- Usa `v-show` para toggles frecuentes
- Usa `v-if` para renderizado condicional
- Virtualiza listas largas

### 4. TypeScript

- Define tipos para todo
- Evita `any`, usa `unknown` si es necesario
- Usa interfaces para objetos
- Aprovecha la inferencia de tipos

### 5. GraphQL

- Reutiliza fragments
- Pide solo los campos que necesitas
- Usa variables en vez de strings dinamicos
- Cachea resultados apropiadamente

### 6. Testing

- Testea comportamiento, no implementacion
- Un assert por test (cuando sea posible)
- Nombres descriptivos para tests
- Arrange-Act-Assert pattern

### 7. Git

- Commits pequeños y frecuentes
- Mensajes descriptivos (conventional commits)
- Crea branches para features
- Rebase antes de merge

### 8. Documentacion

- Comenta codigo complejo
- Documenta funciones publicas
- Manten README actualizado
- Agrega ejemplos de uso

## Recursos Adicionales

- [Vue 3 Docs](https://vuejs.org/)
- [Nuxt 4 Docs](https://nuxt.com/)
- [Pinia Docs](https://pinia.vuejs.org/)
- [Apollo Client Docs](https://www.apollographql.com/docs/react/)
- [TailwindCSS Docs](https://tailwindcss.com/)
- [Vitest Docs](https://vitest.dev/)
- [Playwright Docs](https://playwright.dev/)
- [Guia de Turbo](./TURBO.md)
- [Arquitectura](./ARCHITECTURE.md)
