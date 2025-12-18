<script setup lang="ts">
  import { computed } from "vue";
  import { useRoute } from "vue-router";
  import { LqBreadcrumb } from "@lq/ui";
  import type { Component } from "nuxt/schema";

  const route = useRoute();
  const NuxtLink = resolveComponent("NuxtLink") as Component;

  const breadcrumbs = computed(() => {
    const fullPath = route.path;
    const pathArray = fullPath.split("/").filter((p) => p);

    // Default to Dashboard if root
    if (pathArray.length === 0) {
      return [
        {
          label: "Dashboard",
          to: "/",
          active: true,
        },
      ];
    }

    let currentPath = "";
    const crumbs = pathArray.map((segment, index) => {
      currentPath += `/${segment}`;

      // Format label: capitalize and replace hyphens
      let label = segment.charAt(0).toUpperCase() + segment.slice(1).replace(/-/g, " ");

      // Handle specific cases if needed
      if (segment === "student") label = "Student";
      if (segment === "teacher") label = "Teacher";
      if (segment === "admin") label = "Admin";

      return {
        label: label,
        to: currentPath,
        active: index === pathArray.length - 1,
      };
    });

    return crumbs;
  });
</script>

<template>
  <LqBreadcrumb :items="breadcrumbs" :link-component="NuxtLink" />
</template>
