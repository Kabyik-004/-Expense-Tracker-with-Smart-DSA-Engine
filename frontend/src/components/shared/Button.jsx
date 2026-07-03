import { forwardRef } from "react";
import { FiLoader } from "react-icons/fi";

const variantStyles = {
  primary: "bg-indigo-600 text-white hover:bg-indigo-700",
  "primary-green": "bg-green-600 text-white hover:bg-green-700",
  danger: "bg-red-600 text-white hover:bg-red-700",
  undo: "bg-orange-600 text-white hover:bg-orange-700",
  secondary: "border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700/50",
  ghost: "text-gray-400 dark:text-gray-500 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/30",
  outline: "bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors",
  auth: "w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50 font-medium",
};

const sizeStyles = {
  xs: "px-2 py-1 text-xs",
  sm: "px-3 py-1.5 text-xs",
  md: "px-4 py-2 text-sm",
  lg: "px-6 py-2 text-sm",
  xl: "px-6 py-3 text-base",
};

const Button = forwardRef(({
  variant = "primary",
  size = "md",
  loading = false,
  disabled = false,
  icon,
  iconPosition = "left",
  children,
  className = "",
  type = "button",
  fullWidth = false,
  ...props
}, ref) => {
  const isIconOnly = !children;
  const iconEl = loading ? <FiLoader className="w-4 h-4 animate-spin" /> : icon;

  return (
    <button
      ref={ref}
      type={type}
      disabled={disabled || loading}
      className={`${fullWidth ? "w-full" : ""} ${variantStyles[variant] || variantStyles.primary} ${isIconOnly ? "" : sizeStyles[size] || sizeStyles.md} rounded-lg font-medium transition-colors inline-flex items-center justify-center gap-2 ${disabled || loading ? "opacity-50 cursor-not-allowed" : "cursor-pointer"} ${className}`}
      {...props}
    >
      {iconEl && iconPosition === "left" ? iconEl : null}
      {children}
      {iconEl && iconPosition === "right" ? iconEl : null}
    </button>
  );
});

Button.displayName = "Button";
export default Button;
