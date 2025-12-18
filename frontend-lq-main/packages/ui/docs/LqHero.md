# LqHero

Componente Hero flexible que soporta múltiples variantes para diferentes casos de uso, desde banners simples hasta
headers complejos con imágenes y metadata.

## Características

- **3 Variantes**: `banner`, `card`, `detailed`
- **Usa LqBanner internamente** cuando `variant="banner"`
- **Layouts flexibles**: horizontal, vertical, three-column
- **Soporte para imágenes** con overlay y play button
- **Navegación integrada** con back button
- **Slots extensibles** para máxima personalización
- **PrimeVue 4 + Tailwind CSS**

## Variantes

### 1. Banner (Simple)

Usa `LqBanner` internamente. Ideal para headers de página simples.

```vue
<LqHero
  variant="banner"
  title="My Classes"
  description="Manage and organize your classes"
  icon="solar:book-line-duotone"
>
  <template #action>
    <Button label="Create Class" />
  </template>
</LqHero>
```

### 2. Card (Activities Detail)

Layout horizontal con imagen thumbnail, metadata y acciones múltiples.

```vue
<LqHero
  variant="card"
  :image="activity.coverImage"
  :title="activity.title"
  :show-play-button="true"
  :show-back-button="true"
  @back="router.back()"
  @image-click="openTest"
>
  <template #metadata>
    <CEFRBadge :level="activity.level" />
    <span class="text-primary-400 text-3xl">•</span>
    <span class="text-sm text-surface-600">{{ activity.theme }}</span>
  </template>

  <template #header-action>
    <Button label="Share" severity="secondary" outlined />
  </template>

  <template #actions>
    <Button label="Test" severity="info" />
    <Button label="Assign" severity="success" />
    <Button label="Delete" severity="danger" />
  </template>
</LqHero>
```

### 3. Detailed (Class Detail)

Layout de 3 columnas con imagen, información y panel lateral.

```vue
<LqHero
  variant="detailed"
  :image="classDetail.coverImage"
  :title="classDetail.name"
  :show-back-button="true"
  @back="router.back()"
>
  <template #image-overlay>
    <AvatarGroup class="absolute left-1/2 -translate-x-1/2 bottom-0 translate-y-1/2">
      <Avatar v-for="student in students" :key="student.id" />
    </AvatarGroup>
  </template>

  <template #navigation>
    <Button icon="pi pi-arrow-left" @click="router.back()" />
    <Button icon="pi pi-pencil" @click="editClass" />
  </template>

  <template #metadata>
    <div class="flex items-center gap-3">
      <img :src="flagUrl" class="w-5 h-4" />
      <span>{{ classDetail.language }}</span>
    </div>
    <span class="badge">{{ classDetail.level }}</span>
  </template>

  <template #info>
    <div class="flex items-center gap-2">
      <Icon name="solar:users-group-rounded-line-duotone" />
      <span>{{ students.length }} students</span>
    </div>
  </template>

  <template #sidebar>
    <TeachersPanel :teachers="teachers" />
    <InviteLinksPanel />
  </template>
</LqHero>
```

## Props

### Variant & Layout

| Prop      | Type                                           | Default        | Description          |
| --------- | ---------------------------------------------- | -------------- | -------------------- |
| `variant` | `'banner' \| 'card' \| 'detailed'`             | `'banner'`     | Variante del Hero    |
| `layout`  | `'horizontal' \| 'vertical' \| 'three-column'` | `'horizontal'` | Layout del contenido |

### Image

| Prop             | Type                            | Default     | Description                           |
| ---------------- | ------------------------------- | ----------- | ------------------------------------- |
| `image`          | `string`                        | `undefined` | URL de la imagen                      |
| `imageAspect`    | `'square' \| 'video' \| 'wide'` | `'video'`   | Aspect ratio de la imagen             |
| `showPlayButton` | `boolean`                       | `false`     | Mostrar botón de play sobre la imagen |

### Content

| Prop          | Type     | Default     | Description                              |
| ------------- | -------- | ----------- | ---------------------------------------- |
| `title`       | `string` | `undefined` | Título principal                         |
| `subtitle`    | `string` | `undefined` | Subtítulo                                |
| `description` | `string` | `undefined` | Descripción (solo para variant="banner") |

### Navigation

| Prop             | Type      | Default     | Description                  |
| ---------------- | --------- | ----------- | ---------------------------- |
| `showBackButton` | `boolean` | `false`     | Mostrar botón de volver      |
| `backRoute`      | `string`  | `undefined` | Ruta para el botón de volver |

### LqBanner Props (cuando variant="banner")

| Prop                 | Type                                       | Default     | Description                             |
| -------------------- | ------------------------------------------ | ----------- | --------------------------------------- |
| `icon`               | `string`                                   | `undefined` | Icono del banner                        |
| `rounded`            | `'lg' \| 'xl' \| '2xl' \| '3xl' \| 'full'` | `'3xl'`     | Redondeo de esquinas                    |
| `showIconBackground` | `boolean`                                  | `true`      | Mostrar fondo del icono                 |
| `size`               | `'sm' \| 'md' \| 'lg'`                     | `'md'`      | Tamaño del banner                       |
| `iconContainerClass` | `string`                                   | `undefined` | Clases CSS para el contenedor del icono |

## Events

| Event         | Payload | Description                                        |
| ------------- | ------- | -------------------------------------------------- |
| `back`        | `void`  | Emitido cuando se hace click en el botón de volver |
| `image-click` | `void`  | Emitido cuando se hace click en la imagen          |

## Slots

### Variant: Banner

| Slot      | Description                                |
| --------- | ------------------------------------------ |
| `icon`    | Icono personalizado                        |
| `default` | Contenido principal (título + descripción) |
| `action`  | Botón de acción                            |

### Variant: Card

| Slot            | Description                           |
| --------------- | ------------------------------------- |
| `image`         | Imagen personalizada                  |
| `play-icon`     | Icono de play personalizado           |
| `image-overlay` | Overlay sobre la imagen               |
| `title`         | Título personalizado                  |
| `metadata`      | Badges y metadata                     |
| `header-action` | Acción en el header (ej: botón Share) |
| `actions`       | Botones de acción principales         |

### Variant: Detailed

| Slot            | Description                                      |
| --------------- | ------------------------------------------------ |
| `image`         | Imagen personalizada                             |
| `image-overlay` | Overlay sobre la imagen (ej: avatares flotantes) |
| `navigation`    | Botones de navegación personalizados             |
| `title`         | Título personalizado                             |
| `metadata`      | Metadata (language, level, etc.)                 |
| `info`          | Información adicional                            |
| `sidebar`       | Panel lateral (teachers, invite links, etc.)     |

## Ejemplos Completos

### Ejemplo 1: Classes Header (Banner)

```vue
<script setup>
  import { LqHero } from "@lq/ui";
  import Button from "primevue/button";

  const emit = defineEmits(["create-class"]);
</script>

<template>
  <LqHero
    variant="banner"
    size="lg"
    title="My Classes"
    description="Manage and organize your language classes"
    icon-container-class="size-16 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center"
  >
    <template #icon>
      <Icon name="solar:book-line-duotone" class="text-white text-3xl" />
    </template>

    <template #action>
      <Button
        label="Create New Class"
        class="bg-white text-primary-600 border-0 font-bold"
        @click="emit('create-class')"
      >
        <template #icon>
          <Icon name="lucide:plus" class="text-xl" />
        </template>
      </Button>
    </template>
  </LqHero>
</template>
```

### Ejemplo 2: Activity Detail (Card)

```vue
<script setup>
  import { LqHero } from '@lq/ui'
  import Button from 'primevue/button'
  import CEFRBadge from '~/components/activities/badges/CEFRBadge.vue'

  const props = defineProps<{
    activity: Activity
  }>()

  const router = useRouter()

  const openTest = () => {
    // Logic to open test
  }

  const openShare = () => {
    // Logic to open share modal
  }
</script>

<template>
  <LqHero
    variant="card"
    :image="activity.coverImage"
    :title="activity.title"
    :show-play-button="true"
    :show-back-button="true"
    @back="router.push('/teacher/activities')"
    @image-click="openTest"
  >
    <template #metadata>
      <CEFRBadge no-color size="md" :level="activity.level" />
      <span class="text-primary-400 dark:text-primary-600 text-3xl">•</span>
      <span class="text-sm text-surface-600 dark:text-surface-400">
        {{ activity.theme }}
      </span>
    </template>

    <template #header-action>
      <Button label="Share" severity="secondary" outlined size="small" @click="openShare">
        <template #icon>
          <Icon name="solar:share-line-duotone" class="text-lg" />
        </template>
      </Button>
    </template>

    <template #actions>
      <Button label="Test" severity="info" size="small">
        <template #icon>
          <Icon name="solar:play-line-duotone" />
        </template>
      </Button>
      <Button label="Assign" severity="success" size="small">
        <template #icon>
          <Icon name="solar:user-plus-broken" />
        </template>
      </Button>
      <Button label="Delete" severity="danger" size="small">
        <template #icon>
          <Icon name="solar:trash-bin-trash-line-duotone" />
        </template>
      </Button>
    </template>
  </LqHero>
</template>
```

### Ejemplo 3: Class Detail (Detailed)

```vue
<script setup>
  import { LqHero } from '@lq/ui'
  import Avatar from 'primevue/avatar'
  import AvatarGroup from 'primevue/avatargroup'
  import Button from 'primevue/button'

  const props = defineProps<{
    classDetail: Class
    students: Student[]
    teachers: Teacher[]
  }>()

  const router = useRouter()

  const displayedStudents = computed(() => props.students.slice(0, 3))
  const remainingCount = computed(() => Math.max(0, props.students.length - 3))
</script>

<template>
  <LqHero
    variant="detailed"
    :image="classDetail.coverImage"
    :title="classDetail.name"
    :show-back-button="true"
    @back="router.back()"
  >
    <template #image-overlay>
      <div v-if="students.length > 0" class="absolute left-1/2 -translate-x-1/2 bottom-0 translate-y-1/2 z-10">
        <AvatarGroup>
          <Avatar
            v-for="student in displayedStudents"
            :key="student.id"
            :image="student.photo"
            shape="circle"
            class="border-2 border-white dark:border-surface-800 shadow-md"
          />
          <Avatar
            v-if="remainingCount > 0"
            :label="`+${remainingCount}`"
            shape="circle"
            class="bg-primary-600 text-white border-2 border-white"
          />
        </AvatarGroup>
      </div>
    </template>

    <template #navigation>
      <Button icon="pi pi-arrow-left" class="bg-surface-200 dark:bg-surface-900" @click="router.back()" />
      <Button icon="pi pi-pencil" class="bg-primary-600 text-white" @click="$emit('edit-class')" />
    </template>

    <template #metadata>
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2">
          <img
            :src="`https://flagcdn.com/w20/${classDetail.languageCode.toLowerCase()}.png`"
            :alt="classDetail.language"
            class="w-5 h-4 object-cover rounded"
          />
          <span class="text-sm text-surface-700 dark:text-surface-300">
            {{ classDetail.language }}
          </span>
        </div>
        <span
          class="bg-info-100 dark:bg-info-900/30 text-info-700 dark:text-info-400 px-2 py-1 rounded-lg text-sm font-semibold"
        >
          {{ classDetail.level }}
        </span>
      </div>
    </template>

    <template #info>
      <div class="flex items-center gap-2">
        <Icon name="solar:users-group-rounded-line-duotone" class="text-primary-600 dark:text-primary-400 text-lg" />
        <span class="text-sm text-surface-600 dark:text-surface-400">{{ students.length }} students</span>
      </div>
    </template>

    <template #sidebar>
      <div class="rounded-lg flex flex-col gap-3 md:gap-4">
        <h3 class="text-sm font-semibold text-surface-900 dark:text-surface-100 text-right">Teachers:</h3>

        <!-- Teachers list -->
        <TeachersPanel :teachers="teachers" />

        <!-- Invite links -->
        <div class="flex flex-col gap-2">
          <Button
            label="Copy Student Invite Link"
            class="bg-surface-200 dark:bg-surface-700 text-surface-900 dark:text-surface-100"
            size="small"
          >
            <template #icon>
              <Icon name="solar:copy-line-duotone" />
            </template>
          </Button>
        </div>
      </div>
    </template>
  </LqHero>
</template>
```

## Notas de Diseño

- **Variant Banner**: Usa `LqBanner` internamente, por lo que hereda todos sus estilos y comportamientos
- **Variant Card**: Diseñado para headers de detalle con imagen thumbnail y acciones múltiples
- **Variant Detailed**: Layout de 3 columnas ideal para páginas de detalle complejas con sidebar
- **Responsive**: Todos los layouts se adaptan automáticamente a móvil
- **Dark Mode**: Soporte completo para modo oscuro con Tailwind CSS
- **PrimeVue Integration**: Usa componentes de PrimeVue 4 (Button, Avatar, etc.)

## Migración desde Headers Custom

### Antes (Activities Detail)

```vue
<div class="bg-surface-0 dark:bg-surface-900 rounded-xl border p-5">
  <div class="flex flex-col lg:flex-row gap-6">
    <!-- Custom HTML structure -->
  </div>
</div>
```

### Después

```vue
<LqHero variant="card" :image="..." :title="...">
  <!-- Slots for customization -->
</LqHero>
```

**Beneficios**:

- ✅ Menos código duplicado
- ✅ Estilos consistentes
- ✅ Mantenibilidad mejorada
- ✅ Reutilización entre páginas
