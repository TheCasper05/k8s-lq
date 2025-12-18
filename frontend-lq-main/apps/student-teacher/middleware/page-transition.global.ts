export default defineNuxtRouteMiddleware((to, from) => {
  if (import.meta.client) {
    // Define route hierarchy for forward/backward detection
    const routeHierarchy = [
      "/auth/login",
      "/auth/login/email",
      "/auth/register",
      "/auth/register/account-type",
      "/auth/register/language-preferences",
      "/auth/register/personal-info",
      "/auth/register/institution-info",
      "/student/dashboard",
      "/teacher/dashboard",
      "/admin/dashboard",
      "/profile",
      "/settings",
    ];

    const fromIndex = routeHierarchy.indexOf(from.path);
    const toIndex = routeHierarchy.indexOf(to.path);

    // Determine transition direction
    let transitionName = "page-forward";

    if (fromIndex !== -1 && toIndex !== -1) {
      // Both routes are in hierarchy
      if (toIndex < fromIndex) {
        // Going backward in hierarchy (e.g., logout, back button)
        transitionName = "page-backward";
      } else {
        // Going forward in hierarchy
        transitionName = "page-forward";
      }
    } else if (
      (from.path.startsWith("/student") || from.path.startsWith("/teacher") || from.path.startsWith("/admin")) &&
      to.path.startsWith("/auth")
    ) {
      // Logout scenario - always backward
      transitionName = "page-backward";
    } else if (
      from.path.startsWith("/auth") &&
      (to.path.startsWith("/student") || to.path.startsWith("/teacher") || to.path.startsWith("/admin"))
    ) {
      // Login/Register complete - always forward
      transitionName = "page-forward";
    }

    // Set the transition on both to and from routes
    to.meta.pageTransition = { name: transitionName, mode: "out-in" };
    from.meta.pageTransition = { name: transitionName, mode: "out-in" };
  }
});
