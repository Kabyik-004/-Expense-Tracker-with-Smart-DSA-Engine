import { useState, useCallback, createContext, useContext } from "react";
import { FiCheckCircle, FiAlertCircle, FiInfo, FiX, FiRefreshCw } from "react-icons/fi";

const ToastContext = createContext(null);

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx;
}

const ICONS = {
  success: FiCheckCircle,
  error: FiAlertCircle,
  info: FiInfo,
  undo: FiRefreshCw,
};

const COLORS = {
  success: "bg-green-50 dark:bg-green-900/30 border-green-200 text-green-800",
  error: "bg-red-50 dark:bg-red-900/30 border-red-200 text-red-800",
  info: "bg-blue-50 dark:bg-blue-900/30 border-blue-200 text-blue-800",
  undo: "bg-orange-50 dark:bg-orange-900/30 border-orange-200 text-orange-800",
};

const ICON_COLORS = {
  success: "text-green-500 dark:text-green-400",
  error: "text-red-500 dark:text-red-400",
  info: "text-blue-500 dark:text-blue-400",
  undo: "text-orange-500 dark:text-orange-400",
};

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = "info", duration = 4000) => {
    const id = Date.now() + Math.random();
    setToasts((prev) => [...prev, { id, message, type }]);
    if (duration > 0) {
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, duration);
    }
  }, []);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ addToast, removeToast }}>
      {children}
      <div className="fixed top-4 right-4 z-[100] flex flex-col gap-2 max-w-sm w-full pointer-events-none">
        {toasts.map((toast, _i) => {
          const Icon = ICONS[toast.type] || FiInfo;
          return (
            <div
              key={toast.id}
              className={`pointer-events-auto flex items-start gap-3 px-4 py-3 rounded-xl border shadow-lg animate-slide-in-right ${COLORS[toast.type] || COLORS.info}`}
              style={{ animation: `slideInRight 0.3s ease-out` }}
            >
              <Icon className={`w-5 h-5 mt-0.5 shrink-0 ${ICON_COLORS[toast.type] || ICON_COLORS.info}`} />
              <p className="text-sm font-medium flex-1">{toast.message}</p>
              <button onClick={() => removeToast(toast.id)} className="shrink-0 p-0.5 hover:opacity-60 transition-opacity">
                <FiX className="w-4 h-4" />
              </button>
            </div>
          );
        })}
      </div>
      <style>{`
        @keyframes slideInRight {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
      `}</style>
    </ToastContext.Provider>
  );
}