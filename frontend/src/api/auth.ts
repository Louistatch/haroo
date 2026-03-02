import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

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

export function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  try {
    window.location.href = "/login";
  } catch (e) {}
}

// Attach access token on requests
api.interceptors.request.use((config) => {
  const token = getAccess();
  if (token && config && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Refresh flow
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
        return new Promise((resolve, reject) => {
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
        const newRefresh = r.data.refresh_token || refresh;
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

export async function login(phone: string, password: string) {
  const res = await api.post("/auth/login", { phone_number: phone, password });
  if (res.data && res.data.tokens) {
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
