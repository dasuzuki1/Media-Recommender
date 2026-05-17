// API client for the Media Recommender backend.
// API_BASE is injected at deploy time by replacing the placeholder below
// with the API Gateway URL from `terraform output -raw api_url`.
window.API_BASE = window.API_BASE || "__API_BASE__";

const Api = {
  loginUrl() {
    return `${window.API_BASE}/login`;
  },

  async sync() {
    const res = await fetch(`${window.API_BASE}/sync`, {
      method: "POST",
      credentials: "include",
    });
    if (res.status === 401) throw new AuthError();
    if (!res.ok) throw new Error(`sync failed: ${res.status}`);
    return res.json();
  },

  async recommendations() {
    const res = await fetch(`${window.API_BASE}/recommendations`, {
      credentials: "include",
    });
    if (res.status === 401) throw new AuthError();
    if (!res.ok) throw new Error(`recommendations failed: ${res.status}`);
    return res.json();
  },
};

class AuthError extends Error {
  constructor() {
    super("not authenticated");
    this.name = "AuthError";
  }
}

window.Api = Api;
window.AuthError = AuthError;
