import { provideApolloClient } from "@vue/apollo-composable";
import { createApolloClient } from "@lq/graphql";
import { useAuthStore } from "@lq/stores";

/**
 * Apollo Client plugin for Nuxt
 * Provides Apollo Client to the app with authentication
 */
export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig();
  const authStore = useAuthStore();

  // Build GraphQL endpoints from apiBaseUrl if not explicitly set
  const apiBaseUrl = config.public.apiBaseUrl as string;

  // Ensure endpoints end with trailing slash for Django APPEND_SLASH
  let graphqlEndpoint = (config.public.graphqlEndpoint as string) || `${apiBaseUrl}/graphql`;
  if (!graphqlEndpoint.endsWith("/")) {
    graphqlEndpoint += "/";
  }

  let graphqlWsEndpoint = (config.public.graphqlWsEndpoint as string) || `${apiBaseUrl.replace("http", "ws")}/graphql`;
  if (!graphqlWsEndpoint.endsWith("/")) {
    graphqlWsEndpoint += "/";
  }

  // Create Apollo Client with auth token getter
  if (import.meta.env.DEV || process.env.NODE_ENV === "development") {
    console.log("[Apollo Plugin] Runtime config values:", {
      apiBaseUrl: config.public.apiBaseUrl,
      graphqlEndpoint_raw: config.public.graphqlEndpoint,
      graphqlWsEndpoint_raw: config.public.graphqlWsEndpoint,
    });

    console.log("[Apollo Plugin] Initializing with endpoints:", {
      http: graphqlEndpoint,
      ws: graphqlWsEndpoint,
      apiBaseUrl: apiBaseUrl,
    });

    console.log("[Apollo Plugin] Using endpoints:", {
      http: graphqlEndpoint,
      ws: graphqlWsEndpoint,
    });
  }

  const apolloClient = createApolloClient({
    httpEndpoint: graphqlEndpoint,
    wsEndpoint: graphqlWsEndpoint,
    getAuth: () => {
      // Django-allauth uses session cookies, not Bearer tokens
      // The session cookie is sent automatically by the browser
      // Only send Bearer token if it's a real JWT token (not the mock "session-authenticated")
      const token = authStore.token;
      if (import.meta.env.DEV || process.env.NODE_ENV === "development") {
        console.log("[Apollo Auth] Token check:", {
          hasToken: !!token,
          tokenValue: token,
          willSendBearer: token && token !== "session-authenticated",
        });
      }
      if (token && token !== "session-authenticated") {
        return `Bearer ${token}`;
      }
      return "";
    },
    onError: (error) => {
      // Handle GraphQL errors globally
      console.error("GraphQL Error:", error);

      // Handle authentication errors
      if (error.networkError && "statusCode" in error.networkError) {
        if (error.networkError.statusCode === 401) {
          authStore.logout();
          navigateTo("/login");
        }
      }
    },
  });

  provideApolloClient(apolloClient);

  return {
    provide: {
      apollo: apolloClient,
    },
  };
});
