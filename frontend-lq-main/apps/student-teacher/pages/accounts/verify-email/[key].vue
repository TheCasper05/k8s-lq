<script setup lang="ts">
  // This page handles email verification links sent to user's inbox
  // Example URL: /accounts/verify-email/NDA%3A1vRWLH%3Ake7khRssINYQrqb4ZNvuBuInSn5x3WTYLH4WLTqGjOI
  // It re-uses the verify-email component from auth by redirecting to it

  const route = useRoute();
  const router = useRouter();

  // Get the verification key from the route params
  const key = route.params.key as string;

  // Redirect to the auth verify-email page with the key as a param
  // This allows us to reuse the same component and logic
  onMounted(() => {
    router.replace({
      path: "/auth/verify-email",
      query: { key },
    });
  });
</script>

<template>
  <div />
</template>
