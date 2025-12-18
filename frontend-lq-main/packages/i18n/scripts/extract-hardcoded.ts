import { readFileSync, writeFileSync, readdirSync, statSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

interface HardcodedText {
  file: string;
  line: number;
  text: string;
  context: "template" | "script";
  suggestedKey?: string;
}

const hardcodedTexts: HardcodedText[] = [];

// Patterns to detect hardcoded text
const templatePatterns = [
  // Text between tags: <div>Hardcoded text</div>
  /<[^>]+>([^<>{}\n]+)</g,
  // Attributes with text: placeholder="Hardcoded"
  /(?:placeholder|title|label|alt)=["']([^"']+)["']/g,
];

const scriptPatterns = [
  // String literals not in i18n calls
  /(?<!t\(|i18n\.|locale\.|message:)\s*["']([^"'\n]{3,})["']/g,
];

// Patterns to ignore
const ignorePatterns = [
  /^\s*$/, // Empty strings
  /^\d+$/, // Numbers only
  /^[a-z-_]+$/, // kebab-case (likely CSS classes or keys)
  /^[A-Z_]+$/, // CONSTANT_CASE
  /^\$t\(/, // Already using i18n
  /^@/, // Directives
  /^v-/, // Vue directives
  /^:/, // Vue bindings
  /^#/, // Slots
  /^\./, // Paths
  /^\//, // Paths
  /^http/, // URLs
  /^data-/, // Data attributes
  /^aria-/, // ARIA attributes
  /^[{[]/, // Objects/Arrays
  /console\./, // Console logs
  /import |export |from /, // Import/export statements
];

function shouldIgnore(text: string): boolean {
  const trimmed = text.trim();
  if (trimmed.length < 3) return true;
  return ignorePatterns.some((pattern) => pattern.test(trimmed));
}

function generateKey(text: string, context: string): string {
  // Generate a key based on the text
  const cleaned = text
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, "")
    .trim()
    .split(/\s+/)
    .slice(0, 4)
    .join("_");

  return `${context}.${cleaned}`;
}

function extractFromTemplate(content: string, filePath: string) {
  const lines = content.split("\n");

  lines.forEach((line, index) => {
    templatePatterns.forEach((pattern) => {
      const matches = line.matchAll(pattern);
      for (const match of matches) {
        const text = match[1]?.trim();
        if (text && !shouldIgnore(text) && !text.includes("{{") && !text.includes("$t(")) {
          hardcodedTexts.push({
            file: filePath,
            line: index + 1,
            text,
            context: "template",
            suggestedKey: generateKey(text, "common"),
          });
        }
      }
    });
  });
}

function extractFromScript(content: string, filePath: string) {
  const lines = content.split("\n");

  lines.forEach((line, index) => {
    // Skip if line contains i18n usage
    if (line.includes("$t(") || line.includes("t(") || line.includes("i18n.")) {
      return;
    }

    scriptPatterns.forEach((pattern) => {
      const matches = line.matchAll(pattern);
      for (const match of matches) {
        const text = match[1]?.trim();
        if (text && !shouldIgnore(text)) {
          hardcodedTexts.push({
            file: filePath,
            line: index + 1,
            text,
            context: "script",
            suggestedKey: generateKey(text, "common"),
          });
        }
      }
    });
  });
}

function scanVueFile(filePath: string) {
  const content = readFileSync(filePath, "utf-8");

  // Extract template section
  const templateMatch = content.match(/<template>([\s\S]*?)<\/template>/);
  if (templateMatch) {
    extractFromTemplate(templateMatch[1], filePath);
  }

  // Extract script section
  const scriptMatch = content.match(/<script[^>]*>([\s\S]*?)<\/script>/);
  if (scriptMatch) {
    extractFromScript(scriptMatch[1], filePath);
  }
}

function scanDirectory(dir: string, baseDir: string) {
  const entries = readdirSync(dir);

  for (const entry of entries) {
    const fullPath = join(dir, entry);
    const stat = statSync(fullPath);

    if (stat.isDirectory()) {
      // Skip node_modules, .nuxt, dist, etc.
      if (!["node_modules", ".nuxt", "dist", ".git", "coverage"].includes(entry)) {
        scanDirectory(fullPath, baseDir);
      }
    } else if (entry.endsWith(".vue")) {
      scanVueFile(fullPath);
    }
  }
}

function generateReport() {
  console.log("\n📝 Hardcoded Text Report\n");
  console.log(`Found ${hardcodedTexts.length} potential hardcoded texts\n`);

  // Group by file
  const byFile = new Map<string, HardcodedText[]>();
  hardcodedTexts.forEach((item) => {
    if (!byFile.has(item.file)) {
      byFile.set(item.file, []);
    }
    byFile.get(item.file)!.push(item);
  });

  // Generate report
  let report = "# Hardcoded Text Extraction Report\n\n";
  report += `Total files scanned: ${byFile.size}\n`;
  report += `Total hardcoded texts found: ${hardcodedTexts.length}\n\n`;

  byFile.forEach((texts, file) => {
    report += `## ${file}\n\n`;
    texts.forEach((item) => {
      report += `- Line ${item.line} (${item.context}): "${item.text}"\n`;
      report += `  Suggested key: \`${item.suggestedKey}\`\n\n`;
    });
  });

  // Save report
  const reportPath = join(__dirname, "..", "hardcoded-texts-report.md");
  writeFileSync(reportPath, report);
  console.log(`✅ Report saved to: ${reportPath}\n`);

  // Generate JSON for programmatic use
  const jsonPath = join(__dirname, "..", "hardcoded-texts.json");
  writeFileSync(jsonPath, JSON.stringify(hardcodedTexts, null, 2));
  console.log(`✅ JSON data saved to: ${jsonPath}\n`);
}

// Main execution
const appsDir = join(__dirname, "..", "..", "..", "apps");

console.log("🔍 Scanning for hardcoded texts in Vue files...\n");

// Scan student-teacher app
const studentTeacherDir = join(appsDir, "student-teacher");
if (statSync(studentTeacherDir).isDirectory()) {
  console.log("Scanning student-teacher app...");
  scanDirectory(studentTeacherDir, appsDir);
}

// Scan institutional app
const institutionalDir = join(appsDir, "institutional");
if (statSync(institutionalDir).isDirectory()) {
  console.log("Scanning institutional app...");
  scanDirectory(institutionalDir, appsDir);
}

generateReport();

console.log("\n💡 Next steps:");
console.log("1. Review the report: packages/i18n/hardcoded-texts-report.md");
console.log("2. Add translations to packages/i18n/src/locales/");
console.log("3. Replace hardcoded texts with $t() calls");
console.log("4. Run pnpm i18n:validate to check completeness\n");
