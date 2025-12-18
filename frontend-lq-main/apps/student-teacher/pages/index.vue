<script setup lang="ts">
  import { useAuthStore } from "@lq/stores";
  import { getRoleDashboardRoute } from "@lq/utils";

  definePageMeta({
    layout: false,
    middleware: [
      function () {
        const authStore = useAuthStore();

        // If not authenticated, redirect to login
        if (!authStore.isAuthenticated) {
          return navigateTo("/auth/login");
        }

        // If authenticated, redirect to role-specific dashboard
        const userRole = authStore.userProfile?.primaryRole || authStore.userProfileComplete?.primaryRole;
        const targetDashboard = getRoleDashboardRoute(userRole) || "/auth/login";
        return navigateTo(targetDashboard);
      },
    ],
  });
</script>

<template>
  <div />
</template>
