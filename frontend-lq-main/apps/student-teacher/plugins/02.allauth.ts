import { createAllauthClient } from "@lq/clients";
/**
 * Nuxt plugin that provides the allauth client to the app.
 * The HTTP logic now lives in a shared helper so this file only wires it up.
 */
export default defineNuxtPlugin(async () => {
  const config = useRuntimeConfig();
  const baseUrl = (config.public.apiBaseUrl as string) || "http://localhost:8000";
  const tokenStorage = import.meta.client ? window.sessionStorage : null;

  const allauth = createAllauthClient({ baseUrl, tokenStorage });

  // Preload allauth config (kept for parity with previous behavior)
  await allauth.loadConfig();

  return {
    provide: {
      allauth,
    },
  };
});
