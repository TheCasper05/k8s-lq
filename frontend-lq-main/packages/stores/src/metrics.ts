import { defineStore } from "pinia";
import { ref } from "vue";

export interface PageView {
  path: string;
  name: string;
  timestamp: Date;
  duration?: number;
}

export interface UserEvent {
  name: string;
  properties: Record<string, any>;
  timestamp: Date;
}

/**
 * Metrics store
 * Tracks user interactions and page views for analytics
 */
export const useMetricsStore = defineStore("metrics", () => {
  const pageViews = ref<PageView[]>([]);
  const events = ref<UserEvent[]>([]);
  const currentPageStartTime = ref<Date | null>(null);

  function trackPageView(pageInfo: { path: string; name: string; params?: Record<string, any> }) {
    // Calculate duration of previous page
    if (currentPageStartTime.value && pageViews.value.length > 0) {
      const lastPage = pageViews.value[pageViews.value.length - 1];
      lastPage.duration = Date.now() - currentPageStartTime.value.getTime();
    }

    // Track new page view
    const pageView: PageView = {
      path: pageInfo.path,
      name: pageInfo.name,
      timestamp: new Date(),
    };

    pageViews.value.push(pageView);
    currentPageStartTime.value = new Date();

    // Send to analytics service (e.g., Sentry, Google Analytics)
    sendToAnalytics("page_view", {
      page_path: pageInfo.path,
      page_name: pageInfo.name,
      page_params: pageInfo.params,
    });
  }

  function trackEvent(eventName: string, properties: Record<string, any> = {}) {
    const event: UserEvent = {
      name: eventName,
      properties,
      timestamp: new Date(),
    };

    events.value.push(event);

    // Send to analytics service
    sendToAnalytics(eventName, properties);
  }

  function trackClick(element: string, properties: Record<string, any> = {}) {
    trackEvent("click", { element, ...properties });
  }

  function trackFormSubmit(formName: string, properties: Record<string, any> = {}) {
    trackEvent("form_submit", { form_name: formName, ...properties });
  }

  function trackError(error: Error, context: Record<string, any> = {}) {
    trackEvent("error", {
      error_message: error.message,
      error_stack: error.stack,
      ...context,
    });

    // Also send to Sentry
    if (typeof window !== "undefined" && (window as any).Sentry) {
      (window as any).Sentry.captureException(error, { extra: context });
    }
  }

  function sendToAnalytics(eventName: string, properties: Record<string, any>) {
    // Send to your analytics service
    // Example: Google Analytics
    if (typeof window !== "undefined" && (window as any).gtag) {
      (window as any).gtag("event", eventName, properties);
    }

    // Example: Sentry breadcrumb
    if (typeof window !== "undefined" && (window as any).Sentry) {
      (window as any).Sentry.addBreadcrumb({
        category: "analytics",
        message: eventName,
        data: properties,
        level: "info",
      });
    }

    // Log in development
    if (import.meta.env.DEV || process.env.NODE_ENV === "development") {
      console.log("[Analytics]", eventName, properties);
    }
  }

  function getSessionSummary() {
    return {
      totalPageViews: pageViews.value.length,
      totalEvents: events.value.length,
      averagePageDuration: pageViews.value.reduce((sum, pv) => sum + (pv.duration || 0), 0) / pageViews.value.length,
      sessionDuration: currentPageStartTime.value ? Date.now() - pageViews.value[0]?.timestamp.getTime() : 0,
    };
  }

  return {
    pageViews,
    events,
    trackPageView,
    trackEvent,
    trackClick,
    trackFormSubmit,
    trackError,
    getSessionSummary,
  };
});
