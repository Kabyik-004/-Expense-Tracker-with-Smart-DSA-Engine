import { useTheme } from "../../context/ThemeContext";
import { FiSun, FiMoon, FiMonitor } from "react-icons/fi";

const modes = [
  { key: "light", icon: FiSun, label: "Light mode" },
  { key: "dark", icon: FiMoon, label: "Dark mode" },
  { key: "system", icon: FiMonitor, label: "System preference" },
];

export default function ThemeSwitch({ className = "", compact = false }) {
  const { theme, setTheme } = useTheme();

  return (
    <div
      className={`inline-flex items-center gap-0.5 p-0.5 rounded-xl bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 transition-colors duration-300 ${className}`}
      role="radiogroup"
      aria-label="Theme switcher"
    >
      {modes.map(({ key, icon: Icon, label }) => {
        const isActive = theme === key;
        return (
          <button
            key={key}
            onClick={() => setTheme(key)}
            role="radio"
            aria-checked={isActive}
            aria-label={label}
            title={label}
            className={`relative p-1.5 rounded-lg transition-all duration-300 ${
              compact ? "text-sm" : "text-base"
            } ${
              isActive
                ? "bg-white dark:bg-gray-700 text-emerald-600 dark:text-emerald-400 shadow-sm scale-105"
                : "text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-200/50 dark:hover:bg-gray-700/50"
            }`}
          >
            <Icon
              className={`w-4 h-4 transition-transform duration-300 ${
                isActive ? "scale-110" : "scale-100"
              }`}
            />
          </button>
        );
      })}
    </div>
  );
}
