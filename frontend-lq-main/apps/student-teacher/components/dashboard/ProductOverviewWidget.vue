<script setup lang="ts">
  import { ref, watch, onMounted } from "vue";
  import { LqDataTable, type LqDataTableColumn } from "@lq/ui";
  import Tag from "primevue/tag";

  const products = ref([
    {
      name: "Laptop Pro",
      category: "Electronics",
      price: 2499,
      status: "In Stock",
    },
    {
      name: "Wireless Mouse",
      category: "Accessories",
      price: 49,
      status: "Low Stock",
    },
    {
      name: "Monitor 4K",
      category: "Electronics",
      price: 699,
      status: "Out of Stock",
    },
    { name: "Keyboard", category: "Accessories", price: 149, status: "In Stock" },
  ]);

  const searchQuery = ref("");
  const loading = ref(false);
  const filteredProducts = ref([]);

  const searchProducts = () => {
    loading.value = true;
    filteredProducts.value = products.value.filter(
      (product) =>
        product.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        product.category.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        product.status.toLowerCase().includes(searchQuery.value.toLowerCase()),
    );
    setTimeout(() => {
      loading.value = false;
    }, 300);
  };

  watch(searchQuery, () => {
    searchProducts();
  });

  onMounted(() => {
    filteredProducts.value = [...products.value];
  });

  const columns: LqDataTableColumn[] = [
    { field: "name", header: "Name", sortable: true },
    { field: "category", header: "Category", sortable: true },
    { field: "price", header: "Price", sortable: true },
    { field: "status", header: "Status" },
  ];
</script>

<template>
  <div
    class="bg-surface-0 dark:bg-surface-900 p-6 rounded-xl border border-surface-200 dark:border-surface-700 flex flex-col gap-4"
  >
    <div class="flex sm:items-center justify-between mb-4 sm:flex-row flex-col gap-2">
      <span class="font-medium text-base">Products Overview</span>
      <IconField class="sm:w-auto w-full">
        <InputIcon>
          <Icon name="solar:magnifier-line-duotone" />
        </InputIcon>
        <InputText
          v-model="searchQuery"
          placeholder="Search products..."
          class="w-full sm:w-64"
          @keyup.enter="searchProducts"
        />
      </IconField>
    </div>
    <div class="flex flex-col gap-2">
      <LqDataTable :data="filteredProducts" :columns="columns" :loading="loading">
        <template #cell-price="{ data }">${{ data.price }}</template>

        <template #cell-status="{ data }">
          <Tag :severity="data.status === 'In Stock' ? 'success' : data.status === 'Low Stock' ? 'warn' : 'danger'">
            {{ data.status }}
          </Tag>
        </template>
      </LqDataTable>
    </div>
  </div>
</template>
