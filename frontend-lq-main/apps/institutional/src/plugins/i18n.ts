import { createI18n as createVueI18n } from "vue-i18n";
import en from "../locales/en";
import es from "../locales/es";

export function createI18n() {
  return createVueI18n({
    legacy: false,
    locale: "en",
    fallbackLocale: "en",
    messages: {
      en,
      es,
    },
    globalInjection: true,
  });
}
