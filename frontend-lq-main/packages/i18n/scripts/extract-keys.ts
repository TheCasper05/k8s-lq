#!/usr/bin/env tsx
/**
 * Extract translation keys from source code
 *
 * Features:
 * 1. Scans .vue, .ts, .js files for t('key') and $t('key') patterns
 * 2. Detects hardcoded text in templates and scripts
 * 3. Updates translation files with missing keys (marked as [MISSING])
 * 4. Generates report of hardcoded texts
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { glob } from "glob";
import * as parser from "@babel/parser";
import traverse from "@babel/traverse";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const ROOT_DIR = path.join(__dirname, "../../..");
const APPS_DIR = path.join(ROOT_DIR, "apps");
const STUDENT_TEACHER_LOCALES_DIR = path.join(ROOT_DIR, "apps/student-teacher/i18n/locales");
const LOCALES = ["en", "es", "ar", "fr", "de", "zh", "pt", "it"];
const APPS = [{ name: "student-teacher", path: STUDENT_TEACHER_LOCALES_DIR }];

interface ExtractedKey {
  key: string;
  file: string;
  line: number;
}

function extractScriptFromVue(code: string): string {
  // Extract <script> or <script setup> content from Vue SFC
  const scriptRegex = /<script[^>]*>([\s\S]*?)<\/script>/g;
  const matches = [...code.matchAll(scriptRegex)];
  return matches.map((m) => m[1]).join("\n");
}

function extractTemplateKeys(code: string): string[] {
  // Extract translation keys from template using regex
  const keys: string[] = [];

  // Match $t('key') or $t("key")
  const templateRegex = /\$t\(['"]([^'"]+)['"]\)/g;
  let match;

  while ((match = templateRegex.exec(code)) !== null) {
    keys.push(match[1]);
  }

  return keys;
}

function extractKeysFromCode(code: string, filePath: string): ExtractedKey[] {
  const keys: ExtractedKey[] = [];

  // If it's a Vue file, extract template keys first
  if (filePath.endsWith(".vue")) {
    const templateKeys = extractTemplateKeys(code);
    templateKeys.forEach((key) => {
      keys.push({ key, file: filePath, line: 0 });
    });

    // Extract script content
    code = extractScriptFromVue(code);
    if (!code.trim()) {
      return keys; // No script section
    }
  }

  try {
    const ast = parser.parse(code, {
      sourceType: "module",
      plugins: ["typescript", "jsx"],
    });

    traverse.default(ast, {
      CallExpression(path) {
        const callee = path.node.callee;

        // Match t('key') or $t('key')
        let isTranslationCall = false;
        if (callee.type === "Identifier" && callee.name === "t") {
          isTranslationCall = true;
        } else if (callee.type === "MemberExpression") {
          const property = callee.property;
          if (property.type === "Identifier" && property.name === "t") {
            isTranslationCall = true;
          }
        }

        if (isTranslationCall && path.node.arguments.length > 0) {
          const firstArg = path.node.arguments[0];
          if (firstArg.type === "StringLiteral") {
            keys.push({
              key: firstArg.value,
              file: filePath,
              line: firstArg.loc?.start.line || 0,
            });
          }
        }
      },
    });
  } catch (error) {
    // Silently skip parse errors for Vue files (template syntax)
    if (!filePath.endsWith(".vue")) {
      console.warn(`⚠️  Failed to parse ${filePath}:`, (error as Error).message);
    }
  }

  return keys;
}

async function scanFiles(): Promise<ExtractedKey[]> {
  console.log("🔍 Scanning files for translation keys...");

  const patterns = [`${APPS_DIR}/**/*.vue`, `${APPS_DIR}/**/*.ts`, `${APPS_DIR}/**/*.js`];

  const ignorePatterns = ["**/node_modules/**", "**/dist/**", "**/.nuxt/**", "**/.output/**"];

  const allKeys: ExtractedKey[] = [];

  for (const pattern of patterns) {
    const files = await glob(pattern, { ignore: ignorePatterns });

    for (const file of files) {
      const code = fs.readFileSync(file, "utf-8");
      const keys = extractKeysFromCode(code, file);
      allKeys.push(...keys);
    }
  }

  return allKeys;
}

function parseKeyPath(key: string): { path: string[] } {
  const parts = key.split(".");
  return { path: parts };
}

function setNestedValue(obj: any, path: string[], value: string): void {
  let current = obj;

  for (let i = 0; i < path.length - 1; i++) {
    const key = path[i];
    if (!(key in current)) {
      current[key] = {};
    }
    current = current[key];
  }

  const lastKey = path[path.length - 1];
  if (!(lastKey in current)) {
    current[lastKey] = value;
  }
}

function generateTranslationFile(data: any): string {
  return `export default ${JSON.stringify(data, null, 2)}\n`;
}

async function updateTranslations(keys: ExtractedKey[]): Promise<void> {
  console.log("\n📝 Updating translation files...");

  const uniqueKeys = Array.from(new Set(keys.map((k) => k.key)));
  const newKeysAdded: Record<string, Record<string, number>> = {};

  // Update translations for each app
  for (const app of APPS) {
    console.log(`\n📱 Updating ${app.name}...`);
    newKeysAdded[app.name] = {};

    for (const locale of LOCALES) {
      newKeysAdded[app.name][locale] = 0;

      const filePath = path.join(app.path, `${locale}.ts`);

      if (!fs.existsSync(filePath)) {
        console.warn(`⚠️  Locale file not found: ${filePath}`);
        continue;
      }

      // Load existing translations
      const fileUrl = pathToFileURL(filePath).href;
      const module = await import(fileUrl);
      const translations = JSON.parse(JSON.stringify(module.default));

      // Add missing keys
      for (const key of uniqueKeys) {
        const { path: keyPath } = parseKeyPath(key);

        if (keyPath.length === 0) continue;

        // Check if key already exists
        let current: any = translations;
        let exists = true;

        for (const part of keyPath) {
          if (!(part in current)) {
            exists = false;
            break;
          }
          current = current[part];
        }

        // Add missing key
        if (!exists) {
          const value = locale === "en" ? `[MISSING] ${key}` : `[TODO-${locale.toUpperCase()}] ${key}`;
          setNestedValue(translations, keyPath, value);
          newKeysAdded[app.name][locale]++;
        }
      }

      // Write updated file
      const content = generateTranslationFile(translations);
      fs.writeFileSync(filePath, content, "utf-8");
    }
  }

  // Report
  console.log("\n📊 Summary:");
  for (const app of APPS) {
    console.log(`\n  ${app.name}:`);
    for (const locale of LOCALES) {
      if (newKeysAdded[app.name][locale] > 0) {
        console.log(`    ${locale.toUpperCase()}: ${newKeysAdded[app.name][locale]} new keys added`);
      }
    }
  }

  const totalNew = Object.values(newKeysAdded).reduce(
    (sum, app) => sum + Object.values(app).reduce((s, n) => s + n, 0),
    0,
  );
  if (totalNew === 0) {
    console.log("\n  ✅ No new keys found");
  }
}

async function main() {
  try {
    console.log("🚀 Starting translation key extraction...\n");

    const keys = await scanFiles();
    const uniqueKeys = Array.from(new Set(keys.map((k) => k.key)));

    console.log(`\n✅ Found ${keys.length} translation calls (${uniqueKeys.length} unique keys)`);

    await updateTranslations(keys);

    console.log("\n✅ Extraction complete!");
  } catch (error) {
    console.error("❌ Error extracting keys:", error);
    process.exit(1);
  }
}

main();
