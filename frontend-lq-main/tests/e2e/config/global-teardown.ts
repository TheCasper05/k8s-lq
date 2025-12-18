import type { FullConfig } from "@playwright/test";

function globalTeardown(_config: FullConfig) {
  // Global teardown logic can be added here
}

export default globalTeardown;
