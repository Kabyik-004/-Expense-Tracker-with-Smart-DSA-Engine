import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { useToast } from "../components/shared/Toast";
import ThemeSwitch from "../components/shared/ThemeSwitch";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const { addToast } = useToast();
  const [form, setForm] = useState({ login: "", password: "" });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await login(form);

      if (res.success) {
        navigate("/dashboard");
      } else {
        addToast(res.message || "Login failed", "error");
      }
    } catch (err) {
      addToast(err.response?.data?.message || "Login failed", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950 px-4">
      <div className="w-full max-w-md bg-white dark:bg-gray-900 rounded-2xl shadow-lg p-8 relative">
        <div className="absolute top-4 right-4">
          <ThemeSwitch />
        </div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
          Welcome back
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mb-6">Sign in to your account</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Email or Username
            </label>
            <input
              type="text"
              required
              className="input-focus w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              value={form.login}
              onChange={(e) => setForm({ ...form, login: e.target.value })}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Password
            </label>
            <input
              type="password"
              required
              className="input-focus w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
            />
            <div className="text-right mt-1">
              <Link
                to="/forgot-password"
                className="link-underline text-xs text-indigo-600 dark:text-indigo-400 font-medium"
              >
                Forgot password?
              </Link>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50 font-medium"
          >
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-6">
          Don't have an account?{" "}
          <Link
            to="/register"
            className="link-underline text-indigo-600 font-medium"
          >
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
}