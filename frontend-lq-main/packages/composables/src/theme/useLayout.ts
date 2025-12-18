import { updatePrimaryPalette, updateSurfacePalette } from "@primeuix/themes";
import { computed, onMounted, ref, watch } from "vue";
import { useBreakpoints, breakpointsTailwind } from "@vueuse/core";
import type { AppState, ColorType, MenuType, PrimaryColor, SurfaceColor, UseLayoutReturn } from "./types";
import { primaryColors as colors, surfaces as surfaceColors } from "./colors";

/* Store the user's preferred menu type (desktop configuration) */
let userPreferredMenuType: MenuType = "simple";

/* Track if we're currently in responsive mode */
let isResponsiveMode = false;

/**
 * Get default menu type based on user role
 * Teachers get 'static' by default, others get 'simple'
 */
const getDefaultMenuType = (role?: string | null): MenuType => {
  if (role === "teacher") {
    return "static";
  }
  return "simple";
};

/**
 * Get default state for the theme configuration
 * @param role - User role to determine default menu type
 */
const getDefaultState = (role?: string | null): AppState => {
  return {
    primary: "default",
    surface: null,
    darkMode: false,
    menuType: getDefaultMenuType(role),
    menuTypeLocked: false,
  };
};

/* Read initial state SYNCHRONOUSLY from localStorage */
const readInitialState = (role?: string | null): AppState => {
  // Check if we're in the browser
  if (typeof window === "undefined" || typeof localStorage === "undefined") {
    return getDefaultState(role);
  }

  try {
    const saved = localStorage.getItem("lq-theme-config");
    if (saved) {
      const parsed = JSON.parse(saved);
      // If there's saved config, use it (respecting user's previous choice)
      return { ...getDefaultState(role), ...parsed };
    }
  } catch (error) {
    console.warn("Failed to read initial state:", error);
  }

  // No saved config - use role-based defaults
  return getDefaultState(role);
};

/* Create reactive state with initial value from localStorage */
const appState = ref<AppState>(readInitialState());

const primaryColors = ref<PrimaryColor[]>(colors);
const surfaces = ref<SurfaceColor[]>(surfaceColors);

let initialized = false;

/**
 * The `useLayout` function in TypeScript is used to manage theme layout settings, including setting
 * primary and surface colors, toggling dark mode, and updating colors based on a color type.
 * @param role - Optional user role to determine default menu type (e.g., 'teacher', 'student', 'admin')
 * @returns The `useLayout` function returns an object with the following properties and methods:
 */
export function useLayout(role?: string | null): UseLayoutReturn {
  // Initialize state with role-based defaults if not already initialized
  if (!initialized && role) {
    appState.value = readInitialState(role);
  }
  /**
   * The functions setPrimary, setSurface, and setDarkMode update values in the appState object and
   * toggle a dark mode class on the document element if applicable.
   * @param {string} value - The `value` parameter in the functions `setPrimary`, `setSurface`, and
   * `setDarkMode` represents the new value that you want to set for the corresponding property in the
   * `appState` object. It can be a string for `setPrimary` and `setSurface`, and a
   */
  function setPrimary(value: string): void {
    appState.value.primary = value;
  }

  function setSurface(value: string): void {
    appState.value.surface = value;
  }

  function setMenuType(value: MenuType): void {
    if (!appState.value.menuTypeLocked) {
      appState.value.menuType = value;
      // Update user preferred menu type when manually changed
      if (!isResponsiveMode) {
        userPreferredMenuType = value;
      }
    }
  }

  /**
   * Apply responsive menu type based on screen size
   * Uses VueUse breakpoints for better reactivity
   */
  function applyResponsiveMenuType(isSmaller: boolean): void {
    if (appState.value.menuTypeLocked) return;

    if (isSmaller && !isResponsiveMode) {
      // Switching to mobile/tablet: save current menu type and switch to icon-only
      userPreferredMenuType = appState.value.menuType;
      isResponsiveMode = true;
      appState.value.menuType = "icon-only";
    } else if (!isSmaller && isResponsiveMode) {
      // Switching to desktop: restore user's preferred menu type
      isResponsiveMode = false;
      appState.value.menuType = userPreferredMenuType;
    }
  }

  function toggleMenuTypeLock(): void {
    appState.value.menuTypeLocked = !appState.value.menuTypeLocked;
  }

  function setDarkMode(value: boolean): void {
    appState.value.darkMode = value;
    if (typeof document !== "undefined") {
      if (value) {
        document.documentElement.classList.add("p-dark");
      } else {
        document.documentElement.classList.remove("p-dark");
      }
    }
  }

  /**
   * The above functions toggle dark mode and update colors in a TypeScript application, including
   * setting CSS variables for PrimeVue and Tailwind.
   */
  function toggleDarkMode(): void {
    appState.value.darkMode = !appState.value.darkMode;
    if (typeof document !== "undefined") {
      document.documentElement.classList.toggle("p-dark");
    }
  }

  /**
   * The function `updateColors` updates CSS variables for color palettes based on the type of color
   * (primary or surface) and the color name provided.
   * @param {ColorType} type - The `type` parameter in the `updateColors` function represents the type
   * of color being updated. It can have two possible values: "primary" or "surface".
   * @param {string} colorName - The `colorName` parameter represents the name of the color you want to
   * update. It could be a specific shade or tone of a color, such as "blue-500" or "green-700". This
   * parameter is used to identify the specific color palette you want to apply to your UI elements
   */
  function updateColors(type: ColorType, colorName: string): void {
    if (type === "primary") {
      setPrimary(colorName);

      if (typeof document !== "undefined") {
        const color = primaryColors.value.find((c) => c.name === colorName);
        if (color) {
          const root = document.documentElement;

          // Aplicar CSS variables para PrimeVue (--p-primary-*) y Tailwind (--primary-*)
          Object.entries(color.palette).forEach(([shade, value]) => {
            // Variables para PrimeVue
            root.style.setProperty(`--p-primary-${shade}`, value as string);
            // Variables para Tailwind (opcional, si usas clases como bg-primary-500)
            root.style.setProperty(`--primary-${shade}`, value as string);
          });

          // call a updatePrimaryPalette if needed as well apply the palette to PrimeVue theme
          updatePrimaryPalette(color.palette);
        }
      }
    } else if (type === "surface") {
      setSurface(colorName);

      if (typeof document !== "undefined") {
        const surfaceColor = surfaces.value.find((s) => s.name === colorName);
        if (surfaceColor) {
          const root = document.documentElement;

          // Aplicar CSS variables para PrimeVue (--p-surface-*) y Tailwind (--surface-*)
          Object.entries(surfaceColor.palette).forEach(([shade, value]) => {
            // Vars for PrimeVue
            root.style.setProperty(`--p-surface-${shade}`, value as string);
            // Vars for Tailwind
            root.style.setProperty(`--surface-${shade}`, value as string);
          });

          // call a updateSurfacePalette if needed
          updateSurfacePalette(surfaceColor.palette);
        }
      }
    }
  }

  // Initialize theme on first use
  /* The highlighted code block is part of the initialization process within the `useLayout` function in
a Vue composition setup. Here's what it does: */
  if (!initialized) {
    initialized = true;

    // Client-side initialization
    /* The `onMounted` function in Vue is a lifecycle hook that is called after the component has been
   mounted to the DOM. In the provided code snippet, the `onMounted` function is used to initialize
   the theme colors and settings when the component is mounted. */
    onMounted(() => {
      // Note: Dark mode is applied by the theme-init plugin before app mounts
      const root = document.documentElement;

      // Apply initial primary color
      const initialPrimaryColor = primaryColors.value.find((c) => c.name === appState.value.primary);
      if (initialPrimaryColor) {
        // Apply CSS variables for both PrimeVue (--p-primary-*) and Tailwind (--primary-*)
        Object.entries(initialPrimaryColor.palette).forEach(([shade, value]) => {
          root.style.setProperty(`--p-primary-${shade}`, value as string);
          root.style.setProperty(`--primary-${shade}`, value as string);
        });

        updatePrimaryPalette(initialPrimaryColor.palette);
      }

      // Apply initial surface color if set
      if (appState.value.surface) {
        const initialSurfaceColor = surfaces.value.find((s) => s.name === appState.value.surface);
        if (initialSurfaceColor) {
          Object.entries(initialSurfaceColor.palette).forEach(([shade, value]) => {
            root.style.setProperty(`--p-surface-${shade}`, value as string);
            root.style.setProperty(`--surface-${shade}`, value as string);
          });
          updateSurfacePalette(initialSurfaceColor.palette);
        }
      }

      // Dark mode is already applied above

      // Watch for dark mode changes and apply to DOM
      watch(
        () => appState.value.darkMode,
        (isDark) => {
          if (isDark) {
            document.documentElement.classList.add("p-dark");
          } else {
            document.documentElement.classList.remove("p-dark");
          }
        },
      );

      // Watch for any state changes and persist to localStorage
      watch(
        appState,
        (newState) => {
          try {
            localStorage.setItem("lq-theme-config", JSON.stringify(newState));
          } catch (error) {
            console.warn("Failed to save theme config:", error);
          }
        },
        { deep: true },
      );

      // Initialize responsive menu type using VueUse breakpoints
      userPreferredMenuType = appState.value.menuType;

      // Use VueUse breakpoints (Tailwind config)
      const breakpoints = useBreakpoints(breakpointsTailwind);
      const isSmallerThanLg = breakpoints.smaller("lg"); // < 1024px

      // Apply initial responsive state
      applyResponsiveMenuType(isSmallerThanLg.value);

      // Watch for breakpoint changes (automatically debounced by VueUse)
      watch(isSmallerThanLg, (isSmaller) => {
        applyResponsiveMenuType(isSmaller);
      });
    });
  }

  /* The code block you provided is creating reactive computed properties using Vue's `computed`
 function. Here's what each computed property is doing: */
  const isDarkMode = computed(() => appState.value.darkMode);
  const primary = computed(() => appState.value.primary);
  const surface = computed(() => appState.value.surface);
  const menuType = computed(() => appState.value.menuType);
  const menuTypeLocked = computed(() => appState.value.menuTypeLocked);

  return {
    primaryColors,
    surfaces,
    isDarkMode,
    primary,
    surface,
    menuType,
    menuTypeLocked,
    toggleDarkMode,
    setDarkMode,
    setPrimary,
    setSurface,
    setMenuType,
    toggleMenuTypeLock,
    updateColors,
  };
}
