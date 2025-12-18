import { z } from "zod";
import { Env } from "@lq/utils";

const envSchema = z.object({
  VITE_API_BASE_URL: z.url().describe("URL base de la API"),
  VITE_GRAPHQL_ENDPOINT: z.url().describe("URL del endpoint GraphQL"),
  VITE_GRAPHQL_WS_ENDPOINT: z.url().describe("URL del endpoint WebSocket para GraphQL subscriptions"),
  VITE_SENTRY_DSN: z.string().optional().describe("DSN de Sentry para reportar errores (opcional)"),
  VITE_ENVIRONMENT: z.enum(Env).default(Env.Local).describe("Ambiente de Sentry"),
});

const validateEnv = () => {
  const result = envSchema.safeParse(import.meta.env);

  if (!result.success) {
    console.error("❌ Error en la configuración de variables de entorno:");
    result.error.issues.forEach((issue) => {
      console.error(`  - ${issue.path.join(".")}: ${issue.message}`);
    });
    throw new Error("Variables de entorno inválidas. Revisa la consola para más detalles.");
  }

  console.log("✅ Configuración de entorno válida");
  return result.data;
};

const envVars = validateEnv();
type envVars = z.infer<typeof envSchema>;

export { envSchema, envVars };
