<script setup lang="ts">
  import { LqSelect } from "@lq/ui";
  import { SUPPORTED_LOCALES } from "@lq/i18n/config";
  import { saveLocale, saveLocaleToCookie } from "@lq/i18n";

  const { locale } = useI18n();
  const selectedLocale = ref(locale.value);

  const availableLocales = computed(() =>
    SUPPORTED_LOCALES.map((l) => ({
      code: l.code,
      name: l.name,
      flag: l.flag,
      dir: l.dir,
    })),
  );

  const getLocaleFlag = (code: string) => {
    return SUPPORTED_LOCALES.find((l) => l.code === code)?.flag || "🌐";
  };

  const getLocaleName = (code: string) => {
    return SUPPORTED_LOCALES.find((l) => l.code === code)?.name || code;
  };

  watch(selectedLocale, async (newLocale) => {
    if (newLocale === locale.value) return;

    const nuxtApp = useNuxtApp();
    const i18n = nuxtApp.$i18n as unknown as {
      locale: { value: string };
      setLocale?: (value: string) => Promise<void> | void;
    };

    if (typeof i18n.setLocale === "function") {
      await i18n.setLocale(newLocale);
    } else {
      locale.value = newLocale;
    }

    // Persist locale
    saveLocale(newLocale);
    saveLocaleToCookie(newLocale);
  });

  // Sync with i18n locale changes
  watch(locale, (newLocale) => {
    selectedLocale.value = newLocale;
  });
</script>

<template>
  <LqSelect
    v-model="selectedLocale"
    :options="availableLocales"
    option-label="name"
    option-value="code"
    class="w-full md:w-14rem"
  >
    <template #value="{ value }">
      <div v-if="value" class="flex items-center gap-2">
        <Icon :name="getLocaleFlag(value)" class="text-lg" />
        <span class="hidden md:inline">{{ getLocaleName(value) }}</span>
      </div>
    </template>
    <template #option="{ option }">
      <div class="flex items-center gap-2">
        <Icon :name="option.flag" class="text-lg" />
        <span>{{ option.name }}</span>
      </div>
    </template>
  </LqSelect>
</template>
