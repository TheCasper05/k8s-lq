import { LingoQuestoTheme } from "@lq/composables";
import PrimeUI from "tailwindcss-primeui";
import { envVars } from "./utils/env";
import { defineNuxtConfig } from "nuxt/config";

/**
 * PrimeVue plugin for Nuxt
 * Registers global PrimeVue components
 */
export default defineNuxtConfig({
  ssr: true,  // Enable SSR for Docker deployment
  modules: [
    "@nuxtjs/tailwindcss",
    "@nuxtjs/tailwindcss",
    "@primevue/nuxt-module",
    "@nuxt/icon",
    "@pinia/nuxt",
    "@nuxtjs/i18n",
    "@vueuse/nuxt",
    "@sentry/nuxt/module",
  ],
  devtools: { enabled: true },

  // App head configuration
  app: {
    // Page transitions (handled dynamically by middleware)
    pageTransition: {
      name: "page-forward", // Default, will be overridden by middleware
      mode: "out-in",
    },
    // Layout transitions (for auth -> default layout changes)
    layoutTransition: {
      name: "layout",
      mode: "out-in",
    },
    head: {
      title: "LingoQuesto - Student & Teacher",
      meta: [
        { charset: "utf-8" },
        { name: "viewport", content: "width=device-width, initial-scale=1" },
        {
          hid: "description",
          name: "description",
          content: "LingoQuesto learning platform for students and teachers",
        },
      ],
      link: [{ rel: "icon", type: "image/x-icon", href: "/favicon.ico" }],
      style: [
        {
          children: `
            /* Prevent FOUC - apply dark background immediately */
            html.p-dark { background-color: #020617; }
            html.p-dark body { background-color: #020617; }
          `,
        },
      ],
      script: [
        {
          children: `
            // Apply theme IMMEDIATELY before any rendering
            (function() {
              try {
                var config = localStorage.getItem('lq-theme-config');
                if (config) {
                  var parsed = JSON.parse(config);
                  if (parsed.darkMode) {
                    document.documentElement.classList.add('p-dark');
                  }
                }
              } catch (e) {}
            })();
          `,
        },
      ],
    },
  },

  // CSS configuration
  css: ["~/assets/css/main.css"],

  // Runtime config for environment variables
  runtimeConfig: {
    public: {
      apiBaseUrl: envVars?.NUXT_PUBLIC_API_BASE_URL ?? "",
      graphqlEndpoint: envVars?.NUXT_PUBLIC_GRAPHQL_ENDPOINT ?? "",
      graphqlWsEndpoint: envVars?.NUXT_PUBLIC_GRAPHQL_WS_ENDPOINT ?? "",
      sentryDsn: envVars?.NUXT_PUBLIC_SENTRY_DSN ?? "",
      sentryEnvironment: envVars?.NUXT_PUBLIC_SENTRY_ENVIRONMENT ?? "",
      appEnv: envVars?.NODE_ENV ?? "",
      bypassOnboarding: envVars?.NUXT_PUBLIC_BYPASS_ONBOARDING === "true",
    },
  },

  // Build configuration
  build: {
    transpile: ["primevue", "@vee-validate/zod"],
  },
  compatibilityDate: "2024-07-01",

  // Security headers
  nitro: {
    preset: "node-server",
    routeRules: {
      "/**": {
        headers: {
          "X-Frame-Options": "SAMEORIGIN",
          "X-Content-Type-Options": "nosniff",
          "X-XSS-Protection": "1; mode=block",
          "Referrer-Policy": "strict-origin-when-cross-origin",
          "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
        },
      },
    },
  },

  // TypeScript configuration
  typescript: {
    strict: false,
    typeCheck: false,
    shim: false,
  },
  // Force dev server port
  server: {
    port: 3001,
  },

  // Vue configuration - Enable Vue 3.5 features
  vue: {
    propsDestructure: true,
  },

  // i18n configuration
  i18n: {
    locales: [
      {
        code: "en",
        language: "en-US",
        name: "English",
        file: "en.ts",
      },
      {
        code: "es",
        language: "es-ES",
        name: "Español",
        file: "es.ts",
      },
      {
        code: "pt",
        language: "pt-BR",
        name: "Português",
        file: "pt.ts",
      },
      {
        code: "ar",
        language: "ar-SA",
        name: "العربية",
        dir: "rtl",
        file: "ar.ts",
      },
      {
        code: "fr",
        language: "fr-FR",
        name: "Français",
        file: "fr.ts",
      },
      {
        code: "de",
        language: "de-DE",
        name: "Deutsch",
        file: "de.ts",
      },
      {
        code: "zh",
        language: "zh-CN",
        name: "中文",
        file: "zh.ts",
      },
      {
        code: "it",
        language: "it-IT",
        name: "Italiano",
        file: "it.ts",
      },
    ],
    lazy: true,
    langDir: "locales",
    defaultLocale: "en",
    strategy: "no_prefix",
    detectBrowserLanguage: {
      useCookie: true,
      cookieKey: "lq_locale",
      redirectOn: "root",
    },
  },

  primevue: {
    options: {
      theme: {
        preset: LingoQuestoTheme,
        options: {
          // cssLayer: {
          //   name: 'primevue',
          //   order: 'tailwind-base, primevue, tailwind-utilities',
          // },
          darkModeSelector: ".p-dark",
        },
      },
      ripple: true,
    },
    autoImport: true,
  },

  // Sentry configuration
  sentry: {
    sourceMapsUploadOptions: {
      org: process.env.SENTRY_ORG,
      project: process.env.SENTRY_PROJECT,
    },
  },

  tailwindcss: {
    config: {
      content: [
        "./components/**/*.{vue,js,ts}",
        "./layouts/**/*.{vue,js,ts}",
        "./pages/**/*.{vue,js,ts}",
        "./app.vue",
        // Scan shared packages
        "../../packages/ui/src/**/*.{vue,js,ts}",
        "../../packages/theme/**/*.{vue,js,ts}",
      ],
      plugins: [PrimeUI],
      darkMode: ["class", ".p-dark"],
    },
  },
});
