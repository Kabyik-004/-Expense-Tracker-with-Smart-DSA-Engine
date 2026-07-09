import { useState, useEffect, useRef, useCallback } from "react";
import { Link, useSearchParams, useNavigate } from "react-router-dom";
import {
  FiKey, FiArrowLeft, FiClock, FiCheck, FiMail, FiCheckCircle,
} from "react-icons/fi";
import { verifyOtp, forgotPassword } from "../services/authService";
import { useToast } from "../components/shared/Toast";
import ThemeSwitch from "../components/shared/ThemeSwitch";

const OTP_LENGTH = 6;
const COOLDOWN = 60;

export default function VerifyOTP() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { addToast } = useToast();

  const email = searchParams.get("email") || "";

  const [otp, setOtp] = useState(Array(OTP_LENGTH).fill(""));
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const [countdown, setCountdown] = useState(COOLDOWN);
  const [showCountdown, setShowCountdown] = useState(true);
  const [shake, setShake] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [verified, setVerified] = useState(false);
  const [fieldError, setFieldError] = useState("");
  const timerRef = useRef(null);
  const inputRefs = useRef([]);

  useEffect(() => {
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, []);

  useEffect(() => {
    startCountdown();
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

  const triggerShake = () => {
    setShake(true);
    setTimeout(() => setShake(false), 500);
  };

  const focusInput = (index) => {
    if (index >= 0 && index < OTP_LENGTH) inputRefs.current[index]?.focus();
  };

  const handleChange = (index, value) => {
    const digit = value.replace(/\D/g, "");
    if (!digit) return;
    const newOtp = [...otp];
    newOtp[index] = digit.slice(-1);
    setOtp(newOtp);
    setFieldError("");
    if (index < OTP_LENGTH - 1) focusInput(index + 1);
  };

  const handleKeyDown = (index, e) => {
    if (e.key === "Backspace" && !otp[index] && index > 0) {
      const newOtp = [...otp];
      newOtp[index - 1] = "";
      setOtp(newOtp);
      focusInput(index - 1);
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pasted = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, OTP_LENGTH);
    if (!pasted) return;
    const newOtp = Array(OTP_LENGTH).fill("");
    for (let i = 0; i < pasted.length; i++) newOtp[i] = pasted[i];
    setOtp(newOtp);
    setFieldError("");
    focusInput(Math.min(pasted.length, OTP_LENGTH - 1));
  };

  const handleResend = async () => {
    if (!email) return;
    setResending(true);
    try {
      const res = await forgotPassword({ email });
      if (res.success) {
        setOtp(Array(OTP_LENGTH).fill(""));
        setVerified(false);
        setVerifying(false);
        focusInput(0);
        startCountdown();
        addToast("OTP resent successfully", "success");
      } else {
        addToast(res.message || "Failed to resend OTP", "error");
      }
    } catch (err) {
      addToast(err.response?.data?.message || "Something went wrong. Please try again.", "error");
    } finally {
      setResending(false);
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    setFieldError("");

    const code = otp.join("");
    if (code.length !== OTP_LENGTH) {
      const msg = "Please enter the complete 6-digit OTP";
      setFieldError(msg);
      triggerShake();
      return;
    }
    if (!email) {
      addToast("Email is missing. Please go back and try again.", "error");
      return;
    }

    setLoading(true);
    setVerifying(true);
    try {
      const res = await verifyOtp({ email, otp: code });
      if (res.success) {
        setVerified(true);
        setTimeout(() => {
          navigate("/reset-password", { state: { email, otp: code } });
        }, 1800);
      } else {
        const msg = res.message || "Invalid or expired OTP";
        setFieldError(msg);
        triggerShake();
        setOtp(Array(OTP_LENGTH).fill(""));
        focusInput(0);
      }
    } catch (err) {
      const msg = err.response?.data?.message || "Something went wrong. Please try again.";
      setFieldError(msg);
      triggerShake();
    } finally {
      setLoading(false);
    }
  };

  const allFilled = otp.every((d) => d !== "");
  const verifyDisabled = loading || !allFilled || verified;
  const resendDisabled = resending || showCountdown || !email || verified;

  const inputClass = `w-10 sm:w-12 h-12 sm:h-14 text-center text-lg sm:text-xl font-bold border rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 disabled:opacity-50 transition-all duration-150 ${
    fieldError
      ? "border-red-400 dark:border-red-500"
      : "border-gray-300 dark:border-gray-600"
  }`;

  if (!email) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950 px-4">
        <div className="w-full max-w-md bg-white dark:bg-gray-900 rounded-2xl shadow-lg p-8 text-center animate-page-enter">
          <FiMail className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
          <h1 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Missing email</h1>
          <p className="text-gray-500 dark:text-gray-400 mb-6">
            No email address provided. Please start from the forgot password page.
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

  if (verified) {
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
            OTP verified
          </h1>
          <p className="text-gray-500 dark:text-gray-400">
            Redirecting to set your new password...
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
          <FiKey className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Verify OTP
          </h1>
        </div>

        <p className="text-gray-500 dark:text-gray-400 mb-1">
          Enter the 6-digit code sent to
        </p>
        <p className="text-sm font-medium text-gray-900 dark:text-white mb-6 break-all">
          {email}
        </p>

        <form onSubmit={handleVerify} noValidate>
          <div aria-live="polite" aria-atomic="true" className="sr-only">
            {fieldError || `${otp.filter(Boolean).length} of ${OTP_LENGTH} digits entered`}
          </div>

          <div className={`flex items-center justify-center gap-1.5 sm:gap-2 mb-2 ${shake ? "animate-shake" : ""}`}>
            {otp.map((digit, index) => (
              <input
                key={index}
                ref={(el) => { inputRefs.current[index] = el; }}
                type="text"
                inputMode="numeric"
                autoComplete="one-time-code"
                maxLength={1}
                value={digit}
                onChange={(e) => handleChange(index, e.target.value)}
                onKeyDown={(e) => handleKeyDown(index, e)}
                onPaste={index === 0 ? handlePaste : undefined}
                disabled={loading}
                className={inputClass}
                aria-label={`Digit ${index + 1}${digit ? `, entered ${digit}` : ", empty"}`}
                aria-invalid={!!fieldError}
              />
            ))}
          </div>

          {fieldError && (
            <p className="text-center text-xs text-red-500 mb-4 flex items-center justify-center gap-1" role="alert">
              <FiClock className="w-3 h-3 shrink-0" />
              {fieldError}
            </p>
          )}

          <button
            type="submit"
            disabled={verifyDisabled}
            className="btn-hover w-full bg-emerald-600 text-white py-2.5 rounded-lg hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-emerald-600 font-medium flex items-center justify-center gap-2 transition-all duration-200 mb-4"
          >
            {loading ? (
              <>
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Verifying...
              </>
            ) : (
              <>
                <FiCheck className="w-4 h-4" />
                Verify OTP
              </>
            )}
          </button>
        </form>

        <div className="text-center">
          <button
            type="button"
            onClick={handleResend}
            disabled={resendDisabled}
            className="inline-flex items-center gap-1.5 text-sm font-medium text-emerald-600 dark:text-emerald-400 disabled:text-gray-400 dark:disabled:text-gray-600 disabled:cursor-not-allowed transition-colors duration-200"
          >
            {resending ? (
              <>
                <svg className="animate-spin h-3.5 w-3.5" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Resending...
              </>
            ) : showCountdown ? (
              <>
                <FiClock className="w-3.5 h-3.5" />
                Resend in {Math.floor(countdown / 60)}:{String(countdown % 60).padStart(2, "0")}
              </>
            ) : (
              "Resend OTP"
            )}
          </button>
        </div>

        <div className="mt-6">
          <Link
            to="/forgot-password"
            className="link-underline text-emerald-600 dark:text-emerald-400 font-medium inline-flex items-center gap-1.5 text-sm"
          >
            <FiArrowLeft className="w-3.5 h-3.5" />
            Change email
          </Link>
        </div>
      </div>
    </div>
  );
}
