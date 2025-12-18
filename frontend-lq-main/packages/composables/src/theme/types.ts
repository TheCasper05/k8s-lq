import type { Ref } from "vue";

export interface ColorPalette {
  50?: string;
  100?: string;
  200?: string;
  300?: string;
  400?: string;
  500?: string;
  600?: string;
  700?: string;
  800?: string;
  900?: string;
  950?: string;
  0?: string;
}

export interface PrimaryColor {
  name: string;
  palette: ColorPalette;
}

export interface SurfaceColor {
  name: string;
  palette: ColorPalette;
}

export type MenuType = "icon-only" | "grouped" | "simple" | "static";

export interface AppState {
  primary: string;
  surface: string | null;
  darkMode: boolean;
  menuType: MenuType;
  menuTypeLocked: boolean;
}

export type ColorType = "primary" | "surface";

// Menu/Sidebar types
export interface MenuItem {
  label: string;
  icon: string;
  to?: string;
  badge?: string | number;
  items?: MenuItem[];
}

export interface MenuSection {
  label: string;
  items: MenuItem[];
}

export interface MenuTypeOption {
  value: MenuType;
  label: string;
  description: string;
  icon: string;
}

export interface UseLayoutReturn {
  primaryColors: Ref<PrimaryColor[]>;
  surfaces: Ref<SurfaceColor[]>;
  isDarkMode: Ref<boolean>;
  primary: Ref<string>;
  surface: Ref<string | null>;
  menuType: Ref<MenuType>;
  menuTypeLocked: Ref<boolean>;
  toggleDarkMode: () => void;
  setDarkMode: (value: boolean) => void;
  setPrimary: (value: string) => void;
  setSurface: (value: string) => void;
  setMenuType: (value: MenuType) => void;
  toggleMenuTypeLock: () => void;
  updateColors: (type: ColorType, colorName: string) => void;
}

export type UseLayoutFunction = (role?: string | null) => UseLayoutReturn;
