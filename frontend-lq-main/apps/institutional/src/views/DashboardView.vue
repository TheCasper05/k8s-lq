<template>
  <div class="dashboard-container">
    <!-- Header -->
    <div class="dashboard-header">
      <h1 class="dashboard-title">{{ $t("dashboard.title") }}</h1>
      <p class="dashboard-subtitle">{{ $t("teacher.dashboard.subtitle") }}</p>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <Card class="stat-card">
        <template #content>
          <div class="stat-content">
            <div class="stat-icon students">
              <i class="pi pi-users" />
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ stats.students }}</p>
              <p class="stat-label">{{ $t("teacher.dashboard.stats.students") }}</p>
            </div>
          </div>
        </template>
      </Card>

      <Card class="stat-card">
        <template #content>
          <div class="stat-content">
            <div class="stat-icon classrooms">
              <i class="pi pi-building" />
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ stats.classrooms }}</p>
              <p class="stat-label">{{ $t("teacher.dashboard.stats.classrooms") }}</p>
            </div>
          </div>
        </template>
      </Card>

      <Card class="stat-card">
        <template #content>
          <div class="stat-content">
            <div class="stat-icon scenarios">
              <i class="pi pi-book" />
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ stats.scenarios }}</p>
              <p class="stat-label">{{ $t("teacher.dashboard.stats.scenarios") }}</p>
            </div>
          </div>
        </template>
      </Card>

      <Card class="stat-card">
        <template #content>
          <div class="stat-content">
            <div class="stat-icon curriculums">
              <i class="pi pi-list" />
            </div>
            <div class="stat-info">
              <p class="stat-value">{{ stats.curriculums }}</p>
              <p class="stat-label">{{ $t("teacher.dashboard.stats.curriculums") }}</p>
            </div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Action Buttons -->
    <div class="actions-section">
      <h2 class="section-title">{{ $t("common.actions") || "Quick Actions" }}</h2>
      <div class="actions-grid">
        <Button
          label="Gestionar Invitaciones"
          icon="pi pi-envelope"
          severity="primary"
          @click="handleAction('invitations')"
        />
        <Button
          :label="$t('teacher.dashboard.actions.manageStudents')"
          icon="pi pi-users"
          class="p-button-outlined"
          @click="handleAction('students')"
        />
        <Button
          :label="$t('teacher.dashboard.actions.manageClassrooms')"
          icon="pi pi-building"
          class="p-button-outlined"
          @click="handleAction('classrooms')"
        />
        <Button
          :label="$t('teacher.dashboard.actions.manageScenarios')"
          icon="pi pi-book"
          class="p-button-outlined"
          @click="handleAction('scenarios')"
        />
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="recent-section">
      <div class="recent-classrooms">
        <h2 class="section-title">{{ $t("teacher.dashboard.recentClassrooms") }}</h2>
        <Card v-if="recentClassrooms.length > 0">
          <template #content>
            <DataTable :value="recentClassrooms" :rows="5">
              <Column field="name" :header="$t('common.name') || 'Name'" />
              <Column field="students" :header="$t('teacher.dashboard.students')" />
              <Column field="date" :header="$t('teacher.scenarios.createdOn')" />
            </DataTable>
          </template>
        </Card>
        <Card v-else>
          <template #content>
            <div class="empty-state">
              <i class="pi pi-building empty-icon" />
              <p>{{ $t("teacher.dashboard.noClassrooms") }}</p>
              <Button
                :label="$t('teacher.dashboard.createClassroom')"
                icon="pi pi-plus"
                class="p-button-sm"
                @click="handleAction('create-classroom')"
              />
            </div>
          </template>
        </Card>
      </div>

      <div class="recent-scenarios">
        <h2 class="section-title">{{ $t("teacher.dashboard.recentScenarios") }}</h2>
        <Card v-if="recentScenarios.length > 0">
          <template #content>
            <DataTable :value="recentScenarios" :rows="5">
              <Column field="name" :header="$t('common.name') || 'Name'" />
              <Column field="level" :header="$t('common.level') || 'Level'" />
              <Column field="date" :header="$t('teacher.scenarios.createdOn')" />
            </DataTable>
          </template>
        </Card>
        <Card v-else>
          <template #content>
            <div class="empty-state">
              <i class="pi pi-book empty-icon" />
              <p>{{ $t("teacher.dashboard.noScenarios") }}</p>
              <Button
                :label="$t('teacher.dashboard.createScenario')"
                icon="pi pi-plus"
                class="p-button-sm"
                @click="handleAction('create-scenario')"
              />
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Language Demo Section -->
    <div class="demo-section">
      <Card>
        <template #title>
          <div class="demo-header">
            <i class="pi pi-globe" />
            <span>{{ $t("common.settings") || "i18n Demo" }}</span>
          </div>
        </template>
        <template #content>
          <div class="demo-content">
            <p>
              <strong>{{ $t("common.loading") }}:</strong>
              {{ $t("common.loading") }}
            </p>
            <p>
              <strong>{{ $t("common.save") }}:</strong>
              {{ $t("common.save") }}
            </p>
            <p>
              <strong>{{ $t("common.cancel") }}:</strong>
              {{ $t("common.cancel") }}
            </p>
            <p>
              <strong>{{ $t("auth.login") }}:</strong>
              {{ $t("auth.login") }}
            </p>
            <p>
              <strong>{{ $t("errors.notFound") }}:</strong>
              {{ $t("errors.notFound") }}
            </p>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref } from "vue";
  import { useI18n } from "vue-i18n";
  import { useRouter } from "vue-router";
  import Card from "primevue/card";
  import Button from "primevue/button";
  import DataTable from "primevue/datatable";
  import Column from "primevue/column";

  const { t: _t } = useI18n();
  const router = useRouter();

  // Stats data
  const stats = ref({
    students: 156,
    classrooms: 12,
    scenarios: 34,
    curriculums: 8,
  });

  // Recent classrooms
  const recentClassrooms = ref([
    { name: "Advanced English", students: 24, date: "2024-11-15" },
    { name: "Beginner Spanish", students: 18, date: "2024-11-14" },
    { name: "Intermediate French", students: 20, date: "2024-11-13" },
  ]);

  // Recent scenarios
  const recentScenarios = ref([
    { name: "Restaurant Conversation", level: "B1", date: "2024-11-16" },
    { name: "Job Interview", level: "B2", date: "2024-11-15" },
    { name: "Travel Planning", level: "A2", date: "2024-11-14" },
  ]);

  const handleAction = (action: string) => {
    if (action === "invitations") {
      router.push("/invitations");
    } else {
      console.log("Action:", action);
    }
  };
</script>

<style scoped>
  .dashboard-container {
    padding: 2rem;
    max-width: 1400px;
    margin: 0 auto;
  }

  .dashboard-header {
    margin-bottom: 2rem;
  }

  .dashboard-title {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-color);
    margin-bottom: 0.5rem;
  }

  .dashboard-subtitle {
    font-size: 1rem;
    color: var(--text-color-secondary);
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
  }

  .stat-card {
    transition: transform 0.2s;
  }

  .stat-card:hover {
    transform: translateY(-4px);
  }

  .stat-content {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .stat-icon {
    width: 60px;
    height: 60px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    color: white;
  }

  .stat-icon.students {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }

  .stat-icon.classrooms {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  }

  .stat-icon.scenarios {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  }

  .stat-icon.curriculums {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  }

  .stat-info {
    flex: 1;
  }

  .stat-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-color);
    margin: 0;
  }

  .stat-label {
    font-size: 0.875rem;
    color: var(--text-color-secondary);
    margin: 0;
  }

  .actions-section {
    margin-bottom: 2rem;
  }

  .section-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-color);
    margin-bottom: 1rem;
  }

  .actions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
  }

  .recent-section {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 2rem;
    margin-bottom: 2rem;
  }

  .empty-state {
    text-align: center;
    padding: 2rem;
  }

  .empty-icon {
    font-size: 3rem;
    color: var(--text-color-secondary);
    margin-bottom: 1rem;
  }

  .empty-state p {
    color: var(--text-color-secondary);
    margin-bottom: 1rem;
  }

  .demo-section {
    margin-top: 2rem;
  }

  .demo-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .demo-content p {
    margin: 0.5rem 0;
    padding: 0.5rem;
    background: var(--surface-50);
    border-radius: 6px;
  }

  @media (max-width: 768px) {
    .dashboard-container {
      padding: 1rem;
    }

    .stats-grid {
      grid-template-columns: 1fr;
    }

    .actions-grid {
      grid-template-columns: 1fr;
    }

    .recent-section {
      grid-template-columns: 1fr;
    }
  }
</style>
