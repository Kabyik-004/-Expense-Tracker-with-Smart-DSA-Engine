import { useState, useMemo } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import {
  FiLock, FiEye, FiEyeOff, FiCheck, FiX, FiArrowLeft, FiShield, FiCheckCircle,
} from "react-icons/fi";
import { resetPassword } from "../services/authService";
import { useToast } from "../components/shared/Toast";
import ThemeSwitch from "../components/shared/ThemeSwitch";

const REQUIREMENTS = [
  { label: "At least 8 characters", test: (pw) => pw.length >= 8 },
  { label: "One uppercase letter", test: (pw) => /[A-Z]/.test(pw) },
  { label: "One lowercase letter", test: (pw) => /[a-z]/.test(pw) },
  { label: "One number", test: (pw) => /\d/.test(pw) },
  { label: "One special character", test: (pw) => /[!@#$%^&*(),.?":{}|<>_\-]/.test(pw) },
];

const STRENGTH_LABELS = ["", "Weak", "Fair", "Good", "Strong", "Very strong"];

function getStrength(password) {
  if (!password) return 0;
  return REQUIREMENTS.filter((r) => r.test(password)).length;
}

function StrengthBar({ score }) {
  if (score === 0) return null;
  const colors = ["", "bg-red-500", "bg-orange-500", "bg-yellow-500", "bg-emerald-400", "bg-emerald-500"];
  const bars = [1, 2, 3, 4, 5];
  return (
    <div className="flex items-center gap-2 mt-2" role="meter" aria-valuenow={score} aria-valuemin={0} aria-valuemax={5} aria-label={`Password strength: ${STRENGTH_LABELS[score]}`}>
      <div className="flex gap-1 flex-1">
        {bars.map((i) => (
          <div
            key={i}
            className={`h-1.5 flex-1 rounded-full transition-colors duration-300 ${
              i <= score ? colors[score] : "bg-gray-200 dark:bg-gray-700"
            }`}
          />
        ))}
      </div>
      <span className={`text-xs font-medium ${
        score <= 2 ? "text-red-500" : score <= 3 ? "text-yellow-600 dark:text-yellow-400" : "text-emerald-600 dark:text-emerald-400"
      }`}>
        {STRENGTH_LABELS[score]}
      </span>
    </div>
  );
}

export default function ResetPassword() {
  const navigate = useNavigate();
  const location = useLocation();
  const { addToast } = useToast();

  const state = location.state || {};
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showNew, setShowNew] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [resetDone, setResetDone] = useState(false);
  const [fieldError, setFieldError] = useState("");

  const strength = useMemo(() => getStrength(newPassword), [newPassword]);
  const allMet = strength === REQUIREMENTS.length;
  const passwordsMatch = confirmPassword === "" || newPassword === confirmPassword;
  const canSubmit = allMet && passwordsMatch && newPassword === confirmPassword && !loading && !resetDone;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFieldError("");

    if (!state.email || !state.otp) {
      addToast("Session expired. Please start from forgot password.", "error");
      navigate("/forgot-password");
      return;
    }

    if (newPassword !== confirmPassword) {
      setFieldError("Passwords do not match");
      return;
    }

    if (!allMet) {
      setFieldError("Meet all password requirements first");
      return;
    }

    setLoading(true);
    try {
      const res = await resetPassword({
        email: state.email,
        otp: state.otp,
        new_password: newPassword,
      });
      if (res.success) {
        setResetDone(true);
        setTimeout(() => navigate("/login", { replace: true }), 2200);
      } else {
        setFieldError(res.message || "Failed to reset password");
      }
    } catch (err) {
      setFieldError(err.response?.data?.message || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  if (!state.email || !state.otp) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950 px-4">
        <div className="w-full max-w-md bg-white dark:bg-gray-900 rounded-2xl shadow-lg p-8 text-center animate-page-enter">
          <FiShield className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
          <h1 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Session expired</h1>
          <p className="text-gray-500 dark:text-gray-400 mb-6">
            Your password reset session has expired. Please start again from the forgot password page.
          </p>
          <Link
            to="/forgot-password"
            className="inline-flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400 font-medium link-underline"
          >
            <FiArrowLeft className="w-3.5 h-3.5" />
            Go to forgot password
          </Link>
        </div>
      </div>
    );
  }

  if (resetDone) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950 px-4">
        <div className="w-full max-w-md bg-white dark:bg-gray-900 rounded-2xl shadow-lg p-8 text-center animate-page-enter" role="alert" aria-live="polite">
          <div className="flex justify-center mb-4">
            <div className="relative">
              <div className="flex items-center justify-center w-20 h-20">
                <div className="absolute inset-0 rounded-full bg-emerald-100 dark:bg-emerald-900/40 animate-success-ring" />
                <div className="absolute inset-2 rounded-full bg-emerald-200 dark:bg-emerald-800/40 animate-success-ring" style={{ animationDelay: "0.15s" }} />
                <div className="relative z-10 w-12 h-12 rounded-full bg-gradient-to-br from-emerald-400 to-green-500 flex items-center justify-center shadow-lg shadow-emerald-500/30 animate-success-check">
                  <FiCheckCircle className="w-6 h-6 text-white" />
                </div>
              </div>
            </div>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Password reset
          </h1>
          <p className="text-gray-500 dark:text-gray-400">
            Your password has been updated. Redirecting to sign in...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950 px-4 py-8">
      <div className="w-full max-w-md bg-white dark:bg-gray-900 rounded-2xl shadow-lg p-8 relative animate-page-enter">
        <div className="absolute top-4 right-4">
          <ThemeSwitch />
        </div>

        <div className="flex items-center gap-3 mb-1">
          <FiLock className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Reset password
          </h1>
        </div>

        <p className="text-gray-500 dark:text-gray-400 mb-1">
          Create a new password for
        </p>
        <p className="text-sm font-medium text-gray-900 dark:text-white mb-6 break-all">
          {state.email}
        </p>

        <form onSubmit={handleSubmit} noValidate className="space-y-4">
          <div>
            <label htmlFor="new-password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              New Password
            </label>
            <div className="relative">
              <input
                id="new-password"
                type={showNew ? "text" : "password"}
                required
                minLength={8}
                maxLength={128}
                placeholder="Enter new password"
                className="input-focus w-full px-3 py-2.5 pr-10 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500"
                value={newPassword}
                onChange={(e) => { setNewPassword(e.target.value); setFieldError(""); }}
                autoFocus
                autoComplete="new-password"
              />
              <button
                type="button"
                onClick={() => setShowNew(!showNew)}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                tabIndex={-1}
                aria-label={showNew ? "Hide password" : "Show password"}
              >
                {showNew ? <FiEyeOff className="w-4 h-4" /> : <FiEye className="w-4 h-4" />}
              </button>
            </div>

            <StrengthBar score={strength} />

            <div aria-live="polite" aria-atomic="true" className="sr-only">
              Password strength: {STRENGTH_LABELS[strength]}
            </div>

            <ul className="mt-3 space-y-1">
              {REQUIREMENTS.map((req) => {
                const met = req.test(newPassword);
                return (
                  <li
                    key={req.label}
                    className={`flex items-center gap-2 text-xs transition-colors duration-200 ${
                      met
                        ? "text-emerald-600 dark:text-emerald-400"
                        : "text-gray-400 dark:text-gray-500"
                    }`}
                  >
                    {met ? <FiCheck className="w-3 h-3 shrink-0" /> : <FiX className="w-3 h-3 shrink-0" />}
                    {req.label}
                  </li>
                );
              })}
            </ul>
          </div>

          <div>
            <label htmlFor="confirm-password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Confirm Password
            </label>
            <div className="relative">
              <input
                id="confirm-password"
                type={showConfirm ? "text" : "password"}
                required
                minLength={8}
                maxLength={128}
                placeholder="Re-enter new password"
                className={`input-focus w-full px-3 py-2.5 pr-10 border rounded-lg focus:outline-none bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 transition-colors ${
                  confirmPassword && !passwordsMatch
                    ? "border-red-500 dark:border-red-500 focus:ring-red-500"
                    : confirmPassword && passwordsMatch
                    ? "border-emerald-500 dark:border-emerald-500"
                    : "border-gray-300 dark:border-gray-600"
                }`}
                value={confirmPassword}
                onChange={(e) => { setConfirmPassword(e.target.value); setFieldError(""); }}
                autoComplete="new-password"
              />
              <button
                type="button"
                onClick={() => setShowConfirm(!showConfirm)}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                tabIndex={-1}
                aria-label={showConfirm ? "Hide password" : "Show password"}
              >
                {showConfirm ? <FiEyeOff className="w-4 h-4" /> : <FiEye className="w-4 h-4" />}
              </button>
            </div>
            {confirmPassword && !passwordsMatch && (
              <p className="mt-1 text-xs text-red-500 flex items-center gap-1" role="alert">
                <FiX className="w-3 h-3 shrink-0" />
                Passwords do not match
              </p>
            )}
            {confirmPassword && passwordsMatch && newPassword === confirmPassword && (
              <p className="mt-1 text-xs text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                <FiCheck className="w-3 h-3" /> Passwords match
              </p>
            )}
          </div>

          {fieldError && (
            <p className="text-xs text-red-500 flex items-center gap-1" role="alert">
              <FiX className="w-3 h-3 shrink-0" />
              {fieldError}
            </p>
          )}

          <button
            type="submit"
            disabled={!canSubmit}
            className="btn-hover w-full bg-emerald-600 text-white py-2.5 rounded-lg hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-emerald-600 font-medium flex items-center justify-center gap-2 transition-all duration-200"
          >
            {loading ? (
              <>
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Resetting...
              </>
            ) : (
              <>
                <FiShield className="w-4 h-4" />
                Reset Password
              </>
            )}
          </button>
        </form>

        <div className="mt-6">
          <Link
            to="/login"
            className="link-underline text-emerald-600 dark:text-emerald-400 font-medium inline-flex items-center gap-1.5 text-sm"
          >
            <FiArrowLeft className="w-3.5 h-3.5" />
            Back to login
          </Link>
        </div>
      </div>
    </div>
  );
}
