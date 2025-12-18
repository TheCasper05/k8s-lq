import { gql } from '@apollo/client/core'

/**
 * Query: Search classrooms
 * Used to fetch classrooms for a specific workspace
 */
export const SEARCH_CLASSROOMS = gql`
  query SearchClassrooms($where: FilterClassroomInput $orderBy: OrderByClassroomInput $paginationConfig: PaginationConfigInput ) {
    searchClassrooms(where: $where orderBy: $orderBy paginationConfig: $paginationConfig ) {
      objects {
        id
        name
        uniqueCode
        description
        isActive
      }
    }
  }
`

