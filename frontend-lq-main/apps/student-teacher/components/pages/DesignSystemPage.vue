<script setup lang="ts">
  import { ref } from "vue";
  import { useSidebar } from "~/composables/useSidebar";
  import Chart from "primevue/chart";
  import { LqCard } from "@lq/ui";

  const { sidebarVisible } = useSidebar();

  // DataTable configuration
  interface Customer {
    id: number;
    name: string;
    country: { name: string; code: string };
    representative: { name: string; image: string };
    date: string;
    balance: number;
    status: string;
    activity: number;
    verified: boolean;
    chartData?: { labels: string[]; datasets: Record<string, unknown>[] };
  }

  interface TableColumn {
    field: string;
    header: string;
    filterable?: boolean;
    style?: string;
  }

  const tableColumns: TableColumn[] = [
    { field: "name", header: "Name", filterable: true, style: "min-width: 12rem" },
    { field: "country", header: "Country", filterable: true, style: "min-width: 12rem" },
    { field: "representative", header: "Agent", filterable: true, style: "min-width: 14rem" },
    { field: "date", header: "Date", filterable: false, style: "min-width: 10rem" },
    { field: "balance", header: "Balance", filterable: false, style: "min-width: 10rem" },
    { field: "status", header: "Status", filterable: true, style: "min-width: 12rem" },
    { field: "activity", header: "Activity", filterable: false, style: "min-width: 12rem" },
    { field: "verified", header: "Verified", filterable: true, style: "min-width: 8rem" },
    { field: "chartData", header: "Chart", filterable: false, style: "min-width: 15rem" },
  ];

  const customers = ref<Customer[]>([
    {
      id: 1000,
      name: "James Butt",
      country: { name: "Algeria", code: "dz" },
      representative: { name: "Ioni Bowcher", image: "ionibowcher.png" },
      date: "2015-09-13",
      balance: 70663,
      status: "unqualified",
      activity: 17,
      verified: true,
      chartData: {
        labels: ["Q1", "Q2", "Q3", "Q4"],
        datasets: [
          {
            data: [30, 25, 20, 25],
            backgroundColor: ["#3b82f6", "#10b981", "#f59e0b", "#ef4444"],
          },
        ],
      },
    },
    {
      id: 1001,
      name: "Josephine Darakjy",
      country: { name: "Egypt", code: "eg" },
      representative: { name: "Amy Elsner", image: "amyelsner.png" },
      date: "2019-02-09",
      balance: 98270,
      status: "qualified",
      activity: 92,
      verified: true,
      chartData: {
        labels: ["Q1", "Q2", "Q3", "Q4"],
        datasets: [
          {
            data: [45, 35, 40, 38],
            backgroundColor: ["#8b5cf6", "#06b6d4", "#ec4899", "#14b8a6"],
          },
        ],
      },
    },
    {
      id: 1002,
      name: "Art Venere",
      country: { name: "Panama", code: "pa" },
      representative: { name: "Bernardo Dominic", image: "bernardodominic.png" },
      date: "2017-04-29",
      balance: 44546,
      status: "negotiation",
      activity: 55,
      verified: false,
      chartData: {
        labels: ["Q1", "Q2", "Q3", "Q4"],
        datasets: [
          {
            data: [20, 30, 25, 35],
            backgroundColor: ["#f97316", "#06b6d4", "#6366f1", "#d946ef"],
          },
        ],
      },
    },
    {
      id: 1003,
      name: "Lenna Paprocki",
      country: { name: "Bosnia and Herzegovina", code: "ba" },
      representative: { name: "Elwin Sharvill", image: "elwinsharvill.png" },
      date: "2020-05-30",
      balance: 120934,
      status: "new",
      activity: 38,
      verified: true,
      chartData: {
        labels: ["Q1", "Q2", "Q3", "Q4"],
        datasets: [
          {
            data: [50, 40, 45, 55],
            backgroundColor: ["#3b82f6", "#8b5cf6", "#ec4899", "#f59e0b"],
          },
        ],
      },
    },
    {
      id: 1004,
      name: "Donette Foller",
      country: { name: "South Africa", code: "za" },
      representative: { name: "Ivan Magalhaes", image: "ivanmagalhaes.png" },
      date: "2021-02-12",
      balance: 49741,
      status: "renewal",
      activity: 64,
      verified: false,
      chartData: {
        labels: ["Q1", "Q2", "Q3", "Q4"],
        datasets: [
          {
            data: [25, 20, 30, 28],
            backgroundColor: ["#10b981", "#06b6d4", "#3b82f6", "#8b5cf6"],
          },
        ],
      },
    },
  ]);

  const formatDate = (value: string): string => {
    return new Date(value).toLocaleDateString("en-US", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    });
  };

  const formatCurrency = (value: number): string => {
    return value.toLocaleString("en-US", { style: "currency", currency: "USD" });
  };

  const getSeverity = (status: string): string => {
    switch (status) {
      case "unqualified":
        return "danger";
      case "qualified":
        return "success";
      case "new":
        return "info";
      case "negotiation":
        return "warn";
      case "renewal":
        return "secondary";
      default:
        return "secondary";
    }
  };

  const chartOptions = {
    maintainAspectRatio: false,
    responsive: true,
    plugins: {
      legend: {
        display: false,
      },
    },
  };
</script>

<template>
  <div class="py-12">
    <h1 class="text-gradient font-display text-4xl font-bold mb-8">UI de LingoQuesto</h1>

    <section class="mb-12">
      <section class="mb-12">
        <div
          class="bg-surface-0 dark:bg-surface-900 p-6 rounded-xl border border-surface-200 dark:border-surface-700 flex flex-col gap-2"
        >
          <h3 class="text-lg font-semibold mb-4">LqDataTable - Componente Reutilizable</h3>
          <LqDataTable
            v-model:items="customers"
            :columns="tableColumns"
            :rows="10"
            :global-filter-fields="['name', 'country.name', 'representative.name', 'balance', 'status']"
            :show-search="false"
            :show-clear-button="false"
            reorderable-columns
            row-reorder
          >
            <!-- Slot para Country con bandera -->
            <template #body-country="{ data }">
              <div class="flex items-center gap-2">
                <img
                  alt="flag"
                  src="https://primefaces.org/cdn/primevue/images/flag/flag_placeholder.png"
                  :class="`flag flag-${data.country.code}`"
                  style="width: 24px"
                />
                <span>{{ data.country.name }}</span>
              </div>
            </template>

            <!-- Slot para Representative con avatar -->
            <template #body-representative="{ data }">
              <div class="flex items-center gap-2">
                <img
                  :alt="data.representative.name"
                  :src="`https://primefaces.org/cdn/primevue/images/avatar/${data.representative.image}`"
                  style="width: 32px"
                />
                <span>{{ data.representative.name }}</span>
              </div>
            </template>

            <!-- Slot para Date -->
            <template #body-date="{ data }">
              {{ formatDate(data.date) }}
            </template>

            <!-- Slot para Balance -->
            <template #body-balance="{ data }">
              {{ formatCurrency(data.balance) }}
            </template>

            <!-- Slot para Status -->
            <template #body-status="{ data }">
              <Tag :value="data.status" :severity="getSeverity(data.status)" />
            </template>

            <!-- Slot para Activity -->
            <template #body-activity="{ data }">
              <ProgressBar :value="data.activity" :show-value="false" style="height: 6px" />
            </template>

            <!-- Slot para Verified -->
            <template #body-verified="{ data }">
              <i
                class="pi"
                :class="{
                  'pi-check-circle text-green-500': data.verified,
                  'pi-times-circle text-red-500': !data.verified,
                }"
              />
            </template>

            <!-- Slot para Gráfica Donut -->
            <template #body-chartData="{ data }">
              <Chart
                type="doughnut"
                :data="data.chartData"
                :options="chartOptions"
                style="width: 100px; height: 100px"
              />
            </template>
          </LqDataTable>
        </div>
      </section>

      <LqCard class="mb-6">
        <h3 class="text-lg font-semibold mb-4">Sidebar</h3>
        <div class="flex flex-wrap gap-4">
          <Button label="Abrir Sidebar (Izquierda)" @click="sidebarVisible = true" />
        </div>
      </LqCard>

      <LqCard class="mb-6">
        <h3 class="text-lg font-semibold mb-4">Botones</h3>
        <div class="flex flex-wrap gap-4">
          <Button label="Primary Button" />
          <Button label="Secondary Button" severity="secondary" />
          <Button label="Outline Button" outlined />
          <Button label="Success Button" severity="success" />
          <Button label="Warning Button" severity="warn" />
          <Button label="Danger Button" severity="danger" />
          <Button label="Help Button" severity="help" />
          <Button label="Contrast Button" severity="contrast" />
        </div>
      </LqCard>

      <LqCard class="mb-6">
        <h3 class="text-lg font-semibold mb-4">Alertas</h3>
        <div class="space-y-4">
          <Message severity="success">Operación completada exitosamente</Message>
          <Message severity="info">Información importante para el usuario</Message>
          <Message severity="warn">Advertencia sobre una acción</Message>
          <Message severity="error">Ha ocurrido un error</Message>
        </div>
      </LqCard>

      <LqCard class="mb-6">
        <h3 class="text-lg font-semibold mb-4">Badges</h3>
        <div class="flex flex-wrap gap-3">
          <Chip label="Apple">
            <template #icon>
              <Icon name="solar:apple-line-duotone" class="mr-2" />
            </template>
          </Chip>
          <Chip label="Facebook">
            <template #icon>
              <Icon name="solar:facebook-line-duotone" class="mr-2" />
            </template>
          </Chip>
          <Chip label="Google">
            <template #icon>
              <Icon name="solar:google-line-duotone" class="mr-2" />
            </template>
          </Chip>
          <Chip label="Microsoft" removable>
            <template #icon>
              <Icon name="solar:microsoft-line-duotone" class="mr-2" />
            </template>
          </Chip>
          <Chip label="GitHub" removable>
            <template #icon>
              <Icon name="solar:github-line-duotone" class="mr-2" />
            </template>
            <template #removeicon="{ removeCallback, keydownCallback }">
              <Icon name="solar:close-circle-line-duotone" @click="removeCallback" @keydown="keydownCallback" />
            </template>
          </Chip>
        </div>
      </LqCard>

      <LqCard class="mb-6">
        <h3 class="text-lg font-semibold mb-4">Cards con Gradientes</h3>
        <div class="grid md:grid-cols-2 gap-4">
          <div class="bg-gradient-primary rounded-lg p-6 text-white">
            <h4 class="text-xl font-bold mb-2">Gradiente Primary</h4>
            <p class="text-primary-100">Ideal para CTAs y elementos destacados</p>
          </div>
          <div class="bg-gradient-secondary rounded-lg p-6 text-white">
            <h4 class="text-xl font-bold mb-2">Gradiente Secondary</h4>
            <p class="text-secondary-100">Perfecto para acentos y elementos especiales</p>
          </div>
        </div>
      </LqCard>

      <!-- Inputs -->
      <LqCard class="card mb-6">
        <h3 class="text-lg font-semibold mb-4">Inputs</h3>
        <div class="space-y-4 max-w-md">
          <input type="text" class="input-base" placeholder="Input con clase personalizada" />
          <input type="email" class="w-full rounded-lg border" placeholder="Email con clases de Tailwind" />
        </div>
      </LqCard>
    </section>

    <!-- Utilidades -->
    <section class="mb-12">
      <h2 class="text-2xl font-bold mb-6">Utilidades</h2>

      <LqCard class="card mb-6">
        <h3 class="text-lg font-semibold mb-4">Texto con Gradiente</h3>
        <h1 class="text-gradient text-4xl font-bold">LingoQuesto</h1>
      </LqCard>

      <LqCard class="card mb-6">
        <h3 class="text-lg font-semibold mb-4">Animaciones</h3>
        <div class="flex flex-wrap gap-4">
          <LqCard class="shadow-soft animate-fade-in w-32 h-32 flex items-center justify-center">Fade In</LqCard>
          <LqCard class="shadow-soft animate-slide-in w-32 h-32 flex items-center justify-center">Slide In</LqCard>
          <LqCard class="shadow-soft animate-bounce-subtle w-32 h-32 flex items-center justify-center">Bounce</LqCard>
        </div>
      </LqCard>
    </section>
  </div>
</template>
