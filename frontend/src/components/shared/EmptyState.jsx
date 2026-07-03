import { FiPlus, FiX } from "react-icons/fi";

const colorSchemes = {
  indigo: {
    bg: "bg-indigo-50 dark:bg-indigo-900/30",
    icon: "text-indigo-500 dark:text-indigo-400",
    btn: "bg-indigo-600 hover:bg-indigo-700 text-white",
    btnOutline: "border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700/50",
  },
  green: {
    bg: "bg-green-50 dark:bg-green-900/30",
    icon: "text-green-500 dark:text-green-400",
    btn: "bg-green-600 hover:bg-green-700 text-white",
    btnOutline: "border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700/50",
  },
  red: {
    bg: "bg-red-50 dark:bg-red-900/30",
    icon: "text-red-500 dark:text-red-400",
    btn: "bg-red-600 hover:bg-red-700 text-white",
    btnOutline: "border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700/50",
  },
  amber: {
    bg: "bg-amber-50 dark:bg-amber-900/30",
    icon: "text-amber-500 dark:text-amber-400",
    btn: "bg-amber-600 hover:bg-amber-700 text-white",
    btnOutline: "border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700/50",
  },
  gray: {
    bg: "bg-gray-100 dark:bg-gray-800",
    icon: "text-gray-400 dark:text-gray-500",
    btn: "bg-gray-600 hover:bg-gray-700 text-white",
    btnOutline: "border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700/50",
  },
};

export default function EmptyState({
  icon,
  title,
  description,
  action,
  secondaryAction,
  color = "gray",
  size = "default",
}) {
  const scheme = colorSchemes[color] || colorSchemes.gray;
  const isLarge = size === "large";

  return (
    <div className={`flex flex-col items-center justify-center text-center ${isLarge ? "py-16 px-4" : "py-12 px-4"}`}>
      <div className={`${scheme.bg} ${isLarge ? "w-20 h-20" : "w-16 h-16"} rounded-full flex items-center justify-center mb-5 transition-transform duration-300 hover:scale-105`}>
        <div className={`${scheme.icon} ${isLarge ? "text-3xl" : "text-2xl"}`}>
          {icon}
        </div>
      </div>

      <h3 className={`font-semibold text-gray-900 dark:text-white ${isLarge ? "text-xl" : "text-lg"} mb-1.5`}>
        {title}
      </h3>

      {description && (
        <p className={`text-gray-500 dark:text-gray-400 max-w-sm ${isLarge ? "text-base" : "text-sm"}`}>
          {description}
        </p>
      )}

      {action && (
        <button
          onClick={action.onClick}
          className={`mt-6 px-5 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 inline-flex items-center gap-2 hover:shadow-md active:scale-[0.97] ${scheme.btn}`}
        >
          {action.icon || <FiPlus className="w-4 h-4" />}
          {action.label}
        </button>
      )}

      {secondaryAction && (
        <button
          onClick={secondaryAction.onClick}
          className={`mt-3 px-5 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 inline-flex items-center gap-2 hover:shadow-sm active:scale-[0.97] ${scheme.btnOutline}`}
        >
          {secondaryAction.icon || <FiX className="w-4 h-4" />}
          {secondaryAction.label}
        </button>
      )}
    </div>
  );
}
