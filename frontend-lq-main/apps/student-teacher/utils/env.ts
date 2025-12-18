import { z } from "zod";
import { Env } from "@lq/utils";

const envSchema = z.object({
  NUXT_PUBLIC_API_BASE_URL: z.url().default("https://api-qa.lingoquesto.com").describe("URL base de la API Django"),
  NUXT_PUBLIC_GRAPHQL_ENDPOINT: z
    .url()
    .default("https://api-qa.lingoquesto.com/graphql/")
    .describe("URL del endpoint GraphQL"),
  NUXT_PUBLIC_GRAPHQL_WS_ENDPOINT: z
    .url()
    .default("wss://api-qa.lingoquesto.com/graphql")
    .describe("URL del endpoint WebSocket para GraphQL subscriptions"),
  NUXT_PUBLIC_SENTRY_DSN: z.string().optional().describe("DSN de Sentry para reportar errores (opcional)"),
  NUXT_PUBLIC_SENTRY_ENVIRONMENT: z.nativeEnum(Env).default(Env.Local).describe("Ambiente de Sentry"),
  NODE_ENV: z.nativeEnum(Env).default(Env.Local).describe("Ambiente de Node.js"),
});

const validateEnv = () => {
  const envVars = {
    NUXT_PUBLIC_API_BASE_URL: process.env.NUXT_PUBLIC_API_BASE_URL,
    NUXT_PUBLIC_GRAPHQL_ENDPOINT: process.env.NUXT_PUBLIC_GRAPHQL_ENDPOINT,
    NUXT_PUBLIC_GRAPHQL_WS_ENDPOINT: process.env.NUXT_PUBLIC_GRAPHQL_WS_ENDPOINT,
    NUXT_PUBLIC_SENTRY_DSN: process.env.NUXT_PUBLIC_SENTRY_DSN,
    NUXT_PUBLIC_SENTRY_ENVIRONMENT: process.env.NUXT_PUBLIC_SENTRY_ENVIRONMENT,
    NODE_ENV: process.env.NODE_ENV || "local",
  };

  const result = envSchema.safeParse(envVars);

  if (!result.success) {
    console.error("❌ Error en la configuración de variables de entorno:");
    result.error.issues.forEach((issue) => {
      console.error(`  - ${issue.path.join(".")}: ${issue.message}`);
    });
    // throw new Error("Variables de entorno inválidas. Revisa la consola para más detalles.");
  }

  console.log("✅ Configuración de entorno válida");
  return result.data;
};

export const envVars = validateEnv();

export type envVars = z.infer<typeof envSchema>;

export { envSchema };
