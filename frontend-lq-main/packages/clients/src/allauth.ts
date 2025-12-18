import type { LoginFormData, LoginResponse, RegisterResponse, RegisterFormData } from "@lq/types";

export interface AuthResponse {
  status: number;
  data: unknown;
  meta: {
    is_authenticated: boolean;
    access_token: string;
    refresh_token?: string;
  };
}

export interface AllauthClientOptions {
  baseUrl: string;
  tokenStorage?: Storage | null;
}

export interface AllauthClient {
  login(data: LoginFormData): Promise<LoginResponse>;
  logout(): Promise<AuthResponse>;
  signUp(data: RegisterFormData): Promise<RegisterResponse>;
  verifyEmail(key: string): Promise<RegisterResponse>;
  resendEmailVerification(): Promise<AuthResponse>;
  getSession(accessToken?: string): Promise<AuthResponse>;
  requestPasswordReset(email: string): Promise<AuthResponse>;
  resetPassword(data: unknown): Promise<AuthResponse>;
  resetPasswordWithKey(key: string, password: string, password2: string): Promise<AuthResponse>;
  changePassword(data: unknown): Promise<AuthResponse>;
  getConfig(): Promise<unknown>;
  getSessionToken(): string | null;
  loadConfig(): Promise<void>;
  getCSRFToken(): string | null;
  socialLogin(provider: "google" | "microsoft", accessToken?: string, idToken?: string): Promise<AuthResponse>;
  getSocialProviders(): Promise<{ id: string; name: string; client_id?: string; flows: string[] }[]>;
}

const ALLAUTH_ENDPOINTS = Object.freeze({
  // Meta
  CONFIG: "/config",

  // Auth
  LOGIN: "/auth/login",
  SESSION: "/auth/session",
  LOGOUT: "/auth/session",
  SIGNUP: "/auth/signup",
  REAUTHENTICATE: "/auth/reauthenticate",

  // Password
  REQUEST_PASSWORD_RESET: "/auth/password/request",
  RESET_PASSWORD: "/auth/password/reset",
  RESET_PASSWORD_KEY: "/auth/password/reset/key",
  CHANGE_PASSWORD: "/account/password/change",

  // Email
  VERIFY_EMAIL: "/auth/email/verify",
  RESEND_EMAIL_VERIFICATION: "/auth/resend-verification",
  EMAIL: "/account/email",

  // Social Auth
  PROVIDER_SIGNUP: "/auth/provider/signup",
  REDIRECT_TO_PROVIDER: "/auth/provider/redirect",
  PROVIDER_TOKEN: "/auth/provider/token",
  PROVIDERS: "/account/providers",
  SOCIAL_LOGIN: "/auth/social",

  // Sessions
  SESSIONS: "/auth/sessions",
});

export type RequestArgs = {
  method: string;
  path: string;
  data?: unknown;
  headers?: Record<string, string>;
};

export type NormalizedAuthError = Error & { status?: number; code?: string };

export function normalizeAllauthError(err: unknown): NormalizedAuthError {
  const baseError = err instanceof Error ? err : new Error(String(err));
  const anyErr = err as { [key: string]: unknown };

  const rootStatus = (anyErr.status as number | undefined) ?? undefined;
  const responseStatus = (anyErr.response as { status?: number } | undefined)?.status ?? undefined;
  const dataStatus = (anyErr.data as { status?: number } | undefined)?.status ?? undefined;
  const metaStatus = (anyErr.meta as { status?: number } | undefined)?.status ?? undefined;
  const statusCode = (anyErr as { statusCode?: number } | undefined)?.statusCode;

  const status = rootStatus ?? responseStatus ?? dataStatus ?? metaStatus ?? statusCode;

  const errorsArray =
    (anyErr.errors as { code?: string }[] | undefined) ??
    (anyErr.data as { errors?: { code?: string }[] } | undefined)?.errors ??
    undefined;
  const firstCode = errorsArray && errorsArray.length > 0 ? errorsArray[0]?.code : undefined;

  const normalized = baseError as NormalizedAuthError;

  if (typeof status === "number") {
    normalized.status = status;
  }

  if (typeof firstCode === "string") {
    normalized.code = firstCode;
  }

  return normalized;
}

export function createAllauthClient(options: AllauthClientOptions): AllauthClient {
  const baseUrl = options.baseUrl || "http://localhost:8000";
  const tokenStorage = options.tokenStorage ?? (typeof window !== "undefined" ? window.sessionStorage : null);

  async function request<T = AuthResponse>(args: RequestArgs): Promise<T> {
    const defaultHeaders: Record<string, string> = {
      "accept": "application/json",
      "Content-Type": "application/json",
    };

    const options: RequestInit = {
      method: args.method,
      headers: { ...defaultHeaders, ...(args.headers ?? {}) },
    };

    if (args.data) {
      options.body = JSON.stringify(args.data);
    }

    const url = `${baseUrl}/_allauth/browser/v1${args.path}`;
    const resp = await fetch(url, options);
    const result = (await resp.json()) as T;

    if (!resp.ok) {
      console.error("Allauth API error:", result);

      // Extract the error message from the response
      let errorMessage = "Allauth API request failed";
      const resultData = result as any;

      // Check if there are errors in the response
      if (resultData?.errors && Array.isArray(resultData.errors) && resultData.errors.length > 0) {
        // Use the first error message
        errorMessage = resultData.errors[0].message || errorMessage;
      } else if (
        resultData?.data?.errors &&
        Array.isArray(resultData.data.errors) &&
        resultData.data.errors.length > 0
      ) {
        // Check for errors in data.errors
        errorMessage = resultData.data.errors[0].message || errorMessage;
      }

      const error = new Error(errorMessage);
      Object.assign(error, { status: resp.status, ...result });
      throw error;
    }

    (result as AuthResponse).status = resp.status;
    return result;
  }

  async function login(data: LoginFormData): Promise<LoginResponse> {
    return await request({ method: "POST", path: ALLAUTH_ENDPOINTS.LOGIN, data });
  }

  async function logout(): Promise<AuthResponse> {
    const result = await request({ method: "DELETE", path: ALLAUTH_ENDPOINTS.SESSION });
    if (tokenStorage) {
      tokenStorage.removeItem("sessionToken");
    }
    return result;
  }

  async function getSession(accessToken?: string): Promise<AuthResponse> {
    const headers: Record<string, string> = {};

    // Add Authorization header if access token is provided
    if (accessToken) {
      headers["Authorization"] = `Bearer ${accessToken}`;
    }

    return await request({ method: "GET", path: ALLAUTH_ENDPOINTS.SESSION, headers });
  }

  async function signUp(data: RegisterFormData): Promise<RegisterResponse> {
    return await request({ method: "POST", path: ALLAUTH_ENDPOINTS.SIGNUP, data });
  }

  async function requestPasswordReset(email: string): Promise<AuthResponse> {
    return await request({ method: "POST", path: ALLAUTH_ENDPOINTS.REQUEST_PASSWORD_RESET, data: { email } });
  }

  async function resetPassword(data: unknown): Promise<AuthResponse> {
    return await request({ method: "POST", path: ALLAUTH_ENDPOINTS.RESET_PASSWORD, data });
  }

  async function resetPasswordWithKey(key: string, password: string, password2: string): Promise<AuthResponse> {
    return await request({
      method: "POST",
      path: ALLAUTH_ENDPOINTS.RESET_PASSWORD_KEY,
      data: { key, password, password2 },
    });
  }

  async function changePassword(data: unknown): Promise<AuthResponse> {
    return await request({ method: "POST", path: ALLAUTH_ENDPOINTS.CHANGE_PASSWORD, data });
  }

  async function verifyEmail(key: string): Promise<RegisterResponse> {
    return await request({ method: "POST", path: ALLAUTH_ENDPOINTS.VERIFY_EMAIL, data: { key } });
  }

  async function resendEmailVerification(): Promise<AuthResponse> {
    return await request({ method: "POST", path: ALLAUTH_ENDPOINTS.RESEND_EMAIL_VERIFICATION });
  }

  async function socialLogin(
    provider: "google" | "microsoft",
    accessToken?: string,
    idToken?: string,
  ): Promise<AuthResponse> {
    const data = {
      provider,
      ...(accessToken && { access_token: accessToken }),
      ...(idToken && { id_token: idToken }),
    };

    return await request({ method: "POST", path: ALLAUTH_ENDPOINTS.SOCIAL_LOGIN, data });
  }

  async function getSocialProviders(): Promise<{ id: string; name: string; client_id?: string; flows: string[] }[]> {
    const config = (await getConfig()) as {
      data?: { socialaccount?: { providers?: { id: string; name: string; client_id?: string; flows: string[] }[] } };
    };
    return config?.data?.socialaccount?.providers || [];
  }

  async function getConfig(): Promise<unknown> {
    return await request({ method: "GET", path: ALLAUTH_ENDPOINTS.CONFIG });
  }

  function getSessionToken(): string | null {
    return tokenStorage?.getItem("sessionToken") || null;
  }

  async function loadConfig() {
    try {
      await fetch(`${baseUrl}/_allauth/browser/v1${ALLAUTH_ENDPOINTS.CONFIG}`, {
        credentials: "include",
      });
    } catch (error) {
      console.error("Failed to load allauth config:", error);
    }
  }

  function getCSRFToken(): string | null {
    if (typeof document === "undefined") return null;

    const cookies = document.cookie.split(";");
    for (const cookie of cookies) {
      const [name, value] = cookie.trim().split("=");
      if (name === "csrftoken") {
        return decodeURIComponent(value);
      }
    }
    return null;
  }

  return {
    login,
    logout,
    getSession,
    signUp,
    socialLogin,
    getSocialProviders,

    requestPasswordReset,
    resetPassword,
    resetPasswordWithKey,
    changePassword,

    verifyEmail,
    resendEmailVerification,

    getConfig,
    getSessionToken,
    getCSRFToken,
    loadConfig,
  };
}
