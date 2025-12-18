import type { InMemoryCacheConfig } from '@apollo/client/core'

/**
 * Apollo Client cache configuration
 * Defines type policies, field policies, and cache behaviors
 *
 * Key concepts:
 * - keyFields: How to uniquely identify cached objects
 * - merge: How to merge incoming data with existing cache
 * - read: How to read derived/computed fields from cache
 */
export const cacheConfig: InMemoryCacheConfig = {
  typePolicies: {
    Query: {
      fields: {
        // Example: Paginated list with merge strategy
        users: {
          keyArgs: ['filter', 'sort'], // Cache separately by filter/sort
          merge(existing = { nodes: [], pageInfo: {} }, incoming) {
            return {
              ...incoming,
              nodes: [...(existing.nodes || []), ...(incoming.nodes || [])],
            }
          },
        },

        currentUser: {
          merge: false,
        },
      },
    },

    User: {
      keyFields: ['id'],
      fields: {
        fullName: {
          read(_, { readField }) {
            const firstName = readField('firstName') as string
            const lastName = readField('lastName') as string
            return `${firstName} ${lastName}`
          },
        },
      },
    },

    Course: {
      keyFields: ['id'],
      fields: {
        students: {
          merge(existing = [], incoming) {
            return incoming
          },
        },
      },
    },

    Material: {
      keyFields: ['id'],
    },

    PageInfo: {
      keyFields: [],
    },
  },

  possibleTypes: {
  },
}

/**
 * Cache eviction helpers
 * Use these to manually remove items from cache
 */
export const cacheHelpers = {
  /**
   * Evict a specific object from cache
   */
  evictObject(cache: any, typename: string, id: string) {
    cache.evict({ id: cache.identify({ __typename: typename, id }) })
    cache.gc()
  },

  /**
   * Evict all objects of a specific type
   */
  evictType(cache: any, typename: string) {
    cache.evict({ fieldName: typename })
    cache.gc()
  },

  /**
   * Evict a specific query
   */
  evictQuery(cache: any, queryName: string, variables?: Record<string, any>) {
    cache.evict({ fieldName: queryName, args: variables })
    cache.gc()
  },

  /**
   * Clear entire cache
   */
  clearCache(cache: any) {
    cache.clear()
  },
}
