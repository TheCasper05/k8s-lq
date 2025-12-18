<template>
  <Dropdown
    v-model="selectedLocale"
    :options="availableLocales"
    option-label="name"
    option-value="code"
    class="w-full md:w-14rem"
    @change="handleLocaleChange"
  >
    <template #value="{ value }">
      <div v-if="value" class="flex items-center gap-2">
        <span>{{ getLocaleFlag(value) }}</span>
        <span class="hidden md:inline">{{ getLocaleName(value) }}</span>
      </div>
    </template>
    <template #option="{ option }">
      <div class="flex items-center gap-2">
        <span>{{ option.flag }}</span>
        <span>{{ option.name }}</span>
      </div>
    </template>
  </Dropdown>
</template>

<script setup lang="ts">
  import { ref, computed, watch } from "vue";
  import { useI18n } from "vue-i18n";
  import Dropdown from "primevue/dropdown";
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

  const handleLocaleChange = (event: { value: string }) => {
    const newLocale = event.value;
    locale.value = newLocale;
    selectedLocale.value = newLocale;

    // Persist locale
    saveLocale(newLocale);
    saveLocaleToCookie(newLocale);
  };

  // Sync with i18n locale changes
  watch(locale, (newLocale) => {
    selectedLocale.value = newLocale;
  });
</script>
