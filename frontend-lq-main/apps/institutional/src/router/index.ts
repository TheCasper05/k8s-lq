import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";
import { useAuthStore } from "@lq/stores";

const routes: RouteRecordRaw[] = [
  {
    path: "/",
    name: "home",
    redirect: "/dashboard",
  },
  {
    path: "/login",
    name: "login",
    component: () => import("../views/LoginView.vue"),
    meta: { public: true },
  },
  {
    path: "/register",
    name: "register",
    component: () => import("../views/RegisterView.vue"),
    meta: { public: true },
  },
  {
    path: "/dashboard",
    name: "dashboard",
    component: () => import("../views/DashboardView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/management",
    component: () => import("../views/ManagementWrapper.vue"),
    meta: { requiresAuth: true },
    redirect: "/management/invitations",
    children: [
      {
        path: "workspaces",
        name: "workspaces",
        component: () => import("../views/workspaces/WorkspaceIndex.vue"),
        meta: { requiresAuth: true },
      },
      {
        path: "licenses",
        name: "licenses",
        component: () => import("../views/licenses/LicenseIndex.vue"),
        meta: { requiresAuth: true },
      },
      {
        path: "invitations",
        name: "invitations",
        component: () => import("../views/invitations/InvitationIndex.vue"),
        meta: { requiresAuth: true },
      },
    ],
  },
  {
    path: "/users",
    name: "users",
    component: () => import("../views/users/Index.vue"),
    meta: { public: true },
  },
  {
    path: "/unauthorized",
    name: "unauthorized",
    component: () => import("../pages/UnauthorizedView.vue"),
    meta: { public: true },
  },
  {
    path: "/:pathMatch(.*)*",
    name: "not-found",
    component: () => import("../pages/NotFoundView.vue"),
    meta: { public: true },
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore();

  // Redirect to dashboard if already authenticated and trying to access login
  if (to.name === "login" && authStore.isAuthenticated) {
    return next({ name: "dashboard" });
  }

  if (to.name === "register" && authStore.isAuthenticated) {
    return next({ name: "dashboard" });
  }

  // Require authentication for protected routes
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next({
      name: "login",
      query: { redirect: to.fullPath },
    });
  }

  // Check role-based access
  if (to.meta.roles && Array.isArray(to.meta.roles)) {
    const userRole = authStore.userRole;

    if (!userRole || !to.meta.roles.includes(userRole)) {
      return next({ name: "unauthorized" });
    }
  }

  next();
});

export default router;
