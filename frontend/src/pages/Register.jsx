import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { useToast } from "../components/shared/Toast";
import ThemeSwitch from "../components/shared/ThemeSwitch";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const { addToast } = useToast();
  const [form, setForm] = useState({
    username: "", email: "", password: "", full_name: "",
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await register(form);
      if (res.success) {
        navigate("/dashboard");
      } else {
        addToast(res.message || "Registration failed", "error");
      }
    } catch {
      addToast("Something went wrong. Please try again.", "error");
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
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">Create account</h1>
        <p className="text-gray-500 dark:text-gray-400 mb-6">Start tracking your expenses</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Username</label>
            <input type="text" required className="input-focus w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none bg-white dark:bg-gray-800 text-gray-900 dark:text-white" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
            <p className="mt-1 text-xs text-gray-400 dark:text-gray-500">3-80 characters, letters, numbers &amp; underscores only</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email</label>
            <input type="email" required className="input-focus w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none bg-white dark:bg-gray-800 text-gray-900 dark:text-white" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
            <p className="mt-1 text-xs text-gray-400 dark:text-gray-500">Enter a valid email address</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Full Name</label>
            <input type="text" className="input-focus w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none bg-white dark:bg-gray-800 text-gray-900 dark:text-white" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
            <p className="mt-1 text-xs text-gray-400 dark:text-gray-500">Optional, max 150 characters</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Password</label>
            <input type="password" required className="input-focus w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none bg-white dark:bg-gray-800 text-gray-900 dark:text-white" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
            <p className="mt-1 text-xs text-gray-400 dark:text-gray-500">8-128 characters, with 1 uppercase, 1 lowercase &amp; 1 digit</p>
          </div>
          <button type="submit" disabled={loading} className="w-full bg-emerald-600 text-white py-2 rounded-lg hover:bg-emerald-700 disabled:opacity-50 font-medium">
            {loading ? "Creating account..." : "Create account"}
          </button>
        </form>
        <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-6">
          Already have an account?{" "}
          <Link to="/login" className="link-underline text-emerald-600 dark:text-emerald-400 font-medium">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
