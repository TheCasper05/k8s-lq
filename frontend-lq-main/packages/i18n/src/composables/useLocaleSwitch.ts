/**
 * Composable for switching locales with persistence and RTL support
 */

import { ref, computed } from "vue";
import { SUPPORTED_LOCALES, DEFAULT_LOCALE, type SupportedLocale } from "../config";
import { setDocumentDir } from "../utils/rtl";
import { saveLocale, saveLocaleToCookie } from "../utils/persistence";

export function useLocaleSwitch() {
  const currentLocale = ref<SupportedLocale>(DEFAULT_LOCALE);

  const availableLocales = computed(() =>
    SUPPORTED_LOCALES.map((locale) => ({
      code: locale.code,
      name: locale.name,
      flag: locale.flag,
      dir: locale.dir,
    })),
  );

  const switchLocale = (newLocale: SupportedLocale) => {
    const isSupported = SUPPORTED_LOCALES.some((l) => l.code === newLocale);

    if (isSupported) {
      currentLocale.value = newLocale;
      setDocumentDir(newLocale);
      saveLocale(newLocale);
      saveLocaleToCookie(newLocale);
    } else {
      console.warn(`Locale "${newLocale}" is not supported`);
    }
  };

  const getCurrentLocaleConfig = () => {
    return SUPPORTED_LOCALES.find((l) => l.code === currentLocale.value);
  };

  return {
    currentLocale,
    availableLocales,
    switchLocale,
    getCurrentLocaleConfig,
  };
}
