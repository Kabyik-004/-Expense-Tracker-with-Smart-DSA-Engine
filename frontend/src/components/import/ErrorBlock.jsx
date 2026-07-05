import { useState, useEffect } from "react";
import { FiAlertCircle, FiX, FiRefreshCw, FiChevronDown, FiChevronUp } from "react-icons/fi";

export default function ErrorBlock({
  title = "Something went wrong",
  message,
  errors,
  onRetry,
  onDismiss,
  retryLabel = "Try Again",
  variant = "default",
  compact = false,
}) {
  const [expanded, setExpanded] = useState(false);
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    setVisible(true);
  }, [message, errors]);

  const handleDismiss = () => {
    setVisible(false);
    onDismiss?.();
  };

  if (!visible) return null;

  const variants = {
    default: {
      border: "border-red-200/50 dark:border-red-800/40",
      bg: "bg-red-50/80 dark:bg-red-950/30",
      icon: "text-red-500 dark:text-red-400",
      title: "text-red-800 dark:text-red-200",
      message: "text-red-600 dark:text-red-400",
      dot: "bg-red-400 dark:bg-red-500",
    },
    warning: {
      border: "border-amber-200/50 dark:border-amber-800/40",
      bg: "bg-amber-50/80 dark:bg-amber-950/30",
      icon: "text-amber-500 dark:text-amber-400",
      title: "text-amber-800 dark:text-amber-200",
      message: "text-amber-600 dark:text-amber-400",
      dot: "bg-amber-400 dark:bg-amber-500",
    },
    subtle: {
      border: "border-red-200/30 dark:border-red-800/25",
      bg: "bg-red-50/50 dark:bg-red-950/20",
      icon: "text-red-400 dark:text-red-400",
      title: "text-red-700 dark:text-red-300",
      message: "text-red-500 dark:text-red-400",
      dot: "bg-red-300 dark:bg-red-500",
    },
  };

  const s = variants[variant] || variants.default;
  const hasDetails = errors && errors.length > 0;

  return (
    <div
      className={`rounded-2xl border ${s.border} ${s.bg} backdrop-blur-sm ${compact ? "p-4" : "p-5"} transition-all duration-300 animate-fade-in`}
      role="alert"
      aria-live="assertive"
    >
      <div className="flex items-start gap-3">
        <div className={`${s.icon} shrink-0 mt-0.5`}>
          <FiAlertCircle className={compact ? "w-5 h-5" : "w-6 h-6"} />
        </div>
        <div className="flex-1 min-w-0 space-y-1.5">
          <div className="flex items-start justify-between gap-2">
            <div>
              <p className={`font-semibold text-sm ${s.title}`}>{title}</p>
              {message && (
                <p className={`text-sm mt-0.5 ${s.message}`}>{message}</p>
              )}
            </div>
            {onDismiss && (
              <button
                onClick={handleDismiss}
                className="p-0.5 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 transition-colors shrink-0"
                aria-label="Dismiss error"
              >
                <FiX className="w-4 h-4" />
              </button>
            )}
          </div>

          {hasDetails && (
            <div className="pt-1.5">
              <button
                onClick={() => setExpanded(!expanded)}
                className="flex items-center gap-1.5 text-xs font-medium text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 transition-colors"
                aria-expanded={expanded}
                aria-controls="error-details"
              >
                {expanded ? <FiChevronUp className="w-3.5 h-3.5" /> : <FiChevronDown className="w-3.5 h-3.5" />}
                {expanded ? "Hide details" : `Show details (${errors.length})`}
              </button>
              {expanded && (
                <ul id="error-details" className="mt-2 space-y-1">
                  {errors.slice(0, 20).map((e, i) => (
                    <li key={i} className="flex items-start gap-2 text-xs text-red-600 dark:text-red-400">
                      <span className={`w-1.5 h-1.5 rounded-full ${s.dot} mt-1.5 shrink-0`} />
                      <span>Row {e.row != null ? e.row + 1 : "?"}: {e.error || e}</span>
                    </li>
                  ))}
                  {errors.length > 20 && (
                    <li className="text-xs text-gray-400 dark:text-gray-500">...and {errors.length - 20} more</li>
                  )}
                </ul>
              )}
            </div>
          )}

          {onRetry && (
            <div className="pt-2">
              <button
                onClick={onRetry}
                className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold text-red-700 dark:text-red-300 bg-red-100 dark:bg-red-900/40 hover:bg-red-200 dark:hover:bg-red-900/60 rounded-xl transition-colors"
                aria-label={retryLabel}
              >
                <FiRefreshCw className="w-3.5 h-3.5" />
                {retryLabel}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
