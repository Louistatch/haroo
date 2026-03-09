import axios from "axios";

const BASE_URL = "/api/v1";

const api = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
});

function getAccess() {
  return localStorage.getItem("access_token");
}

function getRefresh() {
  return localStorage.getItem("refresh_token");
}

export function setTokens(access?: string, refresh?: string) {
  if (access) localStorage.setItem("access_token", access);
  if (refresh) localStorage.setItem("refresh_token", refresh);
}

export function clearTokens() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

export function isLoggedIn() {
  return Boolean(getAccess());
}

export function logout() {
  clearTokens();
  try {
    window.location.href = "/login";
  } catch (e) {}
}

api.interceptors.request.use((config) => {
  const token = getAccess();
  if (token && config && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let isRefreshing = false;
let subscribers: Array<(token: string) => void> = [];

function onRefreshed(token: string) {
  subscribers.forEach((cb) => cb(token));
  subscribers = [];
}

function addSubscriber(cb: (token: string) => void) {
  subscribers.push(cb);
}

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (!original) return Promise.reject(error);
    if (error.response && error.response.status === 401 && !original._retry) {
      original._retry = true;
      if (isRefreshing) {
        return new Promise((resolve) => {
          addSubscriber((token: string) => {
            original.headers.Authorization = `Bearer ${token}`;
            resolve(api(original));
          });
        });
      }
      isRefreshing = true;
      try {
        const refresh = getRefresh();
        if (!refresh) throw new Error("No refresh token");
        const r = await axios.post(`${BASE_URL}/auth/refresh-token`, { refresh_token: refresh });
        const newAccess = r.data.access_token;
        const newRefresh = r.data.refresh_token;
        setTokens(newAccess, newRefresh);
        onRefreshed(newAccess);
        return api(original);
      } catch (e) {
        logout();
        return Promise.reject(e);
      } finally {
        isRefreshing = false;
      }
    }
    return Promise.reject(error);
  }
);

export async function login(phone_number: string, password: string) {
  const res = await api.post("/auth/login", { phone_number, password });
  if (res.data?.tokens) {
    setTokens(res.data.tokens.access_token, res.data.tokens.refresh_token);
  }
  return res.data;
}

export async function loginEmail(email: string, password: string) {
  const res = await api.post("/auth/login-email", { email, password });
  if (res.data?.tokens) {
    setTokens(res.data.tokens.access_token, res.data.tokens.refresh_token);
  }
  return res.data;
}

export async function registerEmail(params: {
  first_name?: string;
  last_name?: string;
  email: string;
  password: string;
  password_confirm: string;
  user_type: string;
}) {
  const res = await api.post("/auth/register-email", params);
  if (res.data?.tokens) {
    setTokens(res.data.tokens.access_token, res.data.tokens.refresh_token);
  }
  return res.data;
}

export async function register(payload: any) {
  const res = await api.post("/auth/register", payload);
  return res.data;
}

export async function me() {
  const res = await api.get("/users/me");
  return res.data;
}

export async function updateProfile(data: any) {
  const res = await api.patch("/users/me", data);
  return res.data;
}

export async function changePassword(old_password: string, new_password: string, new_password_confirm: string) {
  const res = await api.post("/users/me/change-password", { old_password, new_password, new_password_confirm });
  return res.data;
}

export async function verifySms(phone_number: string, code: string) {
  const res = await api.post("/auth/verify-sms", { phone_number, code });
  if (res.data?.tokens) {
    setTokens(res.data.tokens.access_token, res.data.tokens.refresh_token);
  }
  return res.data;
}

export async function logoutApi() {
  try {
    const token = getAccess();
    if (token) {
      // Appel direct sans intercepteur pour éviter une boucle de refresh
      await axios.post(`${BASE_URL}/auth/logout`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });
    }
  } catch (e) {
    // Ignorer les erreurs (token expiré, réseau, etc.)
  } finally {
    clearTokens();
  }
}

export async function forgotPassword(email: string) {
  const res = await api.post("/auth/forgot-password", { email });
  return res.data;
}

export async function resetPassword(token: string, new_password: string, new_password_confirm: string) {
  const res = await api.post("/auth/reset-password", { token, new_password, new_password_confirm });
  return res.data;
}

export async function verifyEmail(token: string) {
  const res = await api.post("/auth/verify-email", { token });
  return res.data;
}

export async function resendVerificationEmail() {
  const res = await api.post("/auth/resend-verification");
  return res.data;
}

export async function chooseProfile(user_type: string) {
  const res = await api.post("/auth/choose-profile", { user_type });
  if (res.data?.tokens) {
    setTokens(res.data.tokens.access_token, res.data.tokens.refresh_token);
  }
  return res.data;
}

export async function supabaseExchange(access_token: string) {
  const res = await api.post("/auth/supabase-exchange", { access_token });
  if (res.data?.tokens) {
    setTokens(res.data.tokens.access_token, res.data.tokens.refresh_token);
  }
  return res.data;
}

export async function firebaseExchange(id_token: string) {
  const res = await api.post("/auth/firebase-exchange", { id_token });
  if (res.data?.tokens) {
    setTokens(res.data.tokens.access_token, res.data.tokens.refresh_token);
  }
  return res.data;
}

export async function getAgronomists(params?: Record<string, string>) {
  const query = params ? "?" + new URLSearchParams(params).toString() : "";
  const res = await api.get(`/agronomists${query}`);
  return res.data;
}

export async function getAgronomistDetail(id: number) {
  const res = await api.get(`/agronomists/${id}`);
  return res.data;
}

export default api;
