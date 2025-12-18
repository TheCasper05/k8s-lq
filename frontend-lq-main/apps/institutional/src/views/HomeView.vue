<template>
  <div class="home-container">
    <div class="hero-section">
      <h1 class="hero-title">{{ $t("home.welcome") }}</h1>
      <p class="hero-description">{{ $t("home.description") }}</p>
    </div>

    <div class="features-grid">
      <Card class="feature-card">
        <template #content>
          <div class="feature-content">
            <i class="pi pi-users feature-icon" />
            <h3>{{ $t("home.forTeachers") }}</h3>
            <p>{{ $t("home.forTeachersDesc") }}</p>
          </div>
        </template>
      </Card>

      <Card class="feature-card">
        <template #content>
          <div class="feature-content">
            <i class="pi pi-book feature-icon" />
            <h3>{{ $t("home.forStudents") }}</h3>
            <p>{{ $t("home.forStudentsDesc") }}</p>
          </div>
        </template>
      </Card>

      <Card class="feature-card">
        <template #content>
          <div class="feature-content">
            <i class="pi pi-sparkles feature-icon" />
            <h3>{{ $t("home.poweredByAI") }}</h3>
            <p>{{ $t("home.poweredByAIDesc") }}</p>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
  import Card from "primevue/card";
</script>

<style scoped>
  .home-container {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
  }

  .hero-section {
    text-align: center;
    padding: 4rem 2rem;
    margin-bottom: 3rem;
  }

  .hero-title {
    font-size: 3rem;
    font-weight: 700;
    color: var(--text-color);
    margin-bottom: 1rem;
  }

  .hero-description {
    font-size: 1.25rem;
    color: var(--text-color-secondary);
    margin-bottom: 2rem;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
  }

  .cta-buttons {
    display: flex;
    gap: 1rem;
    justify-content: center;
  }

  .features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-top: 3rem;
  }

  .feature-card {
    transition: transform 0.2s;
  }

  .feature-card:hover {
    transform: translateY(-4px);
  }

  .feature-content {
    text-align: center;
    padding: 1rem;
  }

  .feature-icon {
    font-size: 3rem;
    color: var(--primary-color);
    margin-bottom: 1rem;
  }

  .feature-content h3 {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--text-color);
    margin-bottom: 0.5rem;
  }

  .feature-content p {
    color: var(--text-color-secondary);
    line-height: 1.6;
  }

  @media (max-width: 768px) {
    .hero-title {
      font-size: 2rem;
    }

    .hero-description {
      font-size: 1rem;
    }

    .features-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
