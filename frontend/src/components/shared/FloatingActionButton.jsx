import { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { FiPlus, FiDollarSign, FiTrendingUp } from "react-icons/fi";

const actions = [
  { label: "Add Expense", icon: FiDollarSign, path: "/expenses", color: "text-red-600 dark:text-red-400" },
  { label: "Add Income", icon: FiTrendingUp, path: "/incomes", color: "text-green-600 dark:text-green-400" },
];

export default function FloatingActionButton() {
  const [open, setOpen] = useState(false);
  const [visible, setVisible] = useState(true);
  const lastScrollY = useRef(0);
  const fabRef = useRef(null);

  useEffect(() => {
    const main = document.querySelector("main");
    if (!main) return;

    const handleScroll = () => {
      const currentY = main.scrollTop;
      if (currentY > lastScrollY.current && currentY > 60) {
        setVisible(false);
        setOpen(false);
      } else if (currentY < lastScrollY.current - 10) {
        setVisible(true);
      }
      lastScrollY.current = currentY;
    };

    main.addEventListener("scroll", handleScroll, { passive: true });
    return () => main.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    if (!open) return;
    const handleClick = (e) => {
      if (fabRef.current && !fabRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClick, { capture: true });
    document.addEventListener("touchstart", handleClick, { capture: true });
    return () => {
      document.removeEventListener("mousedown", handleClick, { capture: true });
      document.removeEventListener("touchstart", handleClick, { capture: true });
    };
  }, [open]);

  const navigate = useNavigate();

  const handleAction = useCallback((path) => {
    setOpen(false);
    navigate(path);
  }, [navigate]);

  const toggle = useCallback(() => setOpen((prev) => !prev), []);

  return (
    <div ref={fabRef} data-fab className="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-3" role="navigation" aria-label="Quick actions">
      <div
        className={`flex flex-col items-end gap-3 transition-all duration-300 ease-out ${
          open
            ? "opacity-100 translate-y-0 scale-100"
            : "opacity-0 translate-y-4 scale-95 pointer-events-none"
        }`}
      >
        {actions.map((action, i) => {
          const Icon = action.icon;
          return (
            <button
              key={action.path}
              onClick={() => handleAction(action.path)}
              className={`flex items-center gap-2.5 px-4 py-2.5 rounded-xl bg-white/75 dark:bg-gray-800/75 backdrop-blur-xl border border-white/40 dark:border-gray-700/40 shadow-lg shadow-black/5 dark:shadow-black/20 hover:shadow-xl hover:bg-white/90 dark:hover:bg-gray-800/90 text-sm font-medium transition-all duration-200 hover:-translate-x-1 active:scale-95 ${action.color}`}
              style={{ transitionDelay: open ? `${i * 60}ms` : "0ms" }}
            >
              <Icon className="w-4 h-4" />
              {action.label}
            </button>
          );
        })}
      </div>

      <button
        onClick={toggle}
        aria-label={open ? "Close quick actions" : "Open quick actions"}
        aria-expanded={open}
        className={`w-14 h-14 rounded-full flex items-center justify-center bg-white/75 dark:bg-gray-800/75 backdrop-blur-xl border border-white/40 dark:border-gray-700/40 shadow-lg shadow-black/5 dark:shadow-black/20 hover:shadow-xl hover:bg-white/90 dark:hover:bg-gray-800/90 transition-all duration-300 ease-out active:scale-95 ${
          visible
            ? "translate-y-0 opacity-100 scale-100"
            : "translate-y-20 opacity-0 scale-50 pointer-events-none"
        }`}
      >
        <FiPlus
          className={`w-6 h-6 text-emerald-600 dark:text-emerald-400 transition-transform duration-300 ease-out ${
            open ? "rotate-45 scale-110" : "rotate-0 scale-100"
          }`}
        />
      </button>
    </div>
  );
}
