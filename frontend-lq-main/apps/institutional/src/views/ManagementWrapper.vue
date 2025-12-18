<script setup lang="ts">
  import { computed } from "vue";
  import { useRoute, useRouter } from "vue-router";
  import { useI18n } from "vue-i18n";
  import { Icon } from "@iconify/vue";

  const { t } = useI18n();
  const route = useRoute();
  const router = useRouter();

  type TabId = "workspaces" | "licenses" | "invitations";

  const tabs = [
    {
      id: "workspaces" as TabId,
      label: t("management.tabs.workspaces"),
      icon: "solar:buildings-line-duotone",
      route: "/management/workspaces",
    },
    {
      id: "licenses" as TabId,
      label: t("management.tabs.licenses"),
      icon: "solar:key-line-duotone",
      route: "/management/licenses",
    },
    {
      id: "invitations" as TabId,
      label: t("management.tabs.invitations"),
      icon: "solar:letter-line-duotone",
      route: "/management/invitations",
    },
  ];

  const activeTab = computed(() => {
    const currentPath = route.path;
    if (currentPath.includes("/workspaces")) return "workspaces";
    if (currentPath.includes("/licenses")) return "licenses";
    if (currentPath.includes("/invitations")) return "invitations";
    return "invitations"; // default
  });

  const handleTabClick = (tab: (typeof tabs)[number]) => {
    router.push(tab.route);
  };
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Tabs Navigation -->
    <div class="bg-gray-50 pt-6 pb-4">
      <div class="flex px-6">
        <div class="bg-[#F8FAFC] rounded-lg border border-gray-200 p-0 flex gap-1">
          <button
            v-for="(tab, idx) in tabs"
            :key="tab.id"
            :class="[
              'flex items-center gap-2 px-6 py-3 font-medium text-sm transition-all relative flex-1 justify-center',
              idx === 0
                ? 'rounded-s-lg rounded-e-none'
                : idx === tabs.length - 1
                  ? 'rounded-e-lg rounded-s-none'
                  : 'rounded-none',
              activeTab === tab.id
                ? 'text-[#7008E7] bg-[#ebeef2]'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50',
            ]"
            @click="handleTabClick(tab)"
          >
            <Icon :icon="tab.icon" />
            <span>{{ tab.label }}</span>
            <!-- Active indicator -->
            <span
              v-if="activeTab === tab.id"
              class="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-full h-0.5 bg-[#7008E7] rounded-full"
            />
          </button>
        </div>
      </div>
    </div>

    <!-- Dynamic Content -->
    <div>
      <router-view />
    </div>
  </div>
</template>
