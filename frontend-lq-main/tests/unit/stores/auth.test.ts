import { describe, it, expect, beforeEach, vi } from "vitest";
import { setActivePinia, createPinia } from "pinia";
import { useAuthStore } from "@lq/stores";

describe("Auth Store", () => {
  beforeEach(() => {
    // Create a fresh pinia instance for each test
    setActivePinia(createPinia());

    // Mock localStorage
    global.localStorage = {
      getItem: vi.fn(),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn(),
      length: 0,
      key: vi.fn(),
    };
  });

  it("should initialize with no user", () => {
    const store = useAuthStore();
    expect(store.user).toBeNull();
    expect(store.token).toBeNull();
    expect(store.isAuthenticated).toBe(false);
  });

  it("should set user on login", async () => {
    const store = useAuthStore();

    await store.login("test@example.com", "password123");

    expect(store.user).toBeDefined();
    expect(store.user?.email).toBe("test@example.com");
    expect(store.token).toBeTruthy();
    expect(store.isAuthenticated).toBe(true);
  });

  it("should clear user on logout", async () => {
    const store = useAuthStore();

    await store.login("test@example.com", "password123");
    expect(store.isAuthenticated).toBe(true);

    await store.logout();
    expect(store.user).toBeNull();
    expect(store.token).toBeNull();
    expect(store.isAuthenticated).toBe(false);
  });

  it("should check user roles", async () => {
    const store = useAuthStore();

    await store.login("test@example.com", "password123");

    expect(store.hasRole("teacher")).toBe(true);
    expect(store.hasRole("admin")).toBe(false);
    expect(store.hasAnyRole(["teacher", "student"])).toBe(true);
    expect(store.hasAnyRole(["admin", "moderator"])).toBe(false);
  });
});
