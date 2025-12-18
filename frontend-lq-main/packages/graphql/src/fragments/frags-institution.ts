import { gql } from '@apollo/client/core'

export const INSTITUTION_CORE_FIELDS = gql`
  fragment Institution on InstitutionType {
    city
    address
    contactEmail
    contactPhone
    country
    createdAt
    deletedAt
    description
    id
    isActive
    logo
    name
    slug
    timezone
    updatedAt
    settings
    website
  }
`

