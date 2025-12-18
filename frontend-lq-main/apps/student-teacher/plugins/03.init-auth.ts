import { useAuthStore, setAllauthInstance, setApolloInstance } from "@lq/stores";

export default defineNuxtPlugin(async () => {
  const { $allauth, $apollo } = useNuxtApp();
  const authStore = useAuthStore();

  // Initialize store dependencies
  setAllauthInstance($allauth);
  setApolloInstance($apollo);

  // Restore session on client side
  if (import.meta.client) {
    try {
      await authStore.restoreSession();

      // If authenticated after restore, fetch full profile
      if (authStore.isAuthenticated && authStore.userAuth) {
        await authStore.fetchCurrentUserById(authStore.userAuth);
      }
    } catch (error) {
      console.error("Failed to restore session:", error);
    }
  }
});
