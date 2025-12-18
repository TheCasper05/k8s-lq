import { useMetricsStore } from "@lq/stores";

/**
 * Composable for tracking metrics
 */
export function useMetrics() {
  const metricsStore = useMetricsStore();

  return {
    trackPageView: metricsStore.trackPageView,
    trackEvent: metricsStore.trackEvent,
    trackClick: metricsStore.trackClick,
    trackFormSubmit: metricsStore.trackFormSubmit,
    trackError: metricsStore.trackError,
    getSessionSummary: metricsStore.getSessionSummary,
  };
}

/**
 * Performance measurement utilities
 */
export class PerformanceMonitor {
  private marks: Map<string, number> = new Map();

  /**
   * Start measuring
   */
  start(label: string) {
    this.marks.set(label, performance.now());
  }

  /**
   * End measuring and return duration
   */
  end(label: string): number {
    const startTime = this.marks.get(label);
    if (!startTime) {
      console.warn(`No start mark found for "${label}"`);
      return 0;
    }

    const duration = performance.now() - startTime;
    this.marks.delete(label);

    return duration;
  }

  /**
   * Measure and log
   */
  measure(label: string): number {
    const duration = this.end(label);
    console.log(`[Performance] ${label}: ${duration.toFixed(2)}ms`);
    return duration;
  }
}

export const performanceMonitor = new PerformanceMonitor();
