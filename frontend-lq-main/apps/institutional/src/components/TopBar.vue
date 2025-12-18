<template>
  <div class="topbar">
    <div class="topbar-content">
      <!-- Logo y título -->
      <div class="topbar-brand">
        <h1 class="topbar-logo">LingoQuesto</h1>
        <span class="topbar-subtitle">Institucional</span>
      </div>

      <!-- Navegación -->
      <nav class="topbar-nav">
        <RouterLink to="/dashboard" class="nav-link" active-class="active">
          <Icon icon="solar:home-line-duotone" />
          <span>Dashboard</span>
        </RouterLink>
        <RouterLink to="/invitations" class="nav-link" active-class="active">
          <Icon icon="solar:letter-line-duotone" />
          <span>Invitaciones</span>
        </RouterLink>
      </nav>

      <!-- Usuario y acciones -->
      <div class="topbar-actions">
        <div v-if="authStore.userProfile" class="user-info">
          <span class="user-name">{{ authStore.userProfile.firstName }} {{ authStore.userProfile.lastName }}</span>
          <span class="user-email">{{ authStore.userProfile.user.email }}</span>
        </div>

        <Button label="Cerrar sesión" severity="secondary" text @click="handleLogout">
          <template #icon>
            <Icon icon="solar:logout-line-duotone" />
          </template>
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { useRouter } from "vue-router";
  import { useAuthStore } from "@lq/stores";
  import Button from "primevue/button";
  import { Icon } from "@iconify/vue";

  const router = useRouter();
  const authStore = useAuthStore();

  const handleLogout = async () => {
    await authStore.logout();
    router.push("/login");
  };
</script>

<style scoped>
  .topbar {
    background: white;
    border-bottom: 1px solid #e2e8f0;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    position: sticky;
    top: 0;
    z-index: 100;
  }

  .topbar-content {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0.75rem 2rem;
    display: flex;
    align-items: center;
    gap: 2rem;
    justify-content: space-between;
  }

  .topbar-brand {
    display: flex;
    align-items: baseline;
    gap: 0.5rem;
  }

  .topbar-logo {
    font-size: 1.5rem;
    font-weight: 700;
    color: #7008e7;
    margin: 0;
  }

  .topbar-subtitle {
    font-size: 0.875rem;
    color: #64748b;
    font-weight: 500;
  }

  .topbar-nav {
    display: flex;
    gap: 0.5rem;
    flex: 1;
  }

  .nav-link {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    color: #64748b;
    text-decoration: none;
    font-weight: 500;
    transition: all 0.2s;
  }

  .nav-link:hover {
    background: #f1f5f9;
    color: #7008e7;
  }

  .nav-link.active {
    background: #ede9fe;
    color: #7008e7;
  }

  .topbar-actions {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .user-info {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.125rem;
  }

  .user-name {
    font-size: 0.875rem;
    font-weight: 600;
    color: #1e293b;
  }

  .user-email {
    font-size: 0.75rem;
    color: #64748b;
  }

  @media (max-width: 768px) {
    .topbar-content {
      padding: 0.75rem 1rem;
      flex-wrap: wrap;
    }

    .topbar-nav {
      order: 3;
      width: 100%;
      margin-top: 0.5rem;
      padding-top: 0.5rem;
      border-top: 1px solid #e2e8f0;
    }

    .user-info {
      display: none;
    }
  }
</style>
