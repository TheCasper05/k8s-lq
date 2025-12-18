import { createApp, watch } from "vue";
import { createPinia } from "pinia";
import { createI18n } from "vue-i18n";
import PrimeVue from "primevue/config";
import ToastService from "primevue/toastservice";
import * as Sentry from "@sentry/vue";
import { setAllauthInstance, setApolloInstance } from "@lq/stores";
import { DEFAULT_LOCALE, FALLBACK_LOCALE, loadLocale, setDocumentDir } from "@lq/i18n";

import App from "./App.vue";
import router from "./router";
import { apolloPlugin, apolloClientContainer } from "./plugins/apollo";
import { createAllauthClient } from "@lq/clients";

import { envVars } from "./config/env";

import en from "./locales/en";
import es from "./locales/es";
import ar from "./locales/ar";
import fr from "./locales/fr";
import de from "./locales/de";
import zh from "./locales/zh";

import "./assets/css/main.css";
import { LingoQuestoTheme } from "@lq/composables";

const app = createApp(App);

const pinia = createPinia();
app.use(pinia);

app.use(router);

// Load saved locale or use default
const savedLocale = loadLocale();
const initialLocale = savedLocale || DEFAULT_LOCALE;

const i18n = createI18n({
  legacy: false,
  locale: initialLocale,
  fallbackLocale: FALLBACK_LOCALE,
  messages: {
    en,
    es,
    ar,
    fr,
    de,
    zh,
  },
  globalInjection: true,
});

// Set initial document direction
setDocumentDir(initialLocale);

// Watch for locale changes to update document direction
watch(
  () => i18n.global.locale.value,
  (newLocale) => {
    setDocumentDir(newLocale);
  },
);

app.use(i18n);

app.use(PrimeVue, {
  theme: {
    preset: LingoQuestoTheme,
    options: {
      darkModeSelector: ".dark-mode",
      cssLayer: {
        name: "primevue",
        order: "theme, base, primevue",
      },
    },
  },
  ripple: true,
});

app.use(ToastService);

app.use(apolloPlugin);

const allauth = createAllauthClient({ baseUrl: envVars.VITE_API_BASE_URL, tokenStorage: window.sessionStorage });
setAllauthInstance(allauth);
setApolloInstance(apolloClientContainer.client);

if (envVars.VITE_SENTRY_DSN) {
  Sentry.init({
    app,
    dsn: envVars.VITE_SENTRY_DSN,
    environment: envVars.VITE_ENVIRONMENT,
    integrations: [Sentry.browserTracingIntegration({ router }), Sentry.replayIntegration()],
    tracesSampleRate: 1.0,
    replaysSessionSampleRate: 0.1,
    replaysOnErrorSampleRate: 1.0,
  });
}

app.mount("#app");
