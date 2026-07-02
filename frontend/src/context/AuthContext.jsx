import { useState, useEffect, useCallback } from "react";
import { AuthContext } from "../hooks/useAuth";
import * as authService from "../services/authService";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      authService
        .getProfile()
        .then((res) => {
          if (res.success) setUser(res.data.user);
        })
        .catch(() => {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = useCallback(async (credentials) => {
    const res = await authService.loginUser(credentials);
    if (res.success) {
      localStorage.setItem("access_token", res.data.access_token);
      localStorage.setItem("refresh_token", res.data.refresh_token);
      setUser(res.data.user);
    }
    return res;
  }, []);

  const register = useCallback(async (data) => {
    const res = await authService.registerUser(data);
    if (res.success) {
      localStorage.setItem("access_token", res.data.access_token);
      localStorage.setItem("refresh_token", res.data.refresh_token);
      setUser(res.data.user);
    }
    return res;
  }, []);

  const logout = useCallback(() => {
    authService.logoutUser().catch(() => {});
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, setUser }}>
      {children}
    </AuthContext.Provider>
  );
}
