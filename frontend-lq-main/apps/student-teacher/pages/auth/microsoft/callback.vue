<script setup lang="ts">
  // Disable layout for OAuth callback page
  definePageMeta({
    layout: false,
  });

  // This page handles the OAuth callback for Microsoft
  // It extracts the token from the URL fragment and sends it to the parent window

  // Execute immediately - don't wait for onMounted
  if (import.meta.client) {
    // Extract token from URL fragment
    const hash = window.location.hash.substring(1); // Remove #
    const params = new URLSearchParams(hash);

    const accessToken = params.get("access_token");
    const state = params.get("state");
    const error = params.get("error");

    if (window.opener && !window.opener.closed) {
      if (error) {
        // Send error to parent window
        window.opener.postMessage(
          {
            type: "MSAL_ERROR",
            error: error,
            error_description: params.get("error_description"),
          },
          window.location.origin,
        );
      } else if (accessToken && state) {
        // Send token and state to parent window
        window.opener.postMessage(
          {
            type: "MSAL_TOKEN",
            access_token: accessToken,
            state: state,
          },
          window.location.origin,
        );
      } else {
        // Send generic error
        window.opener.postMessage(
          {
            type: "MSAL_ERROR",
            error: "no_token",
            error_description: "No access token received",
          },
          window.location.origin,
        );
      }

      // Close the popup after a short delay
      setTimeout(() => {
        window.close();
      }, 100);
    }
  }
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-surface-900">
    <div class="text-center">
      <div class="mb-4">
        <ProgressSpinner style="width: 50px; height: 50px" stroke-width="8" />
      </div>
      <h2 class="text-xl font-semibold text-gray-700 dark:text-surface-200 mb-2">Completing sign in...</h2>
      <p class="text-gray-600 dark:text-surface-400">Please wait while we complete your authentication.</p>
    </div>
  </div>
</template>
