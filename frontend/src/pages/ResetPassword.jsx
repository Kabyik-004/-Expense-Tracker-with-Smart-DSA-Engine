import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { resetPassword } from "../services/authService";
import { useToast } from "../components/shared/Toast";
import ThemeSwitch from "../components/shared/ThemeSwitch";

export default function ResetPassword() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { addToast } = useToast();
  const [form, setForm] = useState({
    token: searchParams.get("token") || "",
    new_password: "",
    confirm_password: "",
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (form.new_password !== form.confirm_password) {
      addToast("Passwords do not match", "error");
      return;
    }
    setLoading(true);
    try {
      const res = await resetPassword({ token: form.token, new_password: form.new_password });
      if (res.success) {
        addToast("Password reset successfully. Please sign in.", "success");
        navigate("/login");
      } else {
        addToast(res.message || "Failed to reset password", "error");
      }
    } catch (err) {
      addToast(err.response?.data?.message || "Something went wrong. Please try again.", "error");
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
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">Reset password</h1>
        <p className="text-gray-500 dark:text-gray-400 mb-6">Enter your new password</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Reset Token</label>
            <input
              type="text"
              required
              className="input-focus w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none bg-white dark:bg-gray-800 text-gray-900 dark:text-white font-mono text-sm"
              value={form.token}
              onChange={(e) => setForm({ ...form, token: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">New Password</label>
            <input
              type="password"
              required
              className="input-focus w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              value={form.new_password}
              onChange={(e) => setForm({ ...form, new_password: e.target.value })}
            />
            <p className="mt-1 text-xs text-gray-400 dark:text-gray-500">8-128 characters, with 1 uppercase, 1 lowercase &amp; 1 digit</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Confirm Password</label>
            <input
              type="password"
              required
              className="input-focus w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              value={form.confirm_password}
              onChange={(e) => setForm({ ...form, confirm_password: e.target.value })}
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-emerald-600 text-white py-2 rounded-lg hover:bg-emerald-700 disabled:opacity-50 font-medium"
          >
            {loading ? "Resetting..." : "Reset Password"}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-6">
          <Link to="/login" className="link-underline text-emerald-600 dark:text-emerald-400 font-medium">Back to login</Link>
        </p>
      </div>
    </div>
  );
}
