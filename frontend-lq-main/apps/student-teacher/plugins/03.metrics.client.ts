import { useMetrics } from "@lq/utils";

/**
 * Metrics tracking plugin (client-side only)
 * Tracks page views and user interactions
 */
export default defineNuxtPlugin(() => {
  const router = useRouter();
  const metrics = useMetrics();

  // Track page views
  router.afterEach((to) => {
    metrics.trackPageView({
      path: to.path,
      name: to.name as string,
      params: to.params,
    });
  });

  // Track initial page load
  metrics.trackPageView({
    path: router.currentRoute.value.path,
    name: router.currentRoute.value.name as string,
    params: router.currentRoute.value.params,
  });
});
