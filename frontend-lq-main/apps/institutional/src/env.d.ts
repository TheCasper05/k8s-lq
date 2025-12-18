/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_GRAPHQL_ENDPOINT: string;
  readonly VITE_GRAPHQL_WS_ENDPOINT: string;
  readonly VITE_SENTRY_DSN: string;
  readonly VITE_ENVIRONMENT: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
