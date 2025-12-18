import { useToast } from "primevue/usetoast";

export type ToastSeverity = "success" | "info" | "warn" | "error";

export interface ToastOptions {
  /**
   * Translation key for the summary (title)
   */
  summaryKey?: string;
  /**
   * Translation key for the detail (message)
   */
  detailKey?: string;
  /**
   * Direct summary text (overrides summaryKey)
   */
  summary?: string;
  /**
   * Direct detail text (overrides detailKey)
   */
  detail?: string;
  /**
   * Duration in milliseconds
   * @default 3000
   */
  life?: number;
  /**
   * Whether the toast can be closed
   * @default true
   */
  closable?: boolean;
}

/**
 * Composable for showing toast notifications throughout the app
 * Supports both translation keys and direct text
 */
export const useAppToast = () => {
  const toast = useToast();
  const { t } = useI18n();

  /**
   * Show a toast notification
   */
  const show = (severity: ToastSeverity, options: ToastOptions) => {
    const summary = options.summary || (options.summaryKey ? t(options.summaryKey) : "");
    const detail = options.detail || (options.detailKey ? t(options.detailKey) : "");

    toast.add({
      severity,
      summary,
      detail,
      life: options.life ?? 3000,
      closable: options.closable ?? true,
    });
  };

  /**
   * Show success toast
   */
  const success = (options: ToastOptions | string) => {
    if (typeof options === "string") {
      show("success", {
        summaryKey: "common.success",
        detail: options,
      });
    } else {
      show("success", {
        summaryKey: options.summaryKey || "common.success",
        ...options,
      });
    }
  };

  /**
   * Show error toast
   */
  const error = (options: ToastOptions | string) => {
    if (typeof options === "string") {
      show("error", {
        summaryKey: "common.error",
        detail: options,
        life: 5000,
      });
    } else {
      show("error", {
        summaryKey: options.summaryKey || "common.error",
        life: options.life ?? 5000,
        ...options,
      });
    }
  };

  /**
   * Show warning toast
   */
  const warning = (options: ToastOptions | string) => {
    if (typeof options === "string") {
      show("warn", {
        summaryKey: "common.warning",
        detail: options,
      });
    } else {
      show("warn", {
        summaryKey: options.summaryKey || "common.warning",
        ...options,
      });
    }
  };

  /**
   * Show info toast
   */
  const info = (options: ToastOptions | string) => {
    if (typeof options === "string") {
      show("info", {
        summaryKey: "common.info",
        detail: options,
      });
    } else {
      show("info", {
        summaryKey: options.summaryKey || "common.info",
        ...options,
      });
    }
  };

  // Shortcuts for common auth scenarios
  const auth = {
    loginSuccess: () =>
      success({
        summaryKey: "common.success",
        detailKey: "auth.loginSuccessful",
      }),
    loginError: (detail?: string) =>
      error({
        summaryKey: "common.error",
        detail: detail || t("auth.loginError"),
        life: 5000,
      }),
    registerSuccess: () =>
      success({
        summaryKey: "common.success",
        detailKey: "auth.registerSuccessful",
      }),
    validationError: () =>
      warning({
        summaryKey: "common.validationError",
        detailKey: "auth.fillAllFields",
      }),
    passwordUpdated: () =>
      success({
        summaryKey: "profile.passwordUpdated",
        detailKey: "profile.passwordUpdatedDetail",
      }),
  };

  // Shortcuts for common profile scenarios
  const profile = {
    updated: () =>
      success({
        summaryKey: "profile.profileUpdated",
        detailKey: "profile.profileUpdatedDetail",
      }),
    updateError: (detail?: string) =>
      error({
        summaryKey: "common.error",
        detail: detail || t("profile.updateError"),
      }),
  };

  return {
    // Generic methods
    show,
    success,
    error,
    warning,
    info,

    // Contextual shortcuts
    auth,
    profile,
  };
};
