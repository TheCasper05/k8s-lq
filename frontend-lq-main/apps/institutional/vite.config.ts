import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { fileURLToPath, URL } from "node:url";
import { PrimeVueResolver } from "@primevue/auto-import-resolver";
import Components from "unplugin-vue-components/vite";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
    Components({
      resolvers: [PrimeVueResolver()],
    }),
  ],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
      "@lq/ui": fileURLToPath(new URL("../../packages/ui/src", import.meta.url)),
      "@lq/graphql": fileURLToPath(new URL("../../packages/graphql/src", import.meta.url)),
      "@lq/stores": fileURLToPath(new URL("../../packages/stores/src", import.meta.url)),
      "@lq/utils": fileURLToPath(new URL("../../packages/utils/src", import.meta.url)),
    },
  },
  server: {
    port: 3001,
    strictPort: false,
  },
  build: {
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          "vendor-vue": ["vue", "vue-router", "pinia"],
          "vendor-apollo": ["@apollo/client", "graphql"],
          "vendor-ui": ["primevue"],
        },
      },
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
  },
});
