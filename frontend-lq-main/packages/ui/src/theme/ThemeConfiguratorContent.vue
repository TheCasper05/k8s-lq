<script setup lang="ts">
  import { useLayout, type MenuType, type MenuTypeOption } from "@lq/composables";
  import ColorPicker from "./ColorPicker.vue";
  import { computed } from "vue";

  defineOptions({
    name: "ThemeConfiguratorContent",
  });

  interface Props {
    /**
     * Show primary color picker
     * @default true
     */
    showPrimary?: boolean;
    /**
     * Show surface color picker
     * @default true
     */
    showSurface?: boolean;
    /**
     * Show menu type selector
     * @default true
     */
    showMenuType?: boolean;
    /**
     * Additional CSS classes for the container
     * @default ''
     */
    class?: string;
    /**
     * Label for primary color picker
     * @default 'Primary Color'
     */
    primaryColorLabel?: string;
    /**
     * Label for surface color picker
     * @default 'Surface Color'
     */
    surfaceColorLabel?: string;
    /**
     * Label for menu type selector
     * @default 'Menu Type'
     */
    menuTypeLabel?: string;
    /**
     * Text for locked menu type
     * @default 'Locked'
     */
    lockedText?: string;
    /**
     * Menu type options with labels and descriptions
     */
    menuTypeOptions?: Array<{
      value: MenuType;
      label: string;
      description: string;
    }>;
  }

  const props = withDefaults(defineProps<Props>(), {
    showPrimary: true,
    showSurface: true,
    showMenuType: true,
    class: "",
    primaryColorLabel: "Primary Color",
    surfaceColorLabel: "Surface Color",
    menuTypeLabel: "Menu Type",
    lockedText: "Locked",
    menuTypeOptions: undefined,
  });

  const { primaryColors, surfaces, primary, surface, isDarkMode, menuType, menuTypeLocked, setMenuType, updateColors } =
    useLayout();

  const handlePrimaryChange = (colorName: string) => {
    updateColors("primary", colorName);
  };

  const handleSurfaceChange = (colorName: string) => {
    updateColors("surface", colorName);
  };

  const isSurfaceSelected = (colorName: string): boolean => {
    if (surface.value) {
      return surface.value === colorName;
    }
    return isDarkMode.value ? colorName === "zinc" : colorName === "slate";
  };

  // Menu type options with icons
  const menuTypeIcons: Record<MenuType, string> = {
    "icon-only": "pi pi-bars",
    "grouped": "pi pi-list",
    "simple": "pi pi-align-justify",
    "static": "pi pi-th-large",
  };

  // Default menu type options
  const defaultMenuTypes: MenuTypeOption[] = [
    {
      value: "icon-only",
      label: "Icon Only",
      description: "Compact sidebar",
      icon: "pi pi-bars",
    },
    {
      value: "grouped",
      label: "Grouped",
      description: "Organized sections",
      icon: "pi pi-list",
    },
    {
      value: "simple",
      label: "Simple",
      description: "Flat list",
      icon: "pi pi-align-justify",
    },
    {
      value: "static",
      label: "Static",
      description: "Full menu with sections",
      icon: "pi pi-th-large",
    },
  ];

  // Use provided menu type options or defaults
  const menuTypes = computed<MenuTypeOption[]>(() => {
    if (props.menuTypeOptions) {
      return props.menuTypeOptions.map((option) => ({
        ...option,
        icon: menuTypeIcons[option.value],
      }));
    }
    return defaultMenuTypes;
  });

  const isMenuTypeSelected = (type: MenuType): boolean => {
    return menuType.value === type;
  };

  const handleMenuTypeChange = (type: MenuType) => {
    setMenuType(type);
  };
</script>

<template>
  <div class="flex flex-col gap-6 p-1">
    <ClientOnly>
      <div v-if="showPrimary">
        <ColorPicker
          :model-value="primary"
          :colors="primaryColors"
          :label="primaryColorLabel"
          @change="handlePrimaryChange"
        />
      </div>

      <div v-if="showSurface">
        <ColorPicker
          :model-value="surface"
          :colors="surfaces"
          :label="surfaceColorLabel"
          :is-selected="isSurfaceSelected"
          @change="handleSurfaceChange"
        />
      </div>
    </ClientOnly>

    <ClientOnly>
      <div v-if="showMenuType" class="flex flex-col gap-3">
        <div class="flex items-center justify-between">
          <label class="text-sm font-semibold text-surface-700 dark:text-surface-200">{{ menuTypeLabel }}</label>
          <span v-if="menuTypeLocked" class="flex items-center gap-1 text-xs text-primary-600 dark:text-primary-400">
            <i class="pi pi-lock text-xs" />
            {{ lockedText }}
          </span>
        </div>

        <div class="flex flex-col gap-2">
          <button
            v-for="type in menuTypes"
            :key="type.value"
            :class="[
              'flex items-center gap-3 p-3 rounded-lg border-2 transition-all text-left',
              isMenuTypeSelected(type.value)
                ? 'border-primary bg-primary-50 dark:bg-primary-500/10'
                : 'border-surface-200 dark:border-surface-700 hover:border-primary/50',
              menuTypeLocked ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer',
            ]"
            type="button"
            :disabled="menuTypeLocked"
            @click="handleMenuTypeChange(type.value)"
          >
            <i :class="[type.icon, 'text-lg']" />
            <div class="flex flex-col flex-1">
              <span class="text-sm font-medium text-surface-900 dark:text-surface-0">{{ type.label }}</span>
              <span class="text-xs text-surface-500 dark:text-surface-400">{{ type.description }}</span>
            </div>
            <i v-if="isMenuTypeSelected(type.value)" class="pi pi-check text-primary" />
          </button>
        </div>
      </div>
    </ClientOnly>
  </div>
</template>
