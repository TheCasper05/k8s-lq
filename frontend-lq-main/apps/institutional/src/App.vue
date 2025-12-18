<template>
  <div class="app-container">
    <!-- TopBar - Solo para usuarios autenticados -->
    <TopBar v-if="authStore.isAuthenticated" />

    <div class="main-content">
      <RouterView />
    </div>

    <Toast />
  </div>
</template>

<script setup lang="ts">
  import { useAuthStore } from "@lq/stores";
  import Toast from "primevue/toast";
  import TopBar from "./components/TopBar.vue";

  const authStore = useAuthStore();
</script>

<!-- <style>
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  .app-container {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  .navbar {
    background: white;
    border-bottom: 1px solid var(--surface-border);
    padding: 1rem 2rem;
    position: sticky;
    top: 0;
    z-index: 1000;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }

  .navbar-content {
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .navbar-brand {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--primary-color);
  }

  .navbar-brand i {
    font-size: 1.5rem;
  }

  .brand-text {
    display: none;
  }

  @media (min-width: 768px) {
    .brand-text {
      display: inline;
    }
  }

  .navbar-actions {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .main-content {
    flex: 1;
    background: var(--surface-ground);
  }

  @media (max-width: 768px) {
    .navbar {
      padding: 0.75rem 1rem;
    }

    .navbar-brand {
      font-size: 1rem;
    }

    .navbar-brand i {
      font-size: 1.25rem;
    }
  }
</style> -->
