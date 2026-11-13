// api.js — every call to the FastAPI backend lives in this one file.
// ANALOGY: the app's "phone book". Components never write URLs themselves,
// they just call api.getSummary(), api.chat(...), etc.

async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    // FastAPI puts error messages in `detail`.
    const detail = typeof data.detail === "string" ? data.detail : `Request failed (${response.status})`;
    throw new Error(detail);
  }
  return data;
}

export const api = {
  health: () => request("/health"),
  seed: () => request("/api/seed", { method: "POST" }),
  getSummary: () => request("/api/analytics/summary"),
  getMerchantSuccessRates: () => request("/api/analytics/merchant-success-rates"),
  getTopMerchants: (limit = 5) => request(`/api/analytics/top-merchants?limit=${limit}`),
  getFailureReasons: () => request("/api/analytics/failure-reasons"),
  chat: (question) => request("/api/chat", { method: "POST", body: JSON.stringify({ question }) }),
};
