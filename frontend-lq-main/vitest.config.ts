import { defineConfig } from "vitest/config";
import vue from "@vitejs/plugin-vue";
import { fileURLToPath } from "node:url";

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: "jsdom",
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      exclude: ["node_modules/", "dist/", ".nuxt/", ".output/", "**/*.config.*", "**/*.d.ts", "**/generated/**"],
    },
  },
  resolve: {
    alias: {
      "@lq/ui": fileURLToPath(new URL("./packages/ui/src", import.meta.url)),
      "@lq/graphql": fileURLToPath(new URL("./packages/graphql/src", import.meta.url)),
      "@lq/stores": fileURLToPath(new URL("./packages/stores/src", import.meta.url)),
      "@lq/utils": fileURLToPath(new URL("./packages/utils/src", import.meta.url)),
    },
  },
});
