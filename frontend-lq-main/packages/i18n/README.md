# @lq/i18n

Shared i18n **utilities and configuration** for LingoQuesto monorepo.

> ⚠️ **Important**: This package does NOT contain translations. Each app manages its own translation files due to
> bundler limitations.

## What's Included

### ✅ Configuration

- `SUPPORTED_LOCALES` - List of all supported languages
- `DEFAULT_LOCALE` - Default language (en)
- `FALLBACK_LOCALE` - Fallback language (en)
- Locale metadata (flags, names, RTL direction)

### ✅ Utilities

- **RTL Support**: `isRTL()`, `setDocumentDir()`, `getDirection()`
- **Persistence**: `saveLocale()`, `loadLocale()`, `clearLocale()`
- **Cookie Support**: `saveLocaleToCookie()`, `loadLocaleFromCookie()`

### ✅ Composables

- `useLocaleSwitch()` - Vue composable for locale switching

## Usage

### Configuration

```typescript
import { SUPPORTED_LOCALES, DEFAULT_LOCALE } from "@lq/i18n";

console.log(SUPPORTED_LOCALES);
// [
//   { code: 'en', name: 'English', flag: '🇺🇸', dir: 'ltr' },
//   { code: 'es', name: 'Español', flag: '🇪🇸', dir: 'ltr' },
//   ...
// ]
```

### RTL Support

```typescript
import { setDocumentDir, isRTL } from "@lq/i18n";

// Set document direction based on locale
setDocumentDir("ar"); // Sets dir="rtl" and lang="ar"

// Check if locale is RTL
if (isRTL("ar")) {
  // Handle RTL layout
}
```

### Persistence

```typescript
import { saveLocale, loadLocale } from "@lq/i18n";

// Save user's locale preference
saveLocale("es");

// Load saved locale
const savedLocale = loadLocale(); // 'es'
```

### Vue Composable

```typescript
import { useLocaleSwitch } from "@lq/i18n";

const { currentLocale, availableLocales, switchLocale } = useLocaleSwitch();

switchLocale("fr");
```

## Translation Files

**Each app manages its own translations:**

```
apps/institutional/src/locales/
├── en.ts
├── es.ts
├── ar.ts
└── ...

apps/student-teacher/locales/
├── en.ts
├── es.ts
├── ar.ts
└── ...
```

### Why not centralized translations?

- **Vite** (institutional app) and **Nuxt** (student-teacher app) have different module resolution
- **Lazy loading** in Nuxt requires specific file structures
- **Build optimization** works better with local files
- **HMR** is faster with co-located translations

## Adding a New Language

1. **Update configuration** in this package:

```typescript
// packages/i18n/src/config.ts
export const SUPPORTED_LOCALES = [
  // ... existing locales
  {
    code: "pt",
    name: "Português",
    dir: "ltr",
    flag: "🇧🇷",
    language: "pt-BR",
  },
];
```

2. **Add translation files** in each app:

```bash
# Institutional app
apps/institutional/src/locales/pt.ts

# Student-Teacher app
apps/student-teacher/locales/pt.ts
```

3. **Register in app configs**:

```typescript
// Institutional: apps/institutional/src/main.ts
import pt from "./locales/pt";

// Student-Teacher: apps/student-teacher/nuxt.config.ts
i18n: {
  locales: [
    // ... existing
    { code: "pt", file: "pt.ts" },
  ];
}
```

## Translation Template

Use this template for new translation files:

```typescript
export default {
  common: {
    loading: "",
    save: "",
    cancel: "",
    // ...
  },
  auth: {
    login: "",
    logout: "",
    // ...
  },
  // ... other namespaces
};
```

## Best Practices

1. **Keep translations in sync** between apps manually or with scripts
2. **Use i18n Ally** VSCode extension to track missing translations
3. **Follow naming conventions**: `namespace.key` (e.g., `common.save`)
4. **Test RTL languages** (Arabic) separately
5. **Use English as source** for all new keys

## API Reference

### Configuration

```typescript
export interface LocaleConfig {
  code: string;
  name: string;
  dir: "ltr" | "rtl";
  flag: string;
  language?: string;
}

export const SUPPORTED_LOCALES: readonly LocaleConfig[];
export const DEFAULT_LOCALE: string;
export const FALLBACK_LOCALE: string;
export const LOCALE_COOKIE_KEY: string;
export const LOCALE_STORAGE_KEY: string;
```

### Utilities

```typescript
// RTL
export function isRTL(locale: string): boolean;
export function setDocumentDir(locale: string): void;
export function getDirection(locale: string): "ltr" | "rtl";

// Persistence
export function saveLocale(locale: string): void;
export function loadLocale(): string | null;
export function clearLocale(): void;
export function saveLocaleToCookie(locale: string, days?: number): void;
export function loadLocaleFromCookie(): string | null;
```

### Composables

```typescript
export function useLocaleSwitch(): {
  currentLocale: Ref<SupportedLocale>;
  availableLocales: ComputedRef<LocaleConfig[]>;
  switchLocale: (newLocale: SupportedLocale) => void;
  getCurrentLocaleConfig: () => LocaleConfig | undefined;
};
```

## License

MIT
