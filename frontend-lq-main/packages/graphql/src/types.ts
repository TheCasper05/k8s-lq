import type { ApolloError } from '@apollo/client'

export interface ApolloClientConfig {
  httpEndpoint: string
  wsEndpoint: string
  getAuth?: () => string
  onError?: (error: ApolloError) => void
}

export interface WebSocketConfig {
  reconnect: boolean
  reconnectionAttempts: number
  reconnectionDelay: number
  heartbeat: {
    interval: number
    timeout: number
  }
}
