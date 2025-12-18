import { computed, type Ref } from "vue";
import { useQuery } from "@vue/apollo-composable";
import { SEARCH_INVITATIONS } from "@lq/graphql";
import type { InvitationFromAPI } from "~/utils/invitations/types";

/**
 * Composable for managing invitation queries and filtering
 * @param searchQuery - Reactive search query string
 * @returns Invitations data, loading state, error, and refetch function
 */
export function useInvitations(searchQuery: Ref<string>) {
  const {
    result: tableResult,
    loading,
    error,
    refetch,
  } = useQuery(SEARCH_INVITATIONS, () => ({
    where: {
      OR: [
        {
          email: {
            icontains: searchQuery.value,
          },
        },
        {
          workspace: {
            name: {
              icontains: searchQuery.value,
            },
          },
        },
      ],
    },
    orderBy: {
      email: "IASC",
    },
  }));

  const invitations = computed(() => {
    const objects = tableResult.value?.searchInvitations?.objects;
    if (!objects) return [];
    return objects.filter((inv: InvitationFromAPI | null): inv is InvitationFromAPI => inv !== null);
  });

  return {
    invitations,
    loading,
    error,
    refetch,
  };
}
