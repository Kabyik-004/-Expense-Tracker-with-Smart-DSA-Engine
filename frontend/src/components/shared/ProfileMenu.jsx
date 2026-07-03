import { useState, useRef, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { FiUser, FiSettings, FiLogOut } from "react-icons/fi";

export default function ProfileMenu({ user, onLogout }) {
  const [open, setOpen] = useState(false);
  const menuRef = useRef(null);
  const navigate = useNavigate();

  const initial = user?.full_name?.charAt(0) || user?.username?.charAt(0) || "U";
  const displayName = user?.full_name || user?.username || "User";

  useEffect(() => {
    if (!open) return;
    const handleClick = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
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

  const handleAction = useCallback((path) => {
    setOpen(false);
    navigate(path);
  }, [navigate]);

  const handleLogout = useCallback(() => {
    setOpen(false);
    onLogout();
  }, [onLogout]);

  const items = [
    { icon: FiSettings, label: "Settings", action: () => handleAction("/settings") },
    { icon: FiLogOut, label: "Logout", action: handleLogout, danger: true },
  ];

  return (
    <div ref={menuRef} className="relative">
      <button
        onClick={() => setOpen((prev) => !prev)}
        className="flex items-center gap-3 w-full px-4 py-2.5 rounded-xl transition-all duration-200 hover:bg-gray-50 dark:hover:bg-gray-800/50 group"
        aria-expanded={open}
        aria-haspopup="true"
      >
        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-sm font-bold shrink-0 shadow-md shadow-indigo-500/20 group-hover:shadow-lg group-hover:shadow-indigo-500/30 transition-all duration-200">
          {initial}
        </div>
        <div className="flex-1 text-left min-w-0">
          <p className="text-sm font-semibold text-gray-900 dark:text-gray-100 truncate">
            {displayName}
          </p>
          <p className="text-[11px] text-gray-400 dark:text-gray-500 truncate">
            {user?.email || ""}
          </p>
        </div>
      </button>

      <div
        className={`absolute bottom-full left-0 right-0 mb-2 origin-bottom transition-all duration-200 ${
          open
            ? "opacity-100 translate-y-0 scale-100 pointer-events-auto"
            : "opacity-0 translate-y-2 scale-95 pointer-events-none"
        }`}
      >
        <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl border border-white/30 dark:border-gray-700/40 rounded-xl shadow-xl shadow-black/5 dark:shadow-black/20 overflow-hidden">
          <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-700/50">
            <p className="text-xs font-semibold text-gray-900 dark:text-gray-100 truncate">
              {displayName}
            </p>
            <p className="text-[11px] text-gray-400 dark:text-gray-500 truncate mt-0.5">
              {user?.email || ""}
            </p>
          </div>
          <div className="p-1">
            {items.map((item, i) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.label}
                  onClick={item.action}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    item.danger
                      ? "text-gray-600 dark:text-gray-400 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30"
                      : "text-gray-600 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/30"
                  }`}
                  style={{ animationDelay: `${i * 40}ms` }}
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
