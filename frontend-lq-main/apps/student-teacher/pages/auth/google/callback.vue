<script setup lang="ts">
  // Disable layout for OAuth callback page
  definePageMeta({
    layout: false,
  });

  // Execute immediately - don't wait for onMounted
  if (import.meta.client) {
    // Extract tokens from URL fragment
    const hash = window.location.hash.substring(1);
    const params = new URLSearchParams(hash);

    const accessToken = params.get("access_token");
    const idToken = params.get("id_token");
    const state = params.get("state");
    const error = params.get("error");

    if (window.opener && !window.opener.closed) {
      if (error) {
        window.opener.postMessage(
          {
            type: "GOOGLE_TOKEN",
            error: error,
          },
          window.location.origin,
        );
      } else if (accessToken && idToken) {
        window.opener.postMessage(
          {
            type: "GOOGLE_TOKEN",
            access_token: accessToken,
            id_token: idToken,
            state: state,
          },
          window.location.origin,
        );
      }

      // Give the parent window time to receive the message before closing
      setTimeout(() => {
        window.close();
      }, 100);
    }
  }
</script>

<template>
  <div class="flex h-screen items-center justify-center">
    <ProgressSpinner style="width: 50px; height: 50px" stroke-width="8" />
  </div>
</template>
