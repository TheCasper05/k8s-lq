#!/usr/bin/env tsx
/**
 * Validate translations across all locales
 * Checks for:
 * - Missing keys compared to EN (base locale)
 * - Pending translations ([TODO], [MISSING] markers)
 * - Structure consistency
 */

import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const STUDENT_TEACHER_LOCALES_DIR = path.join(__dirname, "../../../apps/student-teacher/i18n/locales");
const BASE_LOCALE = "en";
const LOCALES = ["en", "es", "ar", "fr", "de", "zh", "pt", "it"];
const APPS = [{ name: "student-teacher", path: STUDENT_TEACHER_LOCALES_DIR }];

interface TranslationObject {
  [key: string]: string | TranslationObject;
}

interface ValidationResult {
  locale: string;
  missingKeys: string[];
  pendingTranslations: string[];
  extraKeys: string[];
}

function flattenKeys(obj: TranslationObject, prefix = ""): Set<string> {
  const keys = new Set<string>();

  for (const [key, value] of Object.entries(obj)) {
    const fullKey = prefix ? `${prefix}.${key}` : key;

    if (typeof value === "string") {
      keys.add(fullKey);
    } else if (typeof value === "object" && value !== null) {
      const nestedKeys = flattenKeys(value, fullKey);
      nestedKeys.forEach((k) => keys.add(k));
    }
  }

  return keys;
}

function findPendingTranslations(obj: TranslationObject, prefix = ""): string[] {
  const pending: string[] = [];

  for (const [key, value] of Object.entries(obj)) {
    const fullKey = prefix ? `${prefix}.${key}` : key;

    if (typeof value === "string") {
      if (value.includes("[TODO") || value.includes("[MISSING]") || value.startsWith("TODO:")) {
        pending.push(fullKey);
      }
    } else if (typeof value === "object" && value !== null) {
      pending.push(...findPendingTranslations(value, fullKey));
    }
  }

  return pending;
}

async function loadLocale(locale: string, localesDir: string): Promise<TranslationObject> {
  const localePath = path.join(localesDir, `${locale}.ts`);
  const fileUrl = pathToFileURL(localePath).href;
  const module = await import(fileUrl);
  return module.default;
}

async function validateLocale(locale: string, baseKeys: Set<string>, localesDir: string): Promise<ValidationResult> {
  const translations = await loadLocale(locale, localesDir);
  const localeKeys = flattenKeys(translations);
  const pendingTranslations = findPendingTranslations(translations);

  const missingKeys = Array.from(baseKeys).filter((key) => !localeKeys.has(key));
  const extraKeys = Array.from(localeKeys).filter((key) => !baseKeys.has(key));

  return {
    locale,
    missingKeys,
    pendingTranslations,
    extraKeys,
  };
}

async function main() {
  try {
    console.log("🔍 Validating translations...\n");

    let hasErrors = false;
    let hasWarnings = false;

    // Validate each app
    for (const app of APPS) {
      console.log(`\n${"=".repeat(60)}`);
      console.log(`📱 App: ${app.name.toUpperCase()}`);
      console.log("=".repeat(60));

      // Load base locale (EN)
      const baseTranslations = await loadLocale(BASE_LOCALE, app.path);
      const baseKeys = flattenKeys(baseTranslations);
      console.log(`\n📊 Base locale (${BASE_LOCALE}): ${baseKeys.size} keys`);

      // Validate each locale
      for (const locale of LOCALES) {
        if (locale === BASE_LOCALE) continue;

        const result = await validateLocale(locale, baseKeys, app.path);

        console.log(`\n🌍 Locale: ${locale.toUpperCase()}`);
        console.log("─".repeat(50));

        // Missing keys (ERROR)
        if (result.missingKeys.length > 0) {
          hasErrors = true;
          console.log(`\n❌ Missing keys (${result.missingKeys.length}):`);
          result.missingKeys.slice(0, 10).forEach((key) => console.log(`   - ${key}`));
          if (result.missingKeys.length > 10) {
            console.log(`   ... and ${result.missingKeys.length - 10} more`);
          }
        }

        // Extra keys (WARNING)
        if (result.extraKeys.length > 0) {
          hasWarnings = true;
          console.log(`\n⚠️  Extra keys not in base (${result.extraKeys.length}):`);
          result.extraKeys.slice(0, 5).forEach((key) => console.log(`   - ${key}`));
          if (result.extraKeys.length > 5) {
            console.log(`   ... and ${result.extraKeys.length - 5} more`);
          }
        }

        // Pending translations (WARNING)
        if (result.pendingTranslations.length > 0) {
          hasWarnings = true;
          console.log(`\n⚠️  Pending translations (${result.pendingTranslations.length}):`);
          result.pendingTranslations.slice(0, 5).forEach((key) => console.log(`   - ${key}`));
          if (result.pendingTranslations.length > 5) {
            console.log(`   ... and ${result.pendingTranslations.length - 5} more`);
          }
        }

        if (
          result.missingKeys.length === 0 &&
          result.extraKeys.length === 0 &&
          result.pendingTranslations.length === 0
        ) {
          console.log("\n✅ All translations complete!");
        }
      }
    }

    // Summary
    console.log("\n" + "=".repeat(50));
    console.log("📋 Summary:");
    console.log("=".repeat(50));

    if (hasErrors) {
      console.log("❌ Validation failed with errors");
      process.exit(1);
    } else if (hasWarnings) {
      console.log("⚠️  Validation passed with warnings");
      process.exit(0);
    } else {
      console.log("✅ All translations are valid!");
      process.exit(0);
    }
  } catch (error) {
    console.error("❌ Error validating translations:", error);
    process.exit(1);
  }
}

main();
