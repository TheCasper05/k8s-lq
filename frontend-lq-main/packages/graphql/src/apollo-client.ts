import { ApolloClient, InMemoryCache, HttpLink, from, split } from '@apollo/client/core'
import { onError } from '@apollo/client/link/error'
import { setContext } from '@apollo/client/link/context'
import { GraphQLWsLink } from '@apollo/client/link/subscriptions'
import { getMainDefinition } from '@apollo/client/utilities'
import { createClient } from 'graphql-ws'
import { cacheConfig } from './cache-policies'
import type { ApolloClientConfig } from './types'

/**
 * Get cookie value by name
 */
function getCookie(name: string): string | null {
  if (typeof document === 'undefined') return null

  let cookieValue: string | null = null
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === name + '=') {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

/**
 * Get CSRF token from cookies
 */
function getCSRFToken(): string | null {
  return getCookie('csrftoken')
}

/**
 * Creates a configured Apollo Client instance with:
 * - HTTP and WebSocket links
 * - Authentication
 * - CSRF protection
 * - Error handling
 * - Advanced caching
 * - Automatic reconnection
 */
export function createApolloClient(config: ApolloClientConfig) {
  // HTTP link for queries and mutations
  const httpLink = new HttpLink({
    uri: config.httpEndpoint,
    credentials: 'include', // Send cookies
  })

  // Auth link - adds authorization header and CSRF token
  const authLink = setContext(async (_, { headers }) => {
    const token = config.getAuth?.() || ''
    const csrfToken = getCSRFToken()

    // Debug logging
    if (import.meta.env.DEV || process.env.NODE_ENV === 'development') {
      console.log('[Apollo] Auth headers:', {
        hasToken: !!token,
        hasCsrfToken: !!csrfToken,
        csrfToken: csrfToken ? csrfToken.substring(0, 10) + '...' : 'none',
      })
    }

    return {
      headers: {
        ...headers,
        ...(token && { authorization: token }),
        ...(csrfToken && { 'X-CSRFToken': csrfToken }),
      },
    }
  })

  // WebSocket link for subscriptions (only on client-side)
  // Check if we're in a browser environment
  const isClient = typeof window !== 'undefined'

  let wsLink: GraphQLWsLink | null = null

  if (isClient && config.wsEndpoint) {
    const wsClient = createClient({
      url: config.wsEndpoint,
      connectionParams: () => {
        const token = config.getAuth?.() || ''
        return {
          ...(token && { authorization: token }),
        }
      },
      shouldRetry: () => true,
      retryAttempts: Infinity,
      retryWait: async (retries) => {
        const delay = Math.min(1000 * Math.pow(2, retries), 30000)
        await new Promise((resolve) => setTimeout(resolve, delay))
      },
      keepAlive: 10000,
      on: {
        connected: () => {
          // Connection established
        },
        closed: () => {
          // Connection closed
        },
        error: (error) => console.error('[GraphQL WS] Error', error),
      },
    })

    wsLink = new GraphQLWsLink(wsClient)
  }

  // Error link - handles network and GraphQL errors
  const errorLink = onError(({ graphQLErrors, networkError, operation, forward }) => {
    if (graphQLErrors) {
      graphQLErrors.forEach(({ message, locations, path, extensions }) => {
        console.error(
          `[GraphQL error]: Message: ${message}, Location: ${locations}, Path: ${path}`,
          extensions
        )

        // Handle authentication errors
        if (extensions?.code === 'UNAUTHENTICATED') {
          console.warn('Unauthenticated error - token may be expired')
        }
      })
    }

    if (networkError) {
      console.error(`[Network error]: ${networkError}`)

      // Call custom error handler
      if (config.onError) {
        config.onError({
          graphQLErrors: graphQLErrors || [],
          networkError,
          message: networkError.message,
          name: 'ApolloError',
          extraInfo: undefined,
          clientErrors: [],
          protocolErrors: [],
          cause: networkError,
        })
      }
    }

    return forward(operation)
  })

  // Split link - routes operations to HTTP or WS based on type
  // Only use split if we have a WebSocket link (client-side)
  const httpChain = from([errorLink, authLink, httpLink])

  const splitLink = wsLink
    ? split(
        ({ query }) => {
          const definition = getMainDefinition(query)
          return (
            definition.kind === 'OperationDefinition' && definition.operation === 'subscription'
          )
        },
        wsLink,
        httpChain
      )
    : httpChain

  // Create Apollo Client
  const apolloClient = new ApolloClient({
    link: splitLink,
    cache: new InMemoryCache(cacheConfig),
    defaultOptions: {
      watchQuery: {
        fetchPolicy: 'cache-and-network',
        errorPolicy: 'all',
      },
      query: {
        fetchPolicy: 'network-only',
        errorPolicy: 'all',
      },
      mutate: {
        errorPolicy: 'all',
      },
    },
    connectToDevTools: import.meta.env.DEV || process.env.NODE_ENV === 'development',
  })

  return apolloClient
}
