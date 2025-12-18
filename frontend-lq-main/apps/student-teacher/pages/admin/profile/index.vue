<script setup lang="ts">
  import ProfilePage from "~/components/pages/ProfilePage.vue";
  import { useProfilePage } from "~/composables/admin/profile/useProfilePage";

  definePageMeta({
    layout: "app",
  });

  useProfilePage();
</script>

<template>
  <ProfilePage />
</template>
