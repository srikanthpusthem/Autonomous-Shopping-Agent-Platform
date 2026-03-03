import type { AuthResponse, Profile, RunResponse } from "../types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init: RequestInit = {}, token?: string): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
  });

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      detail = body.detail ?? detail;
    } catch {
      // ignore parse failures
    }
    throw new Error(detail);
  }

  return response.json() as Promise<T>;
}

export const api = {
  register(email: string, password: string) {
    return request<AuthResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  },
  login(email: string, password: string) {
    return request<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  },
  getProfiles(token: string) {
    return request<Profile[]>("/profiles", {}, token);
  },
  createProfile(token: string, payload: Partial<Profile> & { name: string }) {
    return request<Profile>(
      "/profiles",
      {
        method: "POST",
        body: JSON.stringify({
          name: payload.name,
          budget_min: payload.budget_min,
          budget_max: payload.budget_max,
          preferred_brands: payload.preferred_brands ?? [],
          avoid_brands: payload.avoid_brands ?? [],
          shipping_speed_preference: payload.shipping_speed_preference ?? "balanced",
          use_case_tags: payload.use_case_tags ?? [],
        }),
      },
      token,
    );
  },
  createRun(token: string, profileId: string, prompt: string) {
    return request<RunResponse>(
      "/runs",
      {
        method: "POST",
        body: JSON.stringify({ profile_id: profileId, prompt }),
      },
      token,
    );
  },
  getRun(token: string, runId: string) {
    return request<RunResponse>(`/runs/${runId}`, {}, token);
  },
  postFeedback(
    token: string,
    payload: {
      profile_id: string;
      run_id?: string;
      feedback_type: "pick" | "not_interested" | "preference";
      product_provider?: string;
      product_id?: string;
      note?: string;
      metadata?: Record<string, unknown>;
    },
  ) {
    return request<{ message: string }>(
      "/feedback",
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      token,
    );
  },
};

export function buildRunEventsWsUrl(runId: string): string {
  const wsBase = import.meta.env.VITE_WS_BASE_URL ?? "ws://localhost:8000";
  return `${wsBase}/runs/${runId}/events`;
}
