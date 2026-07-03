import { useEffect, useCallback } from "react";
import { FiX } from "react-icons/fi";

export default function Modal({
  open,
  onClose,
  title,
  icon,
  iconBg,
  children,
  footer,
  size = "sm",
  closeOnOverlay = true,
}) {
  const handleKeyDown = useCallback((e) => {
    if (e.key === "Escape") onClose?.();
  }, [onClose]);

  useEffect(() => {
    if (open) {
      document.addEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "";
    };
  }, [open, handleKeyDown]);

  if (!open) return null;

  const sizes = { sm: "max-w-sm", md: "max-w-md", lg: "max-w-lg" };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 dark:bg-black/70 backdrop-blur-sm"
      onClick={closeOnOverlay ? onClose : undefined}
    >
      <div
        className={`bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full ${sizes[size] || sizes.sm} p-6 animate-fade-in`}
        onClick={(e) => e.stopPropagation()}
      >
        {title && (
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">{title}</h2>
            {onClose && (
              <button
                onClick={onClose}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              >
                <FiX className="w-5 h-5 text-gray-500 dark:text-gray-400" />
              </button>
            )}
          </div>
        )}
        {icon && (
          <div className="text-center">
            <div className={`w-14 h-14 ${iconBg || "bg-red-100 dark:bg-red-900/50"} rounded-full flex items-center justify-center mx-auto mb-4`}>
              {icon}
            </div>
          </div>
        )}
        {children}
        {footer && <div className="flex gap-3 mt-6">{footer}</div>}
      </div>
    </div>
  );
}
