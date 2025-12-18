// @ts-check
import { createConfigForNuxt } from "@nuxt/eslint-config/flat";
// @ts-expect-error - no tiene tipos oficiales
import eslintConfigPrettier from "eslint-config-prettier";

/**
 * Configuración base compartida para todo el monorepo
 *
 * Este archivo contiene reglas compartidas que aplican a:
 * - apps/student-teacher (Nuxt)
 * - apps/institutional (Vue + Vite)
 * - packages/* (todos los paquetes)
 *
 * Las apps pueden extender esta configuración con reglas específicas.
 */
export default createConfigForNuxt({
  features: {
    tooling: true,
  },
})
  .append(eslintConfigPrettier)
  .append({
    rules: {
      "eqeqeq": ["error", "always"],
      "no-alert": "error",
      "no-debugger": "error",
      "no-var": "error",
      "prefer-const": "error",
      "prefer-arrow-callback": "warn",
      "no-duplicate-imports": "error",
      "no-template-curly-in-string": "warn",
      "require-await": "warn",
      "no-undef": "off",

      "no-console": [
        "warn",
        {
          allow: ["warn", "error"],
        },
      ],

      "@typescript-eslint/no-explicit-any": "warn",
      "@typescript-eslint/no-unused-vars": [
        "error",
        {
          argsIgnorePattern: "^_",
          varsIgnorePattern: "^_",
          ignoreRestSiblings: true,
        },
      ],
      "@typescript-eslint/explicit-module-boundary-types": "off",
      "@typescript-eslint/consistent-type-imports": ["error", { prefer: "type-imports" }], // Importar tipos con 'type'
      "@typescript-eslint/no-non-null-assertion": "warn", // Evitar uso de ! para non-null

      "vue/multi-word-component-names": "off",
      "vue/no-v-html": "warn", // Advertir sobre v-html por seguridad XSS
      "vue/block-lang": "off",
      "vue/component-api-style": ["error", ["script-setup"]], // Preferir <script setup>
      "vue/component-name-in-template-casing": ["error", "PascalCase"], // Componentes en PascalCase
      "vue/no-unused-refs": "warn", // Detectar refs no usados
      "vue/no-useless-v-bind": "error", // Evitar v-bind innecesarios
      "vue/prefer-true-attribute-shorthand": "warn", // :prop="true" → prop
      "vue/block-order": [
        "error",
        {
          order: ["script", "template", "style"],
        },
      ], // Orden de bloques en componentes .vue
      "vue/attributes-order": [
        "error",
        {
          order: [
            "DEFINITION",
            "LIST_RENDERING",
            "CONDITIONALS",
            "RENDER_MODIFIERS",
            "GLOBAL",
            "UNIQUE",
            "TWO_WAY_BINDING",
            "OTHER_DIRECTIVES",
            "OTHER_ATTR",
            "EVENTS",
            "CONTENT",
          ],
        },
      ],
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
