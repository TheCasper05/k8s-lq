# LqDataTable

Componente de tabla de datos reutilizable para Nuxt 4.

## Características

- ✅ **Nuxt 4 Ready**: Diseñado específicamente para Nuxt 4
- ✅ **TypeScript Genérico**: Tipado completo con generics
- ✅ **Slots Flexibles**: Header, footer, actions y celdas personalizables
- ✅ **Loading State**: Estado de carga con icono animado
- ✅ **Sortable**: Columnas ordenables opcionales
- ✅ **PassThrough**: Personalización completa con PrimeVue PT
- ✅ **Dark Mode**: Soporte completo para modo oscuro

## Uso Directo

El componente se importa directamente desde `@lq/ui` sin necesidad de wrappers:

```vue
<script setup lang="ts">
  import { LqDataTable, type LqDataTableColumn } from "@lq/ui";

  const columns: LqDataTableColumn[] = [
    { field: "name", header: "Name", sortable: true },
    { field: "email", header: "Email" },
  ];
</script>

<template>
  <LqDataTable :data="users" :columns="columns" />
</template>
```

## Uso en Apps

### Ejemplo Básico

```vue
<script setup lang="ts">
  import type { LqDataTableColumn } from "@lq/ui";

  interface User {
    id: number;
    name: string;
    email: string;
    role: string;
  }

  const users = ref<User[]>([
    { id: 1, name: "John Doe", email: "john@example.com", role: "Admin" },
    { id: 2, name: "Jane Smith", email: "jane@example.com", role: "User" },
  ]);

  const columns: LqDataTableColumn[] = [
    { field: "name", header: "Name", sortable: true },
    { field: "email", header: "Email", sortable: true },
    { field: "role", header: "Role" },
  ];
</script>

<template>
  <LqDataTable :data="users" :columns="columns" />
</template>
```

### Con Header y Actions

```vue
<script setup lang="ts">
  import { LqDataTable, LqButton, type LqDataTableColumn } from "@lq/ui";
</script>

<template>
  <LqDataTable :data="users" :columns="columns">
    <!-- Header slot -->
    <template #header>
      <div class="flex items-center justify-between">
        <h2 class="text-xl font-semibold">Users</h2>
        <LqButton label="Add User" icon="solar:add-circle-linear" />
      </div>
    </template>

    <!-- Actions slot -->
    <template #actions="{ data }">
      <div class="flex gap-2 justify-end">
        <LqButton icon="solar:pen-linear" severity="secondary" text @click="editUser(data.id)" />
        <LqButton icon="solar:trash-bin-trash-linear" severity="danger" text @click="deleteUser(data.id)" />
      </div>
    </template>
  </LqDataTable>
</template>
```

### Celdas Personalizadas

```vue
<script setup lang="ts">
  import { LqDataTable, LqBadge, type LqDataTableColumn } from "@lq/ui";
</script>

<template>
  <LqDataTable :data="users" :columns="columns">
    <!-- Custom cell for role with badge -->
    <template #cell-role="{ value }">
      <LqBadge :label="value" :severity="value === 'Admin' ? 'success' : 'info'" />
    </template>

    <!-- Custom cell for email with icon -->
    <template #cell-email="{ value }">
      <div class="flex items-center gap-2">
        <Icon name="solar:letter-linear" class="text-surface-400" />
        <span>{{ value }}</span>
      </div>
    </template>
  </LqDataTable>
</template>
```

### Loading State

```vue
<script setup lang="ts">
  import { LqDataTable, type LqDataTableColumn } from "@lq/ui";

  const loading = ref(true);
  const users = ref<User[]>([]);

  onMounted(async () => {
    loading.value = true;
    users.value = await fetchUsers();
    loading.value = false;
  });
</script>

<template>
  <LqDataTable :data="users" :columns="columns" :loading="loading" empty-message="No users found" />
</template>
```

### PassThrough Personalizado

```vue
<script setup lang="ts">
  import { LqDataTable, type LqDataTableColumn } from "@lq/ui";

  const customPT = {
    root: { class: "border-2 border-primary-500" },
    thead: { class: "bg-primary-50" },
    bodyRow: { class: "hover:bg-primary-50" },
  };
</script>

<template>
  <LqDataTable :data="users" :columns="columns" :pt="customPT" />
</template>
```

## Props

| Prop           | Type                  | Default               | Descripción                 |
| -------------- | --------------------- | --------------------- | --------------------------- |
| `data`         | `T[]`                 | **required**          | Array de datos a mostrar    |
| `columns`      | `LqDataTableColumn[]` | **required**          | Definición de columnas      |
| `scrollable`   | `boolean`             | `true`                | Habilitar modo scrollable   |
| `loading`      | `boolean`             | `false`               | Estado de carga             |
| `emptyMessage` | `string`              | `"No data available"` | Mensaje cuando no hay datos |
| `pt`           | `Record<string, any>` | `undefined`           | Configuración PassThrough   |

## Column Interface

```typescript
interface LqDataTableColumn {
  field: string; // Campo del objeto de datos
  header: string; // Texto del encabezado
  class?: string; // Clases CSS adicionales
  sortable?: boolean; // Habilitar ordenamiento
}
```

## Slots

| Slot           | Props             | Descripción                                     |
| -------------- | ----------------- | ----------------------------------------------- |
| `header`       | -                 | Contenido del header de la tabla                |
| `footer`       | -                 | Contenido del footer de la tabla                |
| `actions`      | `{ data }`        | Columna de acciones (se agrega automáticamente) |
| `cell-{field}` | `{ data, value }` | Personalizar celda específica                   |

## Ventajas

- ✅ **Reutilizable**: Un solo componente para todo el proyecto
- ✅ **Mantenible**: Cambios en un solo lugar
- ✅ **Type-Safe**: TypeScript genérico completo
- ✅ **Flexible**: Slots para personalización total
- ✅ **Consistente**: Mismo look & feel en toda la app
- ✅ **Directo**: Sin capas intermedias, importación directa desde `@lq/ui`

## Archivos

- **Componente**: `packages/ui/src/organisms/LqDataTable.vue`
- **Types**: Exportados desde `@lq/ui`
