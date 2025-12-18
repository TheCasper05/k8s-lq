import { readFileSync, writeFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import * as readline from "node:readline";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

interface HardcodedText {
  file: string;
  line: number;
  text: string;
  context: "template" | "script";
  suggestedKey?: string;
}

interface Replacement {
  file: string;
  oldText: string;
  newText: string;
  key: string;
}

const replacements: Replacement[] = [];

async function promptUser(question: string): Promise<string> {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer.trim());
    });
  });
}

async function processHardcodedTexts() {
  const jsonPath = join(__dirname, "..", "hardcoded-texts.json");

  let hardcodedTexts: HardcodedText[];
  try {
    const data = readFileSync(jsonPath, "utf-8");
    hardcodedTexts = JSON.parse(data);
  } catch {
    console.error("❌ Error: Run extract-hardcoded.ts first to generate hardcoded-texts.json");
    process.exit(1);
  }

  console.log(`\n📝 Found ${hardcodedTexts.length} hardcoded texts\n`);
  console.log("This script will help you replace them with i18n keys.\n");

  const mode = await promptUser(
    "Choose mode:\n1. Interactive (review each text)\n2. Auto (use suggested keys)\n3. Skip (exit)\nEnter choice (1/2/3): ",
  );

  if (mode === "3") {
    console.log("Exiting...");
    return;
  }

  const isInteractive = mode === "1";

  for (let i = 0; i < hardcodedTexts.length; i++) {
    const item = hardcodedTexts[i];

    console.log(`\n[${i + 1}/${hardcodedTexts.length}]`);
    console.log(`File: ${item.file}`);
    console.log(`Line: ${item.line}`);
    console.log(`Text: "${item.text}"`);
    console.log(`Context: ${item.context}`);
    console.log(`Suggested key: ${item.suggestedKey}`);

    let key = item.suggestedKey || "";
    let shouldReplace = true;

    if (isInteractive) {
      const action = await promptUser(
        "\nAction:\n1. Use suggested key\n2. Enter custom key\n3. Skip this text\nEnter choice (1/2/3): ",
      );

      if (action === "3") {
        shouldReplace = false;
      } else if (action === "2") {
        key = await promptUser("Enter custom key: ");
      }
    }

    if (shouldReplace && key) {
      const newText = item.context === "template" ? `{{ $t('${key}') }}` : `t('${key}')`;

      replacements.push({
        file: item.file,
        oldText: item.text,
        newText,
        key,
      });

      console.log(`✅ Will replace with: ${newText}`);
    }
  }

  if (replacements.length === 0) {
    console.log("\n⚠️  No replacements to make.");
    return;
  }

  console.log(`\n\n📊 Summary: ${replacements.length} replacements to make\n`);

  const confirm = await promptUser("Proceed with replacements? (yes/no): ");

  if (confirm.toLowerCase() !== "yes") {
    console.log("Cancelled.");
    return;
  }

  applyReplacements();
}

function applyReplacements() {
  const fileChanges = new Map<string, string>();

  // Group replacements by file
  const byFile = new Map<string, Replacement[]>();
  replacements.forEach((rep) => {
    if (!byFile.has(rep.file)) {
      byFile.set(rep.file, []);
    }
    byFile.get(rep.file)!.push(rep);
  });

  // Apply replacements file by file
  byFile.forEach((reps, filePath) => {
    const fullPath = join(__dirname, "..", "..", "..", "apps", filePath);
    let content = readFileSync(fullPath, "utf-8");

    reps.forEach((rep) => {
      // Escape special regex characters
      const escapedOld = rep.oldText.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      const regex = new RegExp(escapedOld, "g");
      content = content.replace(regex, rep.newText);
    });

    writeFileSync(fullPath, content);
    fileChanges.set(filePath, content);
    console.log(`✅ Updated: ${filePath}`);
  });

  // Generate translation keys file
  const keysToAdd = new Map<string, Set<string>>();
  replacements.forEach((rep) => {
    const [namespace] = rep.key.split(".");
    if (!keysToAdd.has(namespace)) {
      keysToAdd.set(namespace, new Set());
    }
    keysToAdd.get(namespace)!.add(rep.key);
  });

  console.log("\n\n📝 Translation keys to add:\n");
  keysToAdd.forEach((keys, namespace) => {
    console.log(`\n${namespace}:`);
    keys.forEach((key) => {
      const text = replacements.find((r) => r.key === key)?.oldText || "";
      console.log(`  ${key}: '${text}',`);
    });
  });

  console.log("\n\n✅ Replacements complete!");
  console.log("\n💡 Next steps:");
  console.log("1. Add the translation keys shown above to packages/i18n/src/locales/en/");
  console.log("2. Translate to other languages");
  console.log("3. Run pnpm i18n:validate");
  console.log("4. Test your changes\n");
}

// Run
processHardcodedTexts().catch(console.error);
