// @ts-check
import { createConfigForNuxt } from "@nuxt/eslint-config/flat";

/**
 * Configuración específica para institutional (Vue 3 + Vite)
 *
 * Este archivo extiende la configuración base del monorepo
 * compartiendo la misma configuración base de Nuxt/Vue.
 */
export default createConfigForNuxt({
  features: {
    tooling: true,
  },
})
  .append({
    ignores: ["dist/", "*.config.{js,mjs,cjs,ts}"],
  })
  .append({
    rules: {
      "nuxt/prefer-import-meta": "off",
    },
  });
