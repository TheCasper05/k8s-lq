import { gql } from '@apollo/client/core'

/**
 * Fragment: UserProfile Core Fields
 * Reutilizable fragment with all common UserProfile fields
 * Use this in mutations and queries to maintain consistency
 */
export const USER_PROFILE_CORE_FIELDS = gql`
  fragment UserProfile on UserProfileType {
    id
    publicId
    primaryRole
    firstName
    lastName
    phone
    photo
    birthday
    country
    languagePreference
    timezone
    isActive
    user {
      id
      email
    }
  }
`

/**
 * Fragment: UserProfile Basic Fields
 * Lighter version with only essential fields for listings
 */
export const USER_PROFILE_BASIC_FIELDS = gql`
  fragment UserProfileBasicFields on UserProfileType {
    id
    publicId
    primaryRole
    firstName
    lastName
    phone
    photo
    languagePreference
    timezone
  }
`
