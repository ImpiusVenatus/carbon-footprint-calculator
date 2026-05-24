import { clearTokens, getRefreshToken, setTokens } from "./auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type?: string;
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
  }
}

let refreshPromise: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  const refresh = getRefreshToken();
  if (!refresh) return null;

  if (!refreshPromise) {
    refreshPromise = (async () => {
      try {
        const res = await fetch(`${API_URL}/api/v1/auth/refresh`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh_token: refresh }),
        });
        if (!res.ok) {
          clearTokens();
          return null;
        }
        const data = (await res.json()) as TokenPair;
        setTokens(data.access_token, data.refresh_token);
        return data.access_token;
      } catch {
        clearTokens();
        return null;
      } finally {
        refreshPromise = null;
      }
    })();
  }

  return refreshPromise;
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null,
  retried = false,
): Promise<T> {
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = headers["Content-Type"] || "application/json";
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (res.status === 401 && token && !retried && !path.startsWith("/api/v1/auth/")) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      return request(path, options, newToken, true);
    }
  }

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      // ignore
    }
    throw new ApiError(String(detail), res.status);
  }

  if (res.status === 204) {
    return undefined as T;
  }

  return res.json();
}

async function fetchExportReport(token: string, year: number): Promise<Blob> {
  const res = await fetch(
    `${API_URL}/api/v1/reports/export?year=${year}&format=csv`,
    { headers: { Authorization: `Bearer ${token}` } },
  );
  if (res.status === 401) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      return fetchExportReport(newToken, year);
    }
  }
  if (!res.ok) throw new ApiError("Export failed", res.status);
  return res.blob();
}

export const api = {
  health: () => request<{ status: string }>("/health"),

  register: (data: {
    organization_name: string;
    email: string;
    password: string;
    industry?: string;
  }) =>
    request<TokenPair>("/api/v1/auth/register", { method: "POST", body: JSON.stringify(data) }),

  login: (data: { email: string; password: string }) =>
    request<TokenPair>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  me: (token: string) => request("/api/v1/auth/me", {}, token),

  factors: (
    token: string,
    params?: { scope?: string; category?: string; year?: number; region?: string },
  ) => {
    const qs = new URLSearchParams();
    if (params?.scope) qs.set("scope", params.scope);
    if (params?.category) qs.set("category", params.category);
    if (params?.year) qs.set("year", String(params.year));
    if (params?.region) qs.set("region", params.region);
    const query = qs.toString();
    return request(`/api/v1/factors${query ? `?${query}` : ""}`, {}, token);
  },

  createFactor: (token: string, data: Record<string, unknown>) =>
    request("/api/v1/factors", { method: "POST", body: JSON.stringify(data) }, token),

  activities: (token: string) => request("/api/v1/activities", {}, token),

  createActivity: (token: string, data: Record<string, unknown>) =>
    request("/api/v1/activities", { method: "POST", body: JSON.stringify(data) }, token),

  updateActivity: (token: string, id: string, data: Record<string, unknown>) =>
    request(`/api/v1/activities/${id}`, { method: "PUT", body: JSON.stringify(data) }, token),

  deleteActivity: (token: string, id: string) =>
    request(`/api/v1/activities/${id}`, { method: "DELETE" }, token),

  importPreview: (token: string, file: File, year = 2024, region = "UK") => {
    const form = new FormData();
    form.append("file", file);
    return request(
      `/api/v1/activities/import/preview?year=${year}&region=${region}`,
      { method: "POST", body: form },
      token,
    );
  },

  importConfirm: (token: string, rows: Record<string, unknown>[]) =>
    request(
      "/api/v1/activities/import/confirm",
      { method: "POST", body: JSON.stringify({ rows }) },
      token,
    ),

  emissionsSummary: (token: string, year: number) =>
    request(`/api/v1/emissions/summary?year=${year}`, {}, token),

  targets: (token: string) => request("/api/v1/targets", {}, token),

  createTarget: (token: string, data: Record<string, unknown>) =>
    request("/api/v1/targets", { method: "POST", body: JSON.stringify(data) }, token),

  exportReport: (token: string, year: number) => fetchExportReport(token, year),

  auditLog: (token: string, limit = 50) =>
    request(`/api/v1/audit-log?limit=${limit}`, {}, token),
};
