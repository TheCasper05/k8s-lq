import { gql } from '@apollo/client/core'

/**
 * Query: Search workspaces
 * Used to fetch workspaces for dropdowns and lists
 */
export const SEARCH_WORKSPACES = gql`
  query SearchWorkspaces($where: FilterWorkspaceInput $orderBy: OrderByWorkspaceInput $paginationConfig: PaginationConfigInput ) {
    searchWorkspaces(where: $where orderBy: $orderBy paginationConfig: $paginationConfig ) {
      objects {
        id
        name
        slug
        description
        type
        isActive
      }
    }
  }
`

