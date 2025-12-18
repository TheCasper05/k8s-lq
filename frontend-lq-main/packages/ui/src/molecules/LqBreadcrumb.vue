<script setup lang="ts">
  import type { Component } from "vue";

  interface BreadcrumbItem {
    label: string;
    to: string;
    active: boolean;
  }

  interface Props {
    items: BreadcrumbItem[];
    linkComponent?: Component | string;
    separator?: string;
  }

  withDefaults(defineProps<Props>(), {
    linkComponent: "a",
    separator: "/",
  });

  defineOptions({
    name: "LqBreadcrumb",
  });
</script>

<template>
  <nav aria-label="Breadcrumb" class="flex flex-col">
    <ol class="flex items-center flex-wrap">
      <li v-for="(crumb, index) in items" :key="crumb.to" class="flex items-center">
        <!-- Separator -->
        <span v-if="index > 0" class="text-surface-400 dark:text-surface-500 mx-2">
          {{ separator }}
        </span>

        <!-- Link -->
        <component
          :is="linkComponent"
          v-if="!crumb.active"
          :to="crumb.to"
          class="text-surface-500 hover:text-primary-600 dark:text-surface-400 dark:hover:text-primary-400 transition-colors font-medium no-underline flex items-center gap-2"
        >
          {{ crumb.label }}
        </component>

        <!-- Active Item -->
        <span
          v-else
          class="text-primary-600 dark:text-primary-400 font-semibold flex items-center gap-2"
          aria-current="page"
        >
          {{ crumb.label }}
        </span>
      </li>
    </ol>
  </nav>
</template>
