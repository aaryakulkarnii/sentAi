import axios from "axios";
import type { User } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  timeout: 30_000,
});

// Attach JWT from localStorage
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("sentinel_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auto-redirect on 401
api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401 && typeof window !== "undefined") {
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

// ── Auth endpoints ────────────────────────────────────────────────────────────
export const authApi = {
  login: (email: string, password: string) => {
    const form = new URLSearchParams();
    form.append("username", email);
    form.append("password", password);
    return api.post<TokenResponse>("/auth/token", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
  },
  me: () => api.get<User>("/auth/me"),
};

// ── Alert endpoints ──────────────────────────────────────────────────────────
export const alertsApi = {
  list: (params?: { severity?: string; status?: string; limit?: number }) =>
    api.get("/alerts", { params }),
  get: (id: string) => api.get(`/alerts/${id}`),
  update: (id: string, data: { status: string }) => api.patch(`/alerts/${id}`, data),
};

// ── Incident endpoints ────────────────────────────────────────────────────────
export const incidentsApi = {
  list: () => api.get("/incidents"),
  get: (id: string) => api.get(`/incidents/${id}`),
  create: (data: { title: string; description?: string; alert_ids?: string[] }) =>
    api.post("/incidents", data),
  update: (id: string, data: object) => api.patch(`/incidents/${id}`, data),
  addNote: (id: string, content: string) => api.post(`/incidents/${id}/notes`, { content }),
};

// ── Investigation endpoints ───────────────────────────────────────────────────
export const investigationsApi = {
  trigger: (incident_id: string) => api.post("/investigations/trigger", { incident_id }),
  get: (incident_id: string) => api.get(`/investigations/${incident_id}/latest`),
};

// ── MITRE endpoints ───────────────────────────────────────────────────────────
export const mitreApi = {
  list: () => api.get("/mitre/techniques"),
  get: (id: string) => api.get(`/mitre/techniques/${id}`),
};

// ── Threat intel endpoints ────────────────────────────────────────────────────
export const threatIntelApi = {
  searchIoc: (q: string) => api.get("/threat-intel/ioc/search", { params: { q } }),
  getCve: (id: string) => api.get(`/threat-intel/cve/${id}`),
};
