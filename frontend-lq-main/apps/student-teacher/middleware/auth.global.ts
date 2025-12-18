/**
 * Global authentication middleware
 * DISABLED - No authentication required (public app)
 */
export default defineNuxtRouteMiddleware(() => {
  // No authentication checks
  // All routes are accessible without login
});
