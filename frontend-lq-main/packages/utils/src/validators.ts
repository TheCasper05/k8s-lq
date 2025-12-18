/**
 * Email validation
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Password strength validation
 * At least 8 characters, 1 uppercase, 1 lowercase, 1 number
 */
export function isStrongPassword(password: string): boolean {
  const minLength = password.length >= 8;
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumber = /[0-9]/.test(password);

  return minLength && hasUpperCase && hasLowerCase && hasNumber;
}

/**
 * URL validation
 */
export function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * Phone number validation (simple)
 */
export function isValidPhone(phone: string): boolean {
  const phoneRegex = /^\+?[1-9]\d{1,14}$/;
  return phoneRegex.test(phone.replace(/[\s-()]/g, ""));
}

/**
 * Required field validation
 */
export function isRequired(value: any): boolean {
  if (value === null || value === undefined) return false;
  if (typeof value === "string") return value.trim().length > 0;
  if (Array.isArray(value)) return value.length > 0;
  return true;
}

/**
 * Min length validation
 */
export function minLength(value: string, min: number): boolean {
  return value.length >= min;
}

/**
 * Max length validation
 */
export function maxLength(value: string, max: number): boolean {
  return value.length <= max;
}

/**
 * Number range validation
 */
export function inRange(value: number, min: number, max: number): boolean {
  return value >= min && value <= max;
}
