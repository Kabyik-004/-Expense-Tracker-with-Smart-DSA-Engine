import { useState } from "react";
import { Link } from "react-router-dom";
import { forgotPassword } from "../services/authService";
import { useToast } from "../components/shared/Toast";
import ThemeSwitch from "../components/shared/ThemeSwitch";

export default function ForgotPassword() {
  const { addToast } = useToast();
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [resetToken, setResetToken] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await forgotPassword({ email });
      if (res.success) {
        setResetToken(res.data.reset_token);
        addToast("Reset link generated successfully", "success");
      } else {
        addToast(res.message || "Failed to send reset link", "error");
      }
    } catch (err) {
      addToast(err.response?.data?.message || "Something went wrong. Please try again.", "error");
    } finally {
      setLoading(false);
    }
  };

  if (resetToken) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950 px-4">
        <div className="w-full max-w-md bg-white dark:bg-gray-900 rounded-2xl shadow-lg p-8 relative">
          <div className="absolute top-4 right-4">
            <ThemeSwitch />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">Reset link sent</h1>
          <p className="text-gray-500 dark:text-gray-400 mb-6">
            Use the link below to reset your password. It expires in 1 hour.
          </p>
          <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 mb-6 break-all">
            <p className="text-xs text-gray-400 dark:text-gray-500 mb-1">Your reset token:</p>
            <code className="text-sm text-indigo-600 dark:text-indigo-400 font-mono">{resetToken}</code>
          </div>
          <Link
            to={`/reset-password?token=${resetToken}`}
            className="block w-full text-center bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 font-medium"
          >
            Reset Password
          </Link>
          <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-4">
            <Link to="/login" className="link-underline text-indigo-600 font-medium">Back to login</Link>
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950 px-4">
      <div className="w-full max-w-md bg-white dark:bg-gray-900 rounded-2xl shadow-lg p-8 relative">
        <div className="absolute top-4 right-4">
          <ThemeSwitch />
        </div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">Forgot password</h1>
        <p className="text-gray-500 dark:text-gray-400 mb-6">Enter your email to receive a reset link</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email</label>
            <input
              type="email"
              required
              className="input-focus w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50 font-medium"
          >
            {loading ? "Sending..." : "Send Reset Link"}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-6">
          Remember your password?{" "}
          <Link to="/login" className="link-underline text-indigo-600 font-medium">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
