import { useState, useEffect, useRef, useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  FiMail, FiClock, FiArrowLeft, FiArrowRight, FiCheckCircle,
} from "react-icons/fi";
import { forgotPassword } from "../services/authService";
import { useToast } from "../components/shared/Toast";
import ThemeSwitch from "../components/shared/ThemeSwitch";

const COOLDOWN = 60;

export default function ForgotPassword() {
  const navigate = useNavigate();
  const { addToast } = useToast();
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [countdown, setCountdown] = useState(COOLDOWN);
  const [showCountdown, setShowCountdown] = useState(false);
  const [fieldError, setFieldError] = useState("");
  const timerRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, []);

  useEffect(() => {
    if (fieldError) {
      const t = setTimeout(() => setFieldError(""), 3000);
      return () => clearTimeout(t);
    }
  }, [fieldError]);

  const startCountdown = useCallback(() => {
    if (timerRef.current) clearInterval(timerRef.current);
    setCountdown(COOLDOWN);
    setShowCountdown(true);
    timerRef.current = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timerRef.current);
          timerRef.current = null;
          setShowCountdown(false);
          return COOLDOWN;
        }
        return prev - 1;
      });
    }, 1000);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFieldError("");

    const trimmed = email.trim();
    if (!trimmed) { setFieldError("Please enter your email address"); return; }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed)) { setFieldError("Please enter a valid email address"); return; }

    setLoading(true);
    try {
      const res = await forgotPassword({ email: trimmed.toLowerCase() });
      if (res.success) {
        setSent(true);
        startCountdown();
        addToast("OTP sent successfully", "success");
      } else {
        addToast(res.message || "Failed to send OTP", "error");
      }
    } catch (err) {
      addToast(err.response?.data?.message || "Something went wrong. Please try again.", "error");
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (sec) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m}:${s.toString().padStart(2, "0")}`;
  };

  const buttonDisabled = loading || (sent && showCountdown);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950 px-4 py-8">
      <div className="w-full max-w-md bg-white dark:bg-gray-900 rounded-2xl shadow-lg p-8 relative animate-page-enter">
        <div className="absolute top-4 right-4">
          <ThemeSwitch />
        </div>

        {sent ? (
          <div className="text-center" role="alert" aria-live="polite">
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
              OTP sent
            </h1>
            <p className="text-gray-500 dark:text-gray-400 mb-6">
              We've sent a one-time password to <span className="font-medium text-gray-700 dark:text-gray-300 break-all">{email}</span>. Please check your inbox.
            </p>
            <button
              type="button"
              onClick={() => navigate(`/verify-otp?email=${encodeURIComponent(email)}`)}
              className="btn-hover w-full bg-emerald-600 text-white py-2.5 rounded-lg hover:bg-emerald-700 font-medium flex items-center justify-center gap-2 transition-all duration-200"
            >
              Enter OTP
              <FiArrowRight className="w-4 h-4" />
            </button>
            <button
              type="button"
              onClick={handleSubmit}
              disabled={buttonDisabled}
              className="w-full mt-3 bg-white dark:bg-gray-800 text-emerald-600 dark:text-emerald-400 border border-emerald-600 dark:border-emerald-500 py-2.5 rounded-lg hover:bg-emerald-50 dark:hover:bg-emerald-900/20 font-medium flex items-center justify-center gap-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Sending...
                </>
              ) : showCountdown ? (
                <>
                  <FiClock className="w-4 h-4" />
                  Resend in {formatTime(countdown)}
                </>
              ) : (
                "Resend OTP"
              )}
            </button>
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
        ) : (
          <>
            <div className="flex items-center gap-3 mb-1">
              <FiMail className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Forgot password
              </h1>
            </div>
            <p className="text-gray-500 dark:text-gray-400 mb-6">
              Enter your registered email to receive a password reset OTP
            </p>
            <form onSubmit={handleSubmit} noValidate className="space-y-4">
              <div>
                <label
                  htmlFor="email"
                  className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                >
                  Email address
                </label>
                <div className="relative">
                  <FiMail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-gray-500 pointer-events-none" />
                  <input
                    ref={inputRef}
                    id="email"
                    type="email"
                    required
                    placeholder="you@example.com"
                    className={`w-full pl-10 pr-3 py-2.5 border rounded-lg focus:outline-none bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 disabled:opacity-50 disabled:cursor-not-allowed input-focus ${
                      fieldError
                        ? "border-red-500 dark:border-red-500"
                        : "border-gray-300 dark:border-gray-600"
                    }`}
                    value={email}
                    onChange={(e) => { setEmail(e.target.value); setFieldError(""); }}
                    disabled={loading}
                    autoComplete="email"
                    autoFocus
                    aria-invalid={!!fieldError}
                    aria-describedby={fieldError ? "email-error" : undefined}
                  />
                </div>
                {fieldError && (
                  <p id="email-error" className="mt-1 text-xs text-red-500 flex items-center gap-1" role="alert">
                    <FiClock className="w-3 h-3 shrink-0" />
                    {fieldError}
                  </p>
                )}
              </div>

              <button
                type="submit"
                disabled={buttonDisabled}
                className="btn-hover w-full bg-emerald-600 text-white py-2.5 rounded-lg hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-emerald-600 font-medium flex items-center justify-center gap-2 transition-all duration-200"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Sending...
                  </>
                ) : sent ? (
                  "Resend OTP"
                ) : (
                  "Send OTP"
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
          </>
        )}
      </div>
    </div>
  );
}
