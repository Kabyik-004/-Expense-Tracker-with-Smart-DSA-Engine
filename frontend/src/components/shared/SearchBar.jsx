import { useState, useRef, useEffect, useCallback } from "react";
import { FiSearch, FiX, FiClock, FiTrash2, FiTrendingUp } from "react-icons/fi";

const MAX_RECENT = 6;

function loadRecent(key) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : [];
  } catch { return []; }
}

function saveRecent(key, items) {
  try { localStorage.setItem(key, JSON.stringify(items)); } catch {}
}

export default function SearchBar({
  value,
  onChange,
  onClear,
  placeholder = "Search...",
  accentColor = "emerald",
  loading = false,
  recentSearchesKey,
  suggestions = [],
  recentLabel = "Recent searches",
  suggestionsLabel = "Suggestions",
  emptyMessage = "No recent searches",
  className = "",
}) {
  const [focused, setFocused] = useState(false);
  const [recentSearches, setRecentSearches] = useState(() =>
    recentSearchesKey ? loadRecent(recentSearchesKey) : []
  );

  const inputRef = useRef(null);
  const containerRef = useRef(null);

  const addRecent = useCallback((term) => {
    if (!recentSearchesKey || !term.trim()) return;
    setRecentSearches((prev) => {
      const filtered = prev.filter((s) => s.toLowerCase() !== term.toLowerCase());
      const next = [term, ...filtered].slice(0, MAX_RECENT);
      saveRecent(recentSearchesKey, next);
      return next;
    });
  }, [recentSearchesKey]);

  const removeRecent = useCallback((e, term) => {
    e.stopPropagation();
    if (!recentSearchesKey) return;
    setRecentSearches((prev) => {
      const next = prev.filter((s) => s.toLowerCase() !== term.toLowerCase());
      saveRecent(recentSearchesKey, next);
      return next;
    });
  }, [recentSearchesKey]);

  const clearAllRecent = useCallback((e) => {
    e.stopPropagation();
    if (!recentSearchesKey) return;
    setRecentSearches([]);
    saveRecent(recentSearchesKey, []);
  }, [recentSearchesKey]);

  useEffect(() => {
    if (!focused) return;
    const handleClick = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setFocused(false);
      }
    };
    document.addEventListener("mousedown", handleClick, { capture: true });
    return () => document.removeEventListener("mousedown", handleClick, { capture: true });
  }, [focused]);

  const selectSuggestion = useCallback((term) => {
    onChange(term);
    addRecent(term);
    setFocused(false);
    inputRef.current?.blur();
  }, [onChange, addRecent]);

  const handleSubmit = useCallback(() => {
    if (value.trim()) addRecent(value);
  }, [value, addRecent]);

  const handleClear = useCallback(() => {
    onClear?.();
    inputRef.current?.focus();
  }, [onClear]);

  const handleChange = useCallback((e) => {
    onChange(e.target.value);
  }, [onChange]);

  const showDropdown = focused && (
    recentSearches.length > 0 || suggestions.length > 0
  );

  const hasContent = value.length > 0;

  const accentRing = {
    emerald: "focus:ring-emerald-500 dark:focus:ring-emerald-400",
    green: "focus:ring-green-500 dark:focus:ring-green-400",
    blue: "focus:ring-blue-500 dark:focus:ring-blue-400",
    red: "focus:ring-red-500 dark:focus:ring-red-400",
  };

  const accentFocus = {
    emerald: "text-emerald-600 dark:text-emerald-400",
    green: "text-green-600 dark:text-green-400",
    blue: "text-blue-600 dark:text-blue-400",
    red: "text-red-600 dark:text-red-400",
  };

  const accentBg = {
    emerald: "bg-emerald-50 dark:bg-emerald-900/20",
    green: "bg-green-50 dark:bg-green-900/20",
    blue: "bg-blue-50 dark:bg-blue-900/20",
    red: "bg-red-50 dark:bg-red-900/20",
  };

  const accentHover = {
    emerald: "hover:bg-emerald-50 dark:hover:bg-emerald-900/15",
    green: "hover:bg-green-50 dark:hover:bg-green-900/15",
    blue: "hover:bg-blue-50 dark:hover:bg-blue-900/15",
    red: "hover:bg-red-50 dark:hover:bg-red-900/15",
  };

  const accentTextHover = {
    emerald: "hover:text-emerald-700 dark:hover:text-emerald-300",
    green: "hover:text-green-700 dark:hover:text-green-300",
    blue: "hover:text-blue-700 dark:hover:text-blue-300",
    red: "hover:text-red-700 dark:hover:text-red-300",
  };

  const ringClass = accentRing[accentColor] || accentRing.emerald;
  const focusColorClass = accentFocus[accentColor] || accentFocus.emerald;
  const bgColorClass = accentBg[accentColor] || accentBg.emerald;
  const hoverColorClass = accentHover[accentColor] || accentHover.emerald;
  const textHoverClass = accentTextHover[accentColor] || accentTextHover.emerald;

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      <div className={`relative flex items-center transition-all duration-200 rounded-lg border bg-white dark:bg-gray-800 ${
        focused
          ? `border-${accentColor}-300 dark:border-${accentColor}-600 ring-2 ${ringClass}`
          : "border-gray-300 dark:border-gray-600"
      }`}>
        <FiSearch className={`absolute left-3 w-4 h-4 transition-all duration-300 ${
          focused ? `${focusColorClass} scale-110` : "text-gray-400 dark:text-gray-500"
        } ${hasContent ? focusColorClass : ""}`} />

        <input
          ref={inputRef}
          type="text"
          className="w-full pl-10 pr-10 py-2.5 bg-transparent border-none outline-none text-sm text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
          placeholder={placeholder}
          value={value}
          onChange={handleChange}
          onFocus={() => setFocused(true)}
          onBlur={() => setTimeout(() => setFocused(false), 200)}
          onKeyDown={(e) => {
            if (e.key === "Enter") { handleSubmit(); }
            if (e.key === "Escape") { setFocused(false); inputRef.current?.blur(); }
          }}
          aria-label={placeholder}
        />

        <div className="absolute right-3 flex items-center gap-1">
          {loading && (
            <svg className="w-4 h-4 text-gray-400 animate-spin" viewBox="0 0 16 16" fill="none">
              <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="2" strokeDasharray="28" strokeLinecap="round" opacity="0.3" />
              <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="2" strokeDasharray="28" strokeDashoffset="14" strokeLinecap="round" />
            </svg>
          )}
          {!loading && hasContent && (
            <button type="button" onClick={handleClear} className="p-0.5 rounded transition-colors text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300" aria-label="Clear search">
              <FiX className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      <div
        className={`absolute left-0 right-0 top-full mt-1.5 z-50 origin-top transition-all duration-200 ${
          showDropdown
            ? "opacity-100 translate-y-0 scale-100 pointer-events-auto"
            : "opacity-0 -translate-y-1 scale-95 pointer-events-none"
        }`}
      >
        <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-xl border border-gray-200/60 dark:border-gray-700/40 rounded-xl shadow-xl shadow-black/5 dark:shadow-black/20 overflow-hidden max-h-72 overflow-y-auto">
          {recentSearches.length > 0 && (
            <div>
              <div className="flex items-center justify-between px-4 py-2">
                <p className="text-[11px] font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">{recentLabel}</p>
                <button onClick={clearAllRecent} className="text-[11px] font-medium text-gray-400 dark:text-gray-500 hover:text-red-500 dark:hover:text-red-400 transition-colors flex items-center gap-1">
                  <FiTrash2 className="w-3 h-3" /> Clear
                </button>
              </div>
              <div className="px-1 pb-1">
                {recentSearches.map((term, i) => (
                  <button
                    key={term}
                    onClick={() => selectSuggestion(term)}
                    className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-gray-600 dark:text-gray-400 transition-all duration-150 ${hoverColorClass} ${textHoverClass} group/item`}
                    style={{ animationDelay: `${i * 30}ms` }}
                  >
                    <FiClock className="w-3.5 h-3.5 shrink-0 text-gray-300 dark:text-gray-600" />
                    <span className="flex-1 text-left truncate">{term}</span>
                    <button
                      onClick={(e) => removeRecent(e, term)}
                      className="p-0.5 rounded opacity-0 group-hover/item:opacity-100 transition-opacity text-gray-300 dark:text-gray-600 hover:text-red-500 dark:hover:text-red-400"
                      aria-label={`Remove ${term}`}
                    >
                      <FiX className="w-3 h-3" />
                    </button>
                  </button>
                ))}
              </div>
            </div>
          )}

          {suggestions.length > 0 && (
            <div className={recentSearches.length > 0 ? "border-t border-gray-100 dark:border-gray-700/50" : ""}>
              <div className="px-4 py-2">
                <p className="text-[11px] font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">{suggestionsLabel}</p>
              </div>
              <div className="px-1 pb-1">
                {suggestions.map((item, i) => (
                  <button
                    key={item.key ?? item.text}
                    onClick={() => selectSuggestion(item.text)}
                    className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-gray-700 dark:text-gray-300 transition-all duration-150 ${hoverColorClass} ${textHoverClass}`}
                    style={{ animationDelay: `${(recentSearches.length + i) * 30}ms` }}
                  >
                    {item.icon || <FiTrendingUp className="w-3.5 h-3.5 shrink-0 text-gray-400" />}
                    <span className="flex-1 text-left truncate">{item.text}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {recentSearches.length === 0 && suggestions.length === 0 && focused && value.length > 0 && (
            <div className="px-4 py-6 text-center">
              <FiSearch className="w-6 h-6 mx-auto mb-2 text-gray-300 dark:text-gray-600" />
              <p className="text-sm text-gray-400 dark:text-gray-500">{emptyMessage}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
