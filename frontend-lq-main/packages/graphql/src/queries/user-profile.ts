import { gql } from '@apollo/client/core'
import { INSTITUTION_CORE_FIELDS,  USER_PROFILE_CORE_FIELDS } from '../fragments'

/**
 * Fragment: UserProfile Core Fields
 * Reutilizable fragment with all common UserProfile fields
 * Use this in mutations and queries to maintain consistency
 */
export const GET_USER_PROFILE_BY_ID = gql`

  ${USER_PROFILE_CORE_FIELDS}

  query GetUserProfileById($id: UUID!) {
    readUserProfile(where: {user: {id: {exact: $id}}}) {
      ...UserProfile
    }
  }
`

export const CREATE_USER_PROFILE = gql`

  ${USER_PROFILE_CORE_FIELDS}

  mutation CreateUserProfile($input: [CreateUserProfileInput!]!) {
    createUserProfiles(
      input: $input
    ) {
      objects {
        ...UserProfile
      }
    }
  }
`

export const CREATE_INSTITUTION = gql`
  ${INSTITUTION_CORE_FIELDS}

  mutation CreateInstitution($input: [CreateInstitutionInput!]!) {
    createInstitutions(input: $input) {
      objects {
        ...Institution
      }
    }
  }
`