import { gql } from '@apollo/client/core'

/**
 * Query: Search invitations
 * Used by institutional app to list and manage user invitations
 */
export const SEARCH_INVITATIONS = gql`
  query SearchInvitations($where: FilterInvitationInput $orderBy: OrderByInvitationInput $paginationConfig: PaginationConfigInput ) {
    searchInvitations(where: $where orderBy: $orderBy paginationConfig: $paginationConfig ) {
      objects {
        id
        email
        status
        role
        welcomeMessage
        isActive
        createdAt
        expiresAt
        acceptedAt
        declinedAt
        workspace {
          id
          description
          name
        }
        createdBy {
          id
          firstName
          lastName
          email
        }
        revokedBy {
          firstName
          lastName
          id
          email
        }
      }
    }
  }
`
