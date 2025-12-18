<template>
  <div class="users-container">
    <div class="users-header">
      <h1 class="users-title">{{ $t("common.users") || "Users" }}</h1>
      <p class="users-subtitle">{{ $t("common.search") || "Search and manage users" }}</p>
    </div>

    <Card v-if="loading" class="loading-card">
      <template #content>
        <div class="loading-state">
          <Icon icon="solar:refresh-line-duotone" class="animate-spin" style="font-size: 2rem" />
          <p>{{ $t("common.loading") || "Loading..." }}</p>
        </div>
      </template>
    </Card>

    <Card v-else-if="error" class="error-card">
      <template #content>
        <div class="error-state">
          <Icon icon="solar:danger-triangle-line-duotone" style="font-size: 2rem; color: var(--red-500)" />
          <p>{{ error.message }}</p>
        </div>
      </template>
    </Card>

    <Card v-else-if="users && users.length > 0">
      <template #content>
        <DataTable :value="users" :rows="10" :paginator="true" responsive-layout="scroll">
          <Column field="id" header="ID" :sortable="true" />
          <Column field="firstName" :header="$t('common.name') || 'Name'" :sortable="true" />
          <Column field="email" :header="$t('common.email') || 'Email'" :sortable="true" />
          <Column :header="$t('common.actions') || 'Actions'">
            <template #body="slotProps">
              <Button class="p-button-rounded p-button-text" @click="viewUser(slotProps.data)">
                <template #icon>
                  <Icon icon="solar:eye-line-duotone" />
                </template>
              </Button>
              <Button class="p-button-rounded p-button-text" @click="inviteUser(slotProps.data)">
                <template #icon>
                  <Icon icon="solar:letter-line-duotone" />
                </template>
              </Button>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Card v-else>
      <template #content>
        <div class="empty-state">
          <Icon icon="solar:users-group-rounded-line-duotone" class="empty-icon" />
          <p>{{ $t("common.noResults") || "No users found" }}</p>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
  import { computed } from "vue";
  import { useI18n } from "vue-i18n";
  import { useQuery, GET_USER_PROFILE_BY_ID } from "@lq/graphql";
  import Card from "primevue/card";
  import Button from "primevue/button";
  import DataTable from "primevue/datatable";
  import Column from "primevue/column";

  const { t: _t } = useI18n();

  // GraphQL Query
  const { result, loading, error } = useQuery(GET_USER_PROFILE_BY_ID);

  // Computed properties
  const users = computed(() => result.value?.searchUsers?.objects ?? []);

  // Actions
  const viewUser = (user: unknown) => {
    console.log("View user:", user);
  };

  const inviteUser = (user: unknown) => {
    console.log("Invite user:", user);
  };
</script>

<style scoped>
  .users-container {
    padding: 2rem;
    max-width: 1400px;
    margin: 0 auto;
  }

  .users-header {
    margin-bottom: 2rem;
  }

  .users-title {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-color);
    margin-bottom: 0.5rem;
  }

  .users-subtitle {
    font-size: 1rem;
    color: var(--text-color-secondary);
  }

  .loading-state,
  .error-state,
  .empty-state {
    text-align: center;
    padding: 3rem;
  }

  .loading-state i,
  .error-state i {
    margin-bottom: 1rem;
  }

  .empty-icon {
    font-size: 3rem;
    color: var(--text-color-secondary);
    margin-bottom: 1rem;
  }

  .empty-state p,
  .error-state p,
  .loading-state p {
    color: var(--text-color-secondary);
    margin: 0;
  }

  @media (max-width: 768px) {
    .users-container {
      padding: 1rem;
    }
  }
</style>
