<script setup lang="ts">
  import { ref, computed, watch } from "vue";
  import { SUPPORTED_LOCALES } from "@lq/i18n/config";
  import Dialog from "primevue/dialog";
  import Button from "primevue/button";
  import InputText from "primevue/inputtext";
  import IconField from "primevue/iconfield";
  import InputIcon from "primevue/inputicon";
  import Select from "primevue/select";
  import ToggleSwitch from "primevue/toggleswitch";
  import Checkbox from "primevue/checkbox";
  import { useAddAssignment } from "~/composables/classes/useAddAssignment";

  const props = defineProps<{
    visible: boolean;
    activeTab?: "modules" | "scenarios";
  }>();

  const emit = defineEmits<{
    "update:visible": [value: boolean];
    "create-complete": [];
  }>();

  const { selectedItems, closeModal, toggleItemSelection, isItemSelected, createAssignments } = useAddAssignment();

  const searchQueryModules = ref("");
  const searchQueryScenarios = ref("");

  // Mock data - TODO: Replace with actual API data
  const modules = ref([
    {
      id: "1",
      name: "SpeakUp A1: Everyday English Con...",
      description: "A practical, conversation-first cours...",
      icon: "solar:book-2-line-duotone",
    },
    {
      id: "2",
      name: "SpeakUp C2 - Relatable Proficient...",
      description: "Engage local in conversational skills...",
      icon: "solar:book-2-line-duotone",
    },
    {
      id: "3",
      name: "SpeakUp A2 - Everyday Essentials",
      description: "A voice-only course that turns...",
      icon: "solar:book-2-line-duotone",
    },
    {
      id: "4",
      name: "SpeakUp A2 - Everyday Essentials",
      description: "A voice-only course that turns...",
      icon: "solar:book-2-line-duotone",
    },
    {
      id: "5",
      name: "SpeakUp B2 - Upper-Intermediat...",
      description: "All the serious B2 goals, but human...",
      icon: "solar:book-2-line-duotone",
    },
    {
      id: "6",
      name: "SpeakUp Pre-A1 Voice-Only Essent...",
      description: "A micro-course for absolute...",
      icon: "solar:book-2-line-duotone",
    },
  ]);

  const scenarios = ref([
    {
      id: "1",
      name: "Describing Weather Using Future Simple",
      description: "You are an english teacher (he Al) so lis...",
      icon: "solar:star-line-duotone",
    },
    {
      id: "2",
      name: "Discussing Last Vacation Adventures",
      description: "I want my student to have a conversation...",
      icon: "solar:star-line-duotone",
    },
    {
      id: "3",
      name: "Describing Weather in Five Cities",
      description: "You are an english teacher (he Al) so lis...",
      icon: "solar:star-line-duotone",
    },
    {
      id: "4",
      name: "Ordering Food with Confidence at a Res...",
      description: "Ordering food at a restaurant",
      icon: "solar:star-line-duotone",
    },
    {
      id: "5",
      name: "Planning Future Vacations Using Future",
      description: "creame una conversación de dos amigos...",
      icon: "solar:star-line-duotone",
    },
    {
      id: "6",
      name: "Ordering Delicious Dishes at a Restaurant",
      description: "Ordering food at a restaurant",
      icon: "solar:star-line-duotone",
    },
  ]);

  const filteredModules = computed(() => {
    if (!searchQueryModules.value.trim()) {
      return modules.value;
    }
    const query = searchQueryModules.value.toLowerCase();
    return modules.value.filter((item) => item.name.toLowerCase().includes(query));
  });

  const filteredScenarios = computed(() => {
    if (!searchQueryScenarios.value.trim()) {
      return scenarios.value;
    }
    const query = searchQueryScenarios.value.toLowerCase();
    return scenarios.value.filter((item) => item.name.toLowerCase().includes(query));
  });

  // Pagination for Modules
  const currentPageModules = ref(1);
  const itemsPerPage = 5;
  const totalPagesModules = computed(() => Math.ceil(filteredModules.value.length / itemsPerPage));
  const paginatedModules = computed(() => {
    const start = (currentPageModules.value - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    return filteredModules.value.slice(start, end);
  });

  // Pagination for Scenarios
  const currentPageScenarios = ref(1);
  const totalPagesScenarios = computed(() => Math.ceil(filteredScenarios.value.length / itemsPerPage));
  const paginatedScenarios = computed(() => {
    const start = (currentPageScenarios.value - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    return filteredScenarios.value.slice(start, end);
  });

  watch(
    () => searchQueryModules.value,
    () => {
      currentPageModules.value = 1;
    },
  );

  watch(
    () => searchQueryScenarios.value,
    () => {
      currentPageScenarios.value = 1;
    },
  );

  const levels = [
    { label: "A1", value: "A1" },
    { label: "A2", value: "A2" },
    { label: "B1", value: "B1" },
    { label: "B2", value: "B2" },
    { label: "C1", value: "C1" },
    { label: "C2", value: "C2" },
  ];

  const availableLanguages = computed(() =>
    SUPPORTED_LOCALES.map((locale) => ({
      code: locale.code,
      name: locale.name,
      flag: locale.flag,
    })),
  );

  const settings = ref({
    language: "en" as string | null,
    level: "B2" as string,
    minimumTime: 15,
    viewTranscription: true,
    viewTranslation: true,
    viewHints: true,
    useNativeLanguage: false,
    viewDescription: true,
  });

  const getLanguageName = (code: string): string => {
    const locale = SUPPORTED_LOCALES.find((l) => l.code === code);
    return locale?.name || code;
  };

  const decreaseTime = () => {
    if (settings.value.minimumTime > 0) {
      settings.value.minimumTime--;
    }
  };

  const increaseTime = () => {
    settings.value.minimumTime++;
  };

  const handleTimeInput = (event: Event) => {
    const target = event.target as HTMLInputElement;
    const value = Number.parseInt(target.value, 10);
    if (!Number.isNaN(value) && value >= 0) {
      settings.value.minimumTime = value;
    } else if (target.value === "") {
      // Allow empty input temporarily while typing
      return;
    } else {
      // Reset to current value if invalid
      target.value = settings.value.minimumTime.toString();
    }
  };

  const handleTimeBlur = (event: Event) => {
    const target = event.target as HTMLInputElement;
    const value = Number.parseInt(target.value, 10);
    if (Number.isNaN(value) || value < 0) {
      settings.value.minimumTime = 0;
      target.value = "0";
    } else {
      settings.value.minimumTime = value;
      target.value = value.toString();
    }
  };

  const handleClose = () => {
    closeModal();
    emit("update:visible", false);
  };

  const handleCreate = async () => {
    await createAssignments();
    emit("update:visible", false);
    emit("create-complete");
  };

  watch(
    () => props.visible,
    (newValue) => {
      if (!newValue) {
        closeModal();
        searchQueryModules.value = "";
        searchQueryScenarios.value = "";
      }
    },
  );
</script>

<template>
  <Dialog
    :visible="visible"
    modal
    :closable="false"
    :draggable="false"
    class="w-full max-w-[95vw] md:max-w-6xl"
    :pt="{
      root: { class: '!rounded-xl' },
      header: { class: '!p-0 !border-0' },
      content: { class: '!p-0' },
    }"
    @update:visible="handleClose"
  >
    <template #header>
      <div
        class="bg-primary-50 dark:bg-primary-900/20 px-4 md:px-6 py-4 md:py-5 border-b border-primary-200 dark:border-primary-800 w-full rounded-t-xl"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="bg-primary-600 dark:bg-primary-500 rounded-lg p-3 flex items-center justify-center">
              <Icon name="solar:document-add-line-duotone" class="text-2xl text-white" />
            </div>
            <div class="flex flex-col">
              <h2 class="text-2xl font-bold text-surface-900 dark:text-surface-100">
                {{ $t("classes.assignments.addModal.title") }}
              </h2>
              <p class="text-sm text-surface-600 dark:text-surface-400 mt-1">
                {{ $t("classes.assignments.addModal.subtitle") }}
                <span class="text-orange-500 font-medium">{{ $t("common.or") }}</span>
                <a
                  href="#"
                  class="text-orange-500 hover:text-orange-600 font-medium uppercase text-xs ml-1"
                  :title="$t('classes.assignments.addModal.createNewActivityTitle')"
                  @click.prevent
                >
                  {{ $t("classes.assignments.addModal.createNewActivity") }}
                </a>
              </p>
            </div>
          </div>
          <button
            class="w-8 h-8 rounded-full bg-white dark:bg-surface-800 flex items-center justify-center hover:bg-surface-100 dark:hover:bg-surface-700 transition-colors"
            @click="handleClose"
          >
            <Icon name="solar:close-circle-line-duotone" class="text-xl text-surface-600 dark:text-surface-400" />
          </button>
        </div>
      </div>
    </template>

    <div class="grid grid-cols-12 gap-4 md:gap-6 p-4 md:p-6">
      <!-- Left Column: Modules (4 columns) -->
      <div class="col-span-12 lg:col-span-4 flex flex-col gap-4">
        <!-- Section Header -->
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <Icon name="solar:list-check-line-duotone" class="text-2xl text-primary-600 dark:text-primary-400" />
            <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-100">
              {{ $t("classes.assignments.addModal.modules") }}
            </h3>
          </div>
          <span
            class="px-3 py-1 rounded-full text-sm font-medium bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300"
          >
            {{ modules.length }} {{ $t("common.items") }}
          </span>
        </div>

        <!-- Search Bar -->
        <IconField class="w-full">
          <InputIcon>
            <Icon name="solar:magnifer-zoom-in-line-duotone" />
          </InputIcon>
          <InputText
            v-model="searchQueryModules"
            :placeholder="$t('classes.assignments.addModal.searchModules')"
            class="w-full"
          />
        </IconField>

        <!-- List of Modules -->
        <div class="overflow-y-auto space-y-2">
          <div
            v-for="item in paginatedModules"
            :key="item.id"
            :class="[
              'flex items-start gap-3 p-4 rounded-lg cursor-pointer transition-colors border',
              isItemSelected(item.id, 'module')
                ? 'bg-primary-50 dark:bg-primary-900/20 border-primary-200 dark:border-primary-800'
                : 'bg-white dark:bg-surface-800 hover:bg-surface-50 dark:hover:bg-surface-700 border-surface-200 dark:border-surface-700',
            ]"
            @click="toggleItemSelection(item.id, 'module')"
          >
            <Checkbox
              :model-value="isItemSelected(item.id, 'module')"
              binary
              class="mt-1"
              @update:model-value="toggleItemSelection(item.id, 'module')"
              @click.stop
            />
            <Icon
              :name="item.icon || 'solar:book-2-line-duotone'"
              class="text-2xl mt-0.5 text-primary-600 dark:text-primary-400"
            />
            <div class="flex-1 min-w-0">
              <h4
                :class="[
                  'text-sm font-semibold mb-1',
                  isItemSelected(item.id, 'module')
                    ? 'text-primary-700 dark:text-primary-300'
                    : 'text-surface-900 dark:text-surface-100',
                ]"
              >
                {{ item.name }}
              </h4>
              <p class="text-xs text-surface-600 dark:text-surface-400 line-clamp-2">
                {{ item.description }}
              </p>
            </div>
          </div>
        </div>

        <!-- Pagination for Modules -->
        <div v-if="totalPagesModules > 1" class="flex items-center justify-center gap-2 pt-2">
          <button
            :disabled="currentPageModules === 1"
            :class="[
              'px-3 py-1 rounded-md text-sm font-medium transition-colors',
              currentPageModules === 1
                ? 'bg-surface-100 dark:bg-surface-800 text-surface-400 dark:text-surface-600 cursor-not-allowed'
                : 'bg-surface-200 dark:bg-surface-700 text-surface-700 dark:text-surface-300 hover:bg-surface-300 dark:hover:bg-surface-600',
            ]"
            @click="currentPageModules--"
          >
            <Icon name="solar:alt-arrow-left-line-duotone" class="text-lg" />
          </button>
          <div class="flex gap-1">
            <button
              v-for="page in totalPagesModules"
              :key="page"
              :class="[
                'px-3 py-1 rounded-md text-sm font-medium transition-colors',
                currentPageModules === page
                  ? 'bg-primary-600 dark:bg-primary-500 text-white'
                  : 'bg-surface-200 dark:bg-surface-700 text-surface-700 dark:text-surface-300 hover:bg-surface-300 dark:hover:bg-surface-600',
              ]"
              @click="currentPageModules = page"
            >
              {{ page }}
            </button>
          </div>
          <button
            :disabled="currentPageModules === totalPagesModules"
            :class="[
              'px-3 py-1 rounded-md text-sm font-medium transition-colors',
              currentPageModules === totalPagesModules
                ? 'bg-surface-100 dark:bg-surface-800 text-surface-400 dark:text-surface-600 cursor-not-allowed'
                : 'bg-surface-200 dark:bg-surface-700 text-surface-700 dark:text-surface-300 hover:bg-surface-300 dark:hover:bg-surface-600',
            ]"
            @click="currentPageModules++"
          >
            <Icon name="solar:alt-arrow-right-line-duotone" class="text-lg" />
          </button>
        </div>

        <!-- Empty State for Modules -->
        <div v-if="filteredModules.length === 0" class="flex flex-col items-center justify-center py-12">
          <Icon name="solar:document-line-duotone" class="text-6xl text-surface-300 dark:text-surface-700 mb-4" />
          <p class="text-lg font-semibold text-surface-600 dark:text-surface-400 mb-2">
            {{ $t("classes.assignments.addModal.noItemsFound") }}
          </p>
          <p class="text-sm text-surface-500 dark:text-surface-500">
            {{ $t("classes.assignments.addModal.noItemsDescription") }}
          </p>
        </div>
      </div>

      <!-- Middle Column: Scenarios (4 columns) -->
      <div class="col-span-12 lg:col-span-4 flex flex-col gap-4">
        <!-- Section Header -->
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <Icon name="solar:star-line-duotone" class="text-2xl text-yellow-500 dark:text-yellow-400" />
            <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-100">
              {{ $t("classes.assignments.addModal.scenarios") }}
            </h3>
          </div>
          <span
            class="px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300"
          >
            {{ scenarios.length }} {{ $t("common.items") }}
          </span>
        </div>

        <!-- Search Bar -->
        <IconField class="w-full">
          <InputIcon>
            <Icon name="solar:magnifer-zoom-in-line-duotone" />
          </InputIcon>
          <InputText
            v-model="searchQueryScenarios"
            :placeholder="$t('classes.assignments.addModal.searchScenarios')"
            class="w-full"
          />
        </IconField>

        <!-- List of Scenarios -->
        <div class="overflow-y-auto space-y-2">
          <div
            v-for="item in paginatedScenarios"
            :key="item.id"
            :class="[
              'flex items-start gap-3 p-4 rounded-lg cursor-pointer transition-colors border',
              isItemSelected(item.id, 'scenario')
                ? 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800'
                : 'bg-white dark:bg-surface-800 hover:bg-surface-50 dark:hover:bg-surface-700 border-surface-200 dark:border-surface-700',
            ]"
            @click="toggleItemSelection(item.id, 'scenario')"
          >
            <Checkbox
              :model-value="isItemSelected(item.id, 'scenario')"
              binary
              class="mt-1"
              @update:model-value="toggleItemSelection(item.id, 'scenario')"
              @click.stop
            />
            <Icon
              :name="item.icon || 'solar:star-line-duotone'"
              class="text-2xl mt-0.5 text-yellow-500 dark:text-yellow-400"
            />
            <div class="flex-1 min-w-0">
              <h4
                :class="[
                  'text-sm font-semibold mb-1',
                  isItemSelected(item.id, 'scenario')
                    ? 'text-yellow-700 dark:text-yellow-300'
                    : 'text-surface-900 dark:text-surface-100',
                ]"
              >
                {{ item.name }}
              </h4>
              <p class="text-xs text-surface-600 dark:text-surface-400 line-clamp-2">
                {{ item.description }}
              </p>
            </div>
          </div>
        </div>

        <!-- Pagination for Scenarios -->
        <div v-if="totalPagesScenarios > 1" class="flex items-center justify-center gap-2 pt-2">
          <button
            :disabled="currentPageScenarios === 1"
            :class="[
              'px-3 py-1 rounded-md text-sm font-medium transition-colors',
              currentPageScenarios === 1
                ? 'bg-surface-100 dark:bg-surface-800 text-surface-400 dark:text-surface-600 cursor-not-allowed'
                : 'bg-surface-200 dark:bg-surface-700 text-surface-700 dark:text-surface-300 hover:bg-surface-300 dark:hover:bg-surface-600',
            ]"
            @click="currentPageScenarios--"
          >
            <Icon name="solar:alt-arrow-left-line-duotone" class="text-lg" />
          </button>
          <div class="flex gap-1">
            <button
              v-for="page in totalPagesScenarios"
              :key="page"
              :class="[
                'px-3 py-1 rounded-md text-sm font-medium transition-colors',
                currentPageScenarios === page
                  ? 'bg-yellow-500 dark:bg-yellow-400 text-white'
                  : 'bg-surface-200 dark:bg-surface-700 text-surface-700 dark:text-surface-300 hover:bg-surface-300 dark:hover:bg-surface-600',
              ]"
              @click="currentPageScenarios = page"
            >
              {{ page }}
            </button>
          </div>
          <button
            :disabled="currentPageScenarios === totalPagesScenarios"
            :class="[
              'px-3 py-1 rounded-md text-sm font-medium transition-colors',
              currentPageScenarios === totalPagesScenarios
                ? 'bg-surface-100 dark:bg-surface-800 text-surface-400 dark:text-surface-600 cursor-not-allowed'
                : 'bg-surface-200 dark:bg-surface-700 text-surface-700 dark:text-surface-300 hover:bg-surface-300 dark:hover:bg-surface-600',
            ]"
            @click="currentPageScenarios++"
          >
            <Icon name="solar:alt-arrow-right-line-duotone" class="text-lg" />
          </button>
        </div>

        <!-- Empty State for Scenarios -->
        <div v-if="filteredScenarios.length === 0" class="flex flex-col items-center justify-center py-12">
          <Icon name="solar:document-line-duotone" class="text-6xl text-surface-300 dark:text-surface-700 mb-4" />
          <p class="text-lg font-semibold text-surface-600 dark:text-surface-400 mb-2">
            {{ $t("classes.assignments.addModal.noItemsFound") }}
          </p>
          <p class="text-sm text-surface-500 dark:text-surface-500">
            {{ $t("classes.assignments.addModal.noItemsDescription") }}
          </p>
        </div>
      </div>

      <!-- Right Column: Evaluation Settings (4 columns) -->
      <div class="col-span-12 lg:col-span-4">
        <div class="sticky top-0 bg-surface-50 dark:bg-surface-800 rounded-lg p-4 space-y-4">
          <!-- Section Header -->
          <div class="flex items-center gap-3 mb-2">
            <Icon name="solar:clock-circle-line-duotone" class="text-2xl text-green-500 dark:text-green-400" />
            <div>
              <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-100">
                {{ $t("classes.assignments.addModal.evaluationSettings") }}
              </h3>
              <p class="text-xs text-surface-600 dark:text-surface-400 mt-0.5">
                {{ $t("classes.assignments.addModal.evaluationSettingsSubtitle") }}
              </p>
            </div>
          </div>

          <!-- Language -->
          <div>
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
              {{ $t("classes.assignments.addModal.language") }}:
            </label>
            <Select
              v-model="settings.language"
              :options="availableLanguages"
              option-label="name"
              option-value="code"
              class="w-full"
            >
              <template #value="slotProps">
                <div v-if="slotProps.value" class="flex items-center gap-2">
                  <Icon name="solar:global-line-duotone" class="text-lg" />
                  <span>{{ getLanguageName(slotProps.value) }}</span>
                </div>
              </template>
              <template #option="slotProps">
                <div class="flex items-center gap-2">
                  <img
                    :src="`https://flagcdn.com/w20/${slotProps.option.flag}.png`"
                    :alt="slotProps.option.name"
                    class="w-5 h-4 object-cover rounded"
                  />
                  <span>{{ slotProps.option.name }}</span>
                </div>
              </template>
            </Select>
          </div>

          <!-- Level -->
          <div>
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
              {{ $t("classes.assignments.addModal.level") }}:
            </label>
            <Select v-model="settings.level" :options="levels" option-label="label" option-value="value" class="w-full">
              <template #value="slotProps">
                <div v-if="slotProps.value" class="flex items-center gap-2">
                  <Icon name="solar:target-line-duotone" class="text-lg" />
                  <span>{{ slotProps.value }}</span>
                </div>
              </template>
              <template #option="slotProps">
                <div class="flex items-center gap-2">
                  <Icon name="solar:target-line-duotone" class="text-lg" />
                  <span>{{ slotProps.option.value }}</span>
                </div>
              </template>
            </Select>
          </div>

          <!-- Minimum Time -->
          <div>
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
              {{ $t("classes.assignments.addModal.minimumTimeMinutes") }}:
            </label>
            <div
              class="flex items-center gap-3 bg-yellow-50 dark:bg-yellow-900/20 border-2 border-yellow-300 dark:border-yellow-700 rounded-xl p-4"
            >
              <button
                class="w-12 h-12 rounded-lg bg-white dark:bg-surface-800 border border-surface-200 dark:border-surface-600 hover:bg-surface-50 dark:hover:bg-surface-700 flex items-center justify-center transition-colors shadow-sm flex-shrink-0"
                @click="decreaseTime"
              >
                <Icon name="solar:minus-circle-line-duotone" class="text-2xl text-surface-700 dark:text-surface-300" />
              </button>
              <div class="flex-1 flex flex-col items-center justify-center py-4">
                <!-- Circular background for number -->
                <div
                  class="w-20 h-20 rounded-full bg-gradient-to-br from-yellow-400 via-yellow-500 to-yellow-600 dark:from-yellow-500 dark:via-yellow-600 dark:to-yellow-700 flex items-center justify-center shadow-lg mb-2"
                >
                  <input
                    type="number"
                    :value="settings.minimumTime"
                    min="0"
                    class="w-full h-full text-4xl font-bold text-white drop-shadow-sm bg-transparent border-0 outline-none text-center [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                    @input="handleTimeInput"
                    @blur="handleTimeBlur"
                  />
                </div>
                <!-- Helper text below -->
                <span class="text-xs text-surface-600 dark:text-surface-400 text-center">
                  {{ $t("classes.assignments.addModal.requiredForCompletion") }}
                </span>
              </div>
              <button
                class="w-12 h-12 rounded-lg bg-white dark:bg-surface-800 border border-surface-200 dark:border-surface-600 hover:bg-surface-50 dark:hover:bg-surface-700 flex items-center justify-center transition-colors shadow-sm flex-shrink-0"
                @click="increaseTime"
              >
                <Icon name="solar:add-circle-line-duotone" class="text-2xl text-surface-700 dark:text-surface-300" />
              </button>
            </div>
          </div>

          <!-- Helper Settings -->
          <div class="space-y-3 pt-2">
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
              {{ $t("classes.assignments.addModal.helperSettings") }}:
            </label>
            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <label class="text-sm text-surface-700 dark:text-surface-300">
                  {{ $t("classes.assignments.addModal.viewTranscription") }}
                </label>
                <ToggleSwitch v-model="settings.viewTranscription" />
              </div>
              <div class="flex items-center justify-between">
                <label class="text-sm text-surface-700 dark:text-surface-300">
                  {{ $t("classes.assignments.addModal.viewSuggestions") }}
                </label>
                <ToggleSwitch v-model="settings.viewHints" />
              </div>
              <div class="flex items-center justify-between">
                <label class="text-sm text-surface-700 dark:text-surface-300">
                  {{ $t("classes.assignments.addModal.viewTranslation") }}
                </label>
                <ToggleSwitch v-model="settings.viewTranslation" />
              </div>
              <div class="flex items-center justify-between">
                <label class="text-sm text-surface-700 dark:text-surface-300">
                  {{ $t("classes.assignments.addModal.useNativeLanguage") }}
                </label>
                <ToggleSwitch v-model="settings.useNativeLanguage" />
              </div>
              <div class="flex items-center justify-between">
                <label class="text-sm text-surface-700 dark:text-surface-300">
                  {{ $t("classes.assignments.addModal.viewDescription") }}
                </label>
                <ToggleSwitch v-model="settings.viewDescription" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div
        class="flex items-center justify-between px-4 md:px-6 py-4 border-t border-surface-200 dark:border-surface-700 w-full"
      >
        <div class="flex items-center gap-2 px-4 py-2 rounded-full bg-green-100 dark:bg-green-900/30">
          <Icon name="solar:check-circle-line-duotone" class="text-lg text-green-600 dark:text-green-400" />
          <span class="text-sm font-medium text-green-700 dark:text-green-300">
            {{ $t("classes.assignments.addModal.usingClassroomDefaults") }}
          </span>
        </div>
        <div class="flex items-center gap-3">
          <Button
            :label="$t('common.cancel')"
            variant="outlined"
            severity="secondary"
            class="flex items-center gap-2"
            @click="handleClose"
          >
            <template #icon>
              <Icon name="solar:close-circle-line-duotone" />
            </template>
          </Button>
          <Button
            :label="`${$t('classes.assignments.addModal.createAssignments')} ${selectedItems.length}`"
            class="bg-primary-600 text-white border-0 flex items-center gap-2"
            :disabled="selectedItems.length === 0"
            @click="handleCreate"
          >
            <template #icon>
              <Icon name="solar:document-add-line-duotone" />
            </template>
          </Button>
        </div>
      </div>
    </template>
  </Dialog>
</template>
