<script setup lang="ts" generic="T extends object">
  import { computed } from "vue";
  import DataTable from "primevue/datatable";
  import Column from "primevue/column";

  export interface LqDataTableColumn {
    field: string;
    header: string;
    class?: string;
    sortable?: boolean;
  }

  const props = withDefaults(
    defineProps<{
      /**
       * Array of data to display
       */
      data: T[];
      /**
       * Column definitions
       */
      columns: LqDataTableColumn[];
      /**
       * Enable scrollable mode
       */
      scrollable?: boolean;
      /**
       * Loading state
       */
      loading?: boolean;
      /**
       * Empty message when no data
       */
      emptyMessage?: string;
      /**
       * Custom PT (PassThrough) configuration
       */
      pt?: Record<string, unknown>;

      /**
       * Optional rowClass passthrough for PrimeVue DataTable
       */
      rowClass?: (data: T) => string | Record<string, boolean> | (string | Record<string, boolean>)[];

      /**
       * Render without the default outer container styles.
       * Useful when embedding inside another card/layout.
       */
      embedded?: boolean;
    }>(),
    {
      scrollable: true,
      loading: false,
      emptyMessage: "No data available",
      pt: undefined,
      rowClass: undefined,
      embedded: false,
    },
  );

  // Default PT configuration matching AssignmentsList
  const defaultPT = {
    root: { class: "border-0" },
    thead: { class: "rounded-xl overflow-hidden" },
    column: {
      headerCell: {
        class:
          "bg-surface-50 dark:bg-surface-800 px-4 py-3 text-sm font-semibold text-surface-700 dark:text-surface-300 border-b border-surface-200 dark:border-surface-700 first:rounded-tl-2xl last:rounded-tr-2xl last:text-right",
      },
    },
    bodyRow: {
      class:
        "hover:bg-surface-50 dark:hover:bg-surface-800/50 transition-colors [&.expanded-row]:bg-surface-50/50 [&.expanded-row]:dark:bg-surface-800/30",
    },
    bodyCell: { class: "py-4 px-4 border-b border-surface-100 dark:border-surface-800 align-middle" },
  };

  const tablePT = computed(() => {
    return props.pt || defaultPT;
  });
</script>

<template>
  <div
    :class="
      embedded
        ? undefined
        : 'flex flex-col bg-surface-0 dark:bg-surface-900 rounded-2xl border border-surface-200 dark:border-surface-700 shadow-sm overflow-hidden h-full'
    "
  >
    <!-- Header slot (optional) -->
    <div v-if="$slots.header" class="flex items-center justify-between p-6">
      <slot name="header" />
    </div>

    <!-- Table -->
    <div class="flex-1" :class="{ 'px-5': $slots.header && !embedded }">
      <DataTable
        :value="data"
        :scrollable="scrollable"
        :loading="loading"
        :row-class="rowClass"
        class="w-full"
        :pt="tablePT"
      >
        <template v-if="loading" #empty>
          <div class="flex items-center justify-center py-8">
            <div class="text-center">
              <Icon
                name="solar:refresh-line-duotone"
                class="text-4xl text-primary-600 dark:text-primary-400 animate-spin mb-4"
              />
              <p class="text-surface-600 dark:text-surface-400">Loading...</p>
            </div>
          </div>
        </template>

        <template v-else #empty>
          <div class="text-center py-8 text-surface-500 dark:text-surface-400">
            {{ emptyMessage }}
          </div>
        </template>

        <!-- Dynamic columns -->
        <Column
          v-for="column in columns"
          :key="column.field"
          :field="column.field"
          :header="column.header"
          :class="column.class"
          :sortable="column.sortable"
        >
          <template #body="slotProps">
            <slot :name="`cell-${column.field}`" :data="slotProps.data" :value="(slotProps.data as any)[column.field]">
              {{ (slotProps.data as any)[column.field] }}
            </slot>
          </template>
        </Column>

        <!-- Actions column (optional) -->
        <Column v-if="$slots.actions" header="Actions" class="w-48 text-right">
          <template #body="slotProps">
            <slot name="actions" :data="slotProps.data" />
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Footer slot (optional) -->
    <div v-if="$slots.footer" class="border-t border-surface-200 dark:border-surface-700 p-6">
      <slot name="footer" />
    </div>
  </div>
</template>
