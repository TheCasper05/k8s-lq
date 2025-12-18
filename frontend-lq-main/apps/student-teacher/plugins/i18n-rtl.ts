import { setDocumentDir } from "@lq/i18n";

export default defineNuxtPlugin((nuxtApp) => {
  // Only run on client side
  if (import.meta.client) {
    const i18n = nuxtApp.$i18n as unknown as { locale: { value: string } };

    // Set initial direction
    setDocumentDir(i18n.locale.value);

    // Watch for locale changes using Vue's watch
    nuxtApp.hook("i18n:localeSwitched", ({ newLocale }) => {
      setDocumentDir(newLocale);
    });
  }
});
