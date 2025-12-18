# @lq/graphql

Centralized GraphQL package with Apollo Client configuration for LingoQuesto.

## Features

- Apollo Client with HTTP and WebSocket support
- Automatic reconnection with exponential backoff
- Heartbeat/keepalive for stable connections
- Advanced caching with type policies
- Authentication integration
- Centralized error handling
- TypeScript types auto-generation

## Usage

### In Nuxt app (plugin):

```typescript
import { createApolloClient } from '@lq/graphql'

const apolloClient = createApolloClient({
  httpEndpoint: 'http://localhost:4000/graphql',
  wsEndpoint: 'ws://localhost:4000/graphql',
  getAuth: () => {
    const token = authStore.token
    return token ? `Bearer ${token}` : ''
  },
  onError: (error) => {
    // Handle errors
  },
})
```

### In Vue 3 app:

```typescript
import { DefaultApolloClient } from '@vue/apollo-composable'
import { createApolloClient } from '@lq/graphql'

app.provide(DefaultApolloClient, apolloClient)
```

### Using queries:

```typescript
import { useQuery } from '@lq/graphql'
import { GET_USERS } from '@lq/graphql/queries'

const { result, loading, error } = useQuery(GET_USERS, { page: 1, limit: 10 })
```

### Using mutations:

```typescript
import { useMutation } from '@lq/graphql'
import { CREATE_USER } from '@lq/graphql/mutations'

const { mutate, loading, error } = useMutation(CREATE_USER)

await mutate({ input: { email: 'test@example.com' } })
```

### Using subscriptions:

```typescript
import { useSubscription } from '@lq/graphql'
import { MESSAGE_RECEIVED } from '@lq/graphql/subscriptions'

const { result, loading } = useSubscription(MESSAGE_RECEIVED, { courseId: '123' })
```

## Available Operations

### Queries

#### User Queries
- `GET_CURRENT_USER` - Get basic user info
- `GET_CURRENT_USER_WITH_PROFILE` - Get user with full profile
- `GET_USER_PERSONAL_WORKSPACE` - Get user's personal workspace
- `GET_USER_WORKSPACE_MEMBERSHIPS` - Get all user's workspace memberships

#### Institution Queries
- `READ_INSTITUTION` - Get single institution details

### Mutations

#### Onboarding Mutations
- `COMPLETE_ONBOARDING` - Complete user onboarding (creates profile + workspace)

### Example: Complete Onboarding

```typescript
import { useMutation, COMPLETE_ONBOARDING } from '@lq/graphql'
import type { CompleteOnboardingInput } from '@lq/graphql'

const { mutate, loading, error } = useMutation(COMPLETE_ONBOARDING)

const input: CompleteOnboardingInput = {
  firstName: 'John',
  lastName: 'Doe',
  primaryRole: 'student',
  languagePreference: 'en',
  timezone: 'America/New_York',
  country: 'US',
}

const result = await mutate({ input })
```

## Code Generation

Run code generation to create TypeScript types:

```bash
pnpm graphql:codegen
```

This will generate types in `src/generated/graphql.ts`.
