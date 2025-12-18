export function generateTestEmail(prefix = "test"): string {
  const timestamp = Date.now();
  const random = Math.floor(Math.random() * 1000);
  return `${prefix}-${timestamp}-${random}@test.com`;
}

export function generateTestName(prefix = "Test"): string {
  const timestamp = Date.now();
  return `${prefix}${timestamp}`;
}

export function generateUserData(role: "student" | "teacher" | "admin" = "student") {
  const timestamp = Date.now();
  const random = Math.floor(Math.random() * 1000);

  return {
    firstName: `Test${role}`,
    lastName: `User${timestamp}`,
    email: `${role}-${timestamp}-${random}@test.com`,
    password: "Test123!@#",
    confirmPassword: "Test123!@#",
    role,
  };
}

export function createUserData(overrides: Partial<ReturnType<typeof generateUserData>> = {}) {
  return {
    ...generateUserData(),
    ...overrides,
  };
}

export function sanitizeTestData(data: string): string {
  return data.replace(/[^\w@.-]/g, "").substring(0, 100);
}
