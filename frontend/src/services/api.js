import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api",
  headers: { "Content-Type": "application/json" },
  timeout: 60000,
});

let isRefreshing = false;
let failedQueue = [];

function processQueue(error, token = null) {
  failedQueue.forEach((prom) => {
    if (error) prom.reject(error);
    else prom.resolve(token);
  });
  failedQueue = [];
}

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

function isRetryable(error) {
  if (!error.response) return error.code === "ECONNABORTED" || error.code === "ERR_NETWORK";
  return error.response.status === 502 || error.response.status === 503;
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (!originalRequest) return Promise.reject(error);

    // — Retry on 502 / 503 / connection drop (transient — cold start) —
    if (isRetryable(error) && !originalRequest._retryCount) {
      originalRequest._retryCount = (originalRequest._retryCount || 0) + 1;
      if (originalRequest._retryCount <= 2) {
        const delay = originalRequest._retryCount === 1 ? 5000 : 10000;
        await new Promise((r) => setTimeout(r, delay));
        return api(originalRequest);
      }
    }

    // — Token refresh on 401 —
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return api(originalRequest);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = localStorage.getItem("refresh_token");
      if (refreshToken) {
        try {
          const baseURL = import.meta.env.VITE_API_URL || "/api";
          const res = await axios.post(
            `${baseURL}/auth/refresh`,
            {},
            { headers: { Authorization: `Bearer ${refreshToken}` } }
          );
          const newToken = res.data.data?.access_token;
          if (newToken) {
            localStorage.setItem("access_token", newToken);
            processQueue(null, newToken);
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            return api(originalRequest);
          }
        } catch (refreshError) {
          processQueue(refreshError, null);
        } finally {
          isRefreshing = false;
        }
      } else {
        isRefreshing = false;
      }

      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      window.location.href = "/login";
      return Promise.reject(error);
    }

    return Promise.reject(error);
  }
);

export function startKeepAlive(interval = 300000) {
  const baseURL = import.meta.env.VITE_API_URL || "/api";
  const id = setInterval(async () => {
    try {
      await axios.get(`${baseURL}/health`, { timeout: 10000 });
    } catch {
      /* keepalive errors are non-critical */
    }
  }, interval);
  return id;
}

export default api;
