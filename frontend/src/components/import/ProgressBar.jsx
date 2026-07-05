import { useMemo } from "react";
import { FiCheck, FiX, FiAlertCircle } from "react-icons/fi";

export default function ProgressBar({
  percent = 0,
  status = "idle",
  label,
  description,
  onRetry,
  onCancel,
  animated = true,
  size = "md",
  showLabel = true,
}) {
  const clamped = Math.min(100, Math.max(0, percent));

  const { barColor, bgColor, icon: Icon, iconColor } = useMemo(() => {
    switch (status) {
      case "success":
        return {
          barColor: "bg-gradient-to-r from-emerald-500 to-green-400",
          bgColor: "bg-emerald-100 dark:bg-emerald-900/30",
          icon: FiCheck,
          iconColor: "text-emerald-600 dark:text-emerald-400",
        };
      case "error":
        return {
          barColor: "bg-gradient-to-r from-red-500 to-rose-400",
          bgColor: "bg-red-100 dark:bg-red-900/30",
          icon: FiAlertCircle,
          iconColor: "text-red-500 dark:text-red-400",
        };
      case "processing":
        return {
          barColor: "bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-500",
          bgColor: "bg-indigo-100 dark:bg-indigo-900/30",
          icon: null,
          iconColor: "text-indigo-500",
        };
      default:
        return {
          barColor: "bg-gradient-to-r from-indigo-500 to-purple-500",
          bgColor: "bg-indigo-100 dark:bg-indigo-900/30",
          icon: null,
          iconColor: "text-indigo-500",
        };
    }
  }, [status]);

  const heights = { sm: "h-1.5", md: "h-2.5", lg: "h-3.5" };

  return (
    <div
      className="w-full space-y-2"
      role="progressbar"
      aria-valuenow={clamped}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={label || `Progress: ${Math.round(clamped)}%`}
    >
      {showLabel && (label || status !== "idle") && (
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2 min-w-0">
            {Icon && <Icon className={`w-4 h-4 shrink-0 ${iconColor}`} />}
            {status === "processing" && (
              <div className={`w-4 h-4 rounded-full border-2 border-indigo-300 border-t-indigo-600 animate-spin shrink-0`} />
            )}
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300 truncate">
              {label || (status === "processing" ? "Processing..." : status === "success" ? "Complete" : status === "error" ? "Failed" : "")}
            </span>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            {onRetry && status === "error" && (
              <button
                onClick={onRetry}
                className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 bg-indigo-50 dark:bg-indigo-900/30 px-2.5 py-1 rounded-lg transition-colors"
                aria-label="Retry upload"
              >
                Retry
              </button>
            )}
            {onCancel && status === "processing" && (
              <button
                onClick={onCancel}
                className="text-xs font-semibold text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 bg-gray-100 dark:bg-gray-800 px-2.5 py-1 rounded-lg transition-colors"
                aria-label="Cancel upload"
              >
                <FiX className="w-3.5 h-3.5" />
              </button>
            )}
            <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 tabular-nums min-w-[3ch] text-right">
              {Math.round(clamped)}%
            </span>
          </div>
        </div>
      )}

      <div className={`relative w-full ${heights[size]} ${bgColor} rounded-full overflow-hidden`}>
        <div
          className={`absolute inset-y-0 left-0 ${barColor} rounded-full transition-all duration-500 ease-out ${animated && status === "processing" ? "animate-progress-pulse" : ""}`}
          style={{ width: `${clamped}%` }}
        />
        {status === "processing" && clamped > 0 && clamped < 100 && (
          <div className="absolute inset-y-0 left-0 w-full">
            <div className="h-full bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer rounded-full" style={{ width: `${clamped}%` }} />
          </div>
        )}
      </div>

      {description && (
        <p className="text-xs text-gray-400 dark:text-gray-500">{description}</p>
      )}
    </div>
  );
}
