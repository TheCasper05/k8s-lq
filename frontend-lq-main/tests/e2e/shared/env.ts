export const ENV = {
  STUDENT_TEACHER_URL: process.env.STUDENT_TEACHER_URL || "https://app-qa.lingoquesto.com",
  INSTITUTIONAL_URL: process.env.INSTITUTIONAL_URL || "https://app-qa.lingoquesto.com",
  ENVIRONMENT: process.env.E2E_ENV || process.env.NODE_ENV || "staging",
  HEADLESS: process.env.HEADLESS !== "false",
  SLOW_MO: process.env.SLOW_MO ? Number.parseInt(process.env.SLOW_MO, 10) : 0,
  TEST_TIMEOUT: process.env.TEST_TIMEOUT ? Number.parseInt(process.env.TEST_TIMEOUT, 10) : 30000,
  ACTION_TIMEOUT: process.env.ACTION_TIMEOUT ? Number.parseInt(process.env.ACTION_TIMEOUT, 10) : 10000,
  TEST_STUDENT_EMAIL: process.env.TEST_STUDENT_EMAIL || "szapatamejia111@gmail.com",
  TEST_STUDENT_PASSWORD: process.env.TEST_STUDENT_PASSWORD || "QwertyuiopA2308***",
  TEST_TEACHER_EMAIL: process.env.TEST_TEACHER_EMAIL || "qalingoquesto@gmail.com",
  TEST_TEACHER_PASSWORD: process.env.TEST_TEACHER_PASSWORD || "QwertyuiopA2308***",
  TEST_ADMIN_EMAIL: process.env.TEST_ADMIN_EMAIL || "qalingoquesto@gmail.com",
  TEST_ADMIN_PASSWORD: process.env.TEST_ADMIN_PASSWORD || "QwertyuiopA2308***",
  API_URL: process.env.API_URL || process.env.GRAPHQL_ENDPOINT || "http://localhost:8000",
};

export function validateEnv() {
  const required = ["STUDENT_TEACHER_URL", "INSTITUTIONAL_URL"];
  const missing = required.filter((key) => !ENV[key as keyof typeof ENV]);

  if (missing.length > 0) {
    console.warn(`⚠️  Missing environment variables: ${missing.join(", ")}`);
    console.warn("Using default values");
  }
}

validateEnv();
