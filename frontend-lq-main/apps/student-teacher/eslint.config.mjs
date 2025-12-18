// @ts-check
import { createConfigForNuxt } from "@nuxt/eslint-config/flat";

/**
 * Configuración específica para student-teacher (Nuxt)
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
    ignores: [".nuxt/", ".output/", "*.config.{js,mjs,cjs,ts}"],
  })
  .append({
    rules: {
      "vue/html-self-closing": [
        "error",
        {
          html: {
            void: "always",
            normal: "always",
            component: "always",
          },
        },
      ],
    },
  });
