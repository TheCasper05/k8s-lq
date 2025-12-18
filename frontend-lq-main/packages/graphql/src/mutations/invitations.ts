import { gql } from '@apollo/client/core'

/**
 * Mutation: Create invitations
 * Used to create one or multiple invitations
 */
export const CREATE_INVITATIONS = gql`
  mutation CreateInvitations($inputCreateInvitations: [CreateInvitationInput!] $file: String) {
    createInvitations(input: $inputCreateInvitations, file: $file) {
      objects {
        id
        email
        status
        role
        workspace {
          id
          name
        }
        createdBy {
          id
          email
          firstName
          lastName
        }
        welcomeMessage
        expiresAt
        createdAt

      }
      errorsReport {
        objectPosition
        errors {
          field
          messages
        }
      }
    }
  }
`

/**
 * Mutation: Update invitations
 * Used to update one or multiple invitations
 */
export const UPDATE_INVITATIONS = gql`
  mutation UpdateInvitations($inputUpdateInvitations: [UpdateInvitationInput!]!) {
    updateInvitations(input: $inputUpdateInvitations) {
      objects {
        id
        email
        status
        role
        workspace {
          id
          name
        }
        createdBy {
          id
          email
          firstName
          lastName
        }
        welcomeMessage
        expiresAt
        createdAt
        revokedAt
        revokedBy {
          id
          email
          firstName
          lastName
        }
      }
      errorsReport {
        objectPosition
        errors {
          field
          messages
        }
      }
    }
  }
`

/**
 * Mutation: Resend invitation email
 * Used to resend an invitation email to a pending invitation
 */
export const RESEND_INVITATION = gql`
  mutation ResendInvitation($invitationId: ID!) {
    resendInvitation(invitationId: $invitationId) {
      success
      invitationId
      message
    }
  }
`

