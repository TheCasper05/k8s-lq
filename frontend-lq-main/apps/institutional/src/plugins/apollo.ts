import type { App } from "vue";
import { DefaultApolloClient } from "@vue/apollo-composable";
import { createApolloClient } from "@lq/graphql";
import { useAuthStore } from "@lq/stores";
import type { ApolloClient, NormalizedCacheObject } from "@apollo/client/core";

// Export apollo client instance for access outside plugin
// Using a mutable object to allow reassignment while keeping the export const
export const apolloClientContainer: { client: ApolloClient<NormalizedCacheObject> | null } = { client: null };

export const apolloPlugin = {
  install(app: App) {
    apolloClientContainer.client = createApolloClient({
      httpEndpoint: import.meta.env.VITE_GRAPHQL_ENDPOINT,
      wsEndpoint: import.meta.env.VITE_GRAPHQL_WS_ENDPOINT,
      getAuth: () => {
        const authStore = useAuthStore();
        const token = authStore.token;
        return token ? `Bearer ${token}` : "";
      },
      onError: (error) => {
        console.error("GraphQL Error:", error);

        if (error.networkError && "statusCode" in error.networkError) {
          if (error.networkError.statusCode === 401) {
            const authStore = useAuthStore();
            authStore.logout();
            window.location.href = "/login";
          }
        }
      },
    });

    app.provide(DefaultApolloClient, apolloClientContainer.client);
  },
};
