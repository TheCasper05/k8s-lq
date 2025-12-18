/**
 * Format date
 */
export function formatDate(date: Date | string, locale = "en-US", options?: Intl.DateTimeFormatOptions): string {
  const dateObj = typeof date === "string" ? new Date(date) : date;

  const defaultOptions: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "long",
    day: "numeric",
    ...options,
  };

  return new Intl.DateTimeFormat(locale, defaultOptions).format(dateObj);
}

/**
 * Format relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(date: Date | string, locale = "en-US"): string {
  const dateObj = typeof date === "string" ? new Date(date) : date;
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - dateObj.getTime()) / 1000);

  const rtf = new Intl.RelativeTimeFormat(locale, { numeric: "auto" });

  const intervals = [
    { label: "year", seconds: 31536000 },
    { label: "month", seconds: 2592000 },
    { label: "week", seconds: 604800 },
    { label: "day", seconds: 86400 },
    { label: "hour", seconds: 3600 },
    { label: "minute", seconds: 60 },
    { label: "second", seconds: 1 },
  ] as const;

  for (const interval of intervals) {
    const count = Math.floor(diffInSeconds / interval.seconds);
    if (count >= 1) {
      return rtf.format(-count, interval.label);
    }
  }

  return rtf.format(0, "second");
}

/**
 * Check if date is today
 */
export function isToday(date: Date | string): boolean {
  const dateObj = typeof date === "string" ? new Date(date) : date;
  const today = new Date();

  return (
    dateObj.getDate() === today.getDate() &&
    dateObj.getMonth() === today.getMonth() &&
    dateObj.getFullYear() === today.getFullYear()
  );
}

/**
 * Check if date is in the past
 */
export function isPast(date: Date | string): boolean {
  const dateObj = typeof date === "string" ? new Date(date) : date;
  return dateObj.getTime() < Date.now();
}

/**
 * Check if date is in the future
 */
export function isFuture(date: Date | string): boolean {
  const dateObj = typeof date === "string" ? new Date(date) : date;
  return dateObj.getTime() > Date.now();
}

/**
 * Add days to date
 */
export function addDays(date: Date, days: number): Date {
  const result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
}

/**
 * Subtract days from date
 */
export function subtractDays(date: Date, days: number): Date {
  return addDays(date, -days);
}
