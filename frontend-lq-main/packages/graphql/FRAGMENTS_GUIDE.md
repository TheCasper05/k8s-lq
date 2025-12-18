# 📚 Guía de Fragments en GraphQL

## ¿Qué son los Fragments?

Los **fragments** son bloques reutilizables de campos de GraphQL. Te permiten definir un conjunto de campos una vez y reutilizarlos en múltiples queries y mutations.

## 🎯 Ejemplo Práctico

### 1. Definición del Fragment

```graphql
fragment UserProfileCoreFields on UserProfileType {
  id
  publicId
  primaryRole
  firstName
  lastName
  phone
  photo
  # ... más campos
}
```

### 2. Uso en una Mutation

**SIN fragment** (forma antigua):
```graphql
mutation CreateUserProfiles($input: CreateUserProfileInput!) {
  createUserProfiles(input: $input) {
    objects {
      id
      publicId
      primaryRole
      firstName
      lastName
      phone
      photo
      birthday
      country
      # ... repites todos los campos
    }
  }
}
```

**CON fragment** (forma nueva y mejor):
```graphql
mutation CreateUserProfiles($input: CreateUserProfileInput!) {
  createUserProfiles(input: $input) {
    objects {
      ...UserProfileCoreFields
    }
  }
}
```

### 3. Uso en el Código TypeScript

```typescript
import { gql } from '@apollo/client/core'
import { USER_PROFILE_CORE_FIELDS } from '../fragments'

// Incluir el fragment con interpolación ${...}
export const CREATE_USER_PROFILES_ADMIN = gql`
  ${USER_PROFILE_CORE_FIELDS}

  mutation CreateUserProfilesAdmin($input: CreateUserProfileInput!) {
    createUserProfiles(input: $input) {
      objects {
        ...UserProfileCoreFields
      }
    }
  }
`
```

## 🔄 Uso en Vue/Nuxt

```vue
<script setup lang="ts">
import { useMutation } from '@vue/apollo-composable'
import { CREATE_USER_PROFILES_ADMIN } from '@lq/graphql'

const { mutate: createProfile, loading, error } = useMutation(CREATE_USER_PROFILES_ADMIN)

const handleCreateProfile = async () => {
  try {
    const result = await createProfile({
      input: {
        primaryRole: 'ADMIN_INSTITUCIONAL',
        firstName: 'Juan',
        lastName: 'Pérez',
        timezone: 'America/Mexico_City',
        languagePreference: 'es',
        country: 'MX',
        phone: '+52 55 1234 5678'
      }
    })

    console.log('Profile created:', result?.data?.createUserProfiles?.objects)
  } catch (err) {
    console.error('Error creating profile:', err)
  }
}
</script>
```

## ✨ Beneficios

1. **DRY (Don't Repeat Yourself)**: Define los campos una vez
2. **Mantenibilidad**: Cambias en un solo lugar
3. **Consistencia**: Todos usan los mismos campos
4. **Type Safety**: TypeScript infiere los tipos correctamente

## 📦 Fragments Disponibles

### UserProfile

- `USER_PROFILE_CORE_FIELDS` - Todos los campos (completo)
- `USER_PROFILE_BASIC_FIELDS` - Solo campos esenciales (ligero)

### ¿Cuándo usar cada uno?

- **CORE_FIELDS**: Para crear/editar perfiles, vistas de detalle
- **BASIC_FIELDS**: Para listados, búsquedas, vistas rápidas

## 🚀 Mejores Prácticas

1. **Nombra descriptivamente**: `UserProfileCoreFields`, no `UserFields1`
2. **Agrupa lógicamente**: Crea fragments por dominio (User, Institution, etc.)
3. **Mantén versiones**: CORE (completo), BASIC (mínimo), EXTENDED (con relaciones)
4. **Documenta**: Explica cuándo usar cada fragment

## 🎓 Conceptos Avanzados

### Fragments anidados

```graphql
fragment WorkspaceWithOwner on WorkspaceNode {
  id
  name
  slug
  owner {
    ...UserProfileBasicFields
  }
}
```

### Múltiples fragments

```graphql
query GetUserData {
  readUser(me: true) {
    ...UserBasicFields
    profile {
      ...UserProfileCoreFields
    }
    workspaces {
      ...WorkspaceBasicFields
    }
  }
}
```

### Type Conditions (Inline Fragments)

```graphql
query GetMembers {
  searchMembers {
    results {
      ... on StudentNode {
        studentId
        grade
      }
      ... on TeacherNode {
        teacherId
        subject
      }
    }
  }
}
```
