import { useState, useCallback, createContext, useContext, useRef, useEffect } from "react";
import { FiCheckCircle, FiAlertCircle, FiAlertTriangle, FiInfo, FiX, FiRefreshCw } from "react-icons/fi";

const ToastContext = createContext(null);

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx;
}

const ICONS = {
  success: FiCheckCircle,
  error: FiAlertCircle,
  warning: FiAlertTriangle,
  info: FiInfo,
  undo: FiRefreshCw,
};

const STYLES = {
  success: {
    border: "border-green-200 dark:border-green-800",
    bg: "bg-white dark:bg-gray-800",
    icon: "text-green-500 dark:text-green-400",
    text: "text-gray-900 dark:text-white",
    desc: "text-gray-500 dark:text-gray-400",
    undo: "text-green-600 dark:text-green-400 hover:text-green-700 dark:hover:text-green-300 hover:bg-green-50 dark:hover:bg-green-900/30",
  },
  error: {
    border: "border-red-200 dark:border-red-800",
    bg: "bg-white dark:bg-gray-800",
    icon: "text-red-500 dark:text-red-400",
    text: "text-gray-900 dark:text-white",
    desc: "text-gray-500 dark:text-gray-400",
    undo: "text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-900/30",
  },
  warning: {
    border: "border-amber-200 dark:border-amber-800",
    bg: "bg-white dark:bg-gray-800",
    icon: "text-amber-500 dark:text-amber-400",
    text: "text-gray-900 dark:text-white",
    desc: "text-gray-500 dark:text-gray-400",
    undo: "text-amber-600 dark:text-amber-400 hover:text-amber-700 dark:hover:text-amber-300 hover:bg-amber-50 dark:hover:bg-amber-900/30",
  },
  info: {
    border: "border-blue-200 dark:border-blue-800",
    bg: "bg-white dark:bg-gray-800",
    icon: "text-blue-500 dark:text-blue-400",
    text: "text-gray-900 dark:text-white",
    desc: "text-gray-500 dark:text-gray-400",
    undo: "text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 hover:bg-blue-50 dark:hover:bg-blue-900/30",
  },
  undo: {
    border: "border-orange-200 dark:border-orange-800",
    bg: "bg-white dark:bg-gray-800",
    icon: "text-orange-500 dark:text-orange-400",
    text: "text-gray-900 dark:text-white",
    desc: "text-gray-500 dark:text-gray-400",
    undo: "text-orange-600 dark:text-orange-400 hover:text-orange-700 dark:hover:text-orange-300 hover:bg-orange-50 dark:hover:bg-orange-900/30",
  },
};

export function ToastProvider({ children, position = "top-right" }) {
  const [toasts, setToasts] = useState([]);
  const timers = useRef({});

  const removeToast = useCallback((id) => {
    setToasts((prev) =>
      prev.map((t) => (t.id === id ? { ...t, exiting: true } : t))
    );
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 300);
  }, []);

  const addToast = useCallback((message, type = "info", options = {}) => {
    const isObj = typeof options === "object" && !Array.isArray(options);
    const duration = isObj ? (options.duration ?? 4000) : (typeof options === "number" ? options : 4000);
    const onUndo = isObj ? options.onUndo : undefined;
    const undoLabel = isObj ? (options.undoLabel || "Undo") : "Undo";
    const toastPosition = isObj ? (options.position || position) : position;
    const description = isObj ? options.description : undefined;

    const id = Date.now() + Math.random();

    setToasts((prev) => [...prev, {
      id, message, type, description, onUndo, undoLabel, position: toastPosition, exiting: false,
    }]);

    if (duration > 0) {
      timers.current[id] = setTimeout(() => {
        removeToast(id);
      }, duration);
    }

    return id;
  }, [removeToast, position]);

  const handleUndo = useCallback((toast) => {
    if (timers.current[toast.id]) {
      clearTimeout(timers.current[toast.id]);
      delete timers.current[toast.id];
    }
    removeToast(toast.id);
    toast.onUndo?.();
  }, [removeToast]);

  useEffect(() => {
    return () => {
      Object.values(timers.current).forEach(clearTimeout);
    };
  }, []);

  const topRight = toasts.filter((t) => t.position === "top-right" || !t.position);
  const bottomRight = toasts.filter((t) => t.position === "bottom-right");

  const ToastList = ({ items, pos }) => {
    if (items.length === 0) return null;
    return (
      <div className={`fixed z-[100] flex flex-col gap-2 w-full max-w-sm pointer-events-none ${
        pos === "bottom-right" ? "bottom-4 right-4" : "top-4 right-4"
      }`}>
        {items.map((toast) => {
          const Icon = ICONS[toast.type] || FiInfo;
          const s = STYLES[toast.type] || STYLES.info;
          return (
            <div
              key={toast.id}
              className={`pointer-events-auto flex items-start gap-3 px-4 py-3 rounded-xl border shadow-lg ${s.bg} ${s.border} ${
                toast.exiting ? "animate-slide-out-right" : "animate-slide-in-right"
              }`}
            >
              <Icon className={`w-5 h-5 mt-0.5 shrink-0 ${s.icon}`} />
              <div className="flex-1 min-w-0">
                <p className={`text-sm font-medium ${s.text}`}>{toast.message}</p>
                {toast.description && (
                  <p className={`text-xs mt-0.5 ${s.desc}`}>{toast.description}</p>
                )}
              </div>
              <div className="flex items-center gap-1 shrink-0">
                {toast.onUndo && (
                  <button
                    onClick={() => handleUndo(toast)}
                    className={`text-xs font-semibold px-2 py-1 rounded-lg transition-colors ${s.undo}`}
                  >
                    {toast.undoLabel}
                  </button>
                )}
                <button
                  onClick={() => removeToast(toast.id)}
                  className="p-0.5 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                >
                  <FiX className="w-4 h-4" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <ToastContext.Provider value={{ addToast, removeToast }}>
      {children}
      <ToastList items={topRight} pos="top-right" />
      <ToastList items={bottomRight} pos="bottom-right" />
      <style>{`
        @keyframes slide-in-right {
          from { transform: translateX(120%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slide-out-right {
          from { transform: translateX(0); opacity: 1; }
          to { transform: translateX(120%); opacity: 0; }
        }
        .animate-slide-in-right {
          animation: slide-in-right 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
        .animate-slide-out-right {
          animation: slide-out-right 0.3s ease-in forwards;
        }
      `}</style>
    </ToastContext.Provider>
  );
}
