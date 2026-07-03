import { useState, useEffect, useRef } from "react";

function easeOutCubic(t) {
  return 1 - Math.pow(1 - t, 3);
}

export default function AnimatedCircularProgress({
  value,
  size = 120,
  strokeWidth = 8,
  color = "#6366f1",
  bgCircle = null,
  label,
  subtitle,
  children,
}) {
  const [progress, setProgress] = useState(0);
  const frameRef = useRef(null);
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;

  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    const check = () => setIsDark(document.documentElement.classList.contains("dark"));
    check();
    const observer = new MutationObserver(check);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["class"] });
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (frameRef.current) cancelAnimationFrame(frameRef.current);

    const startTime = performance.now();
    const duration = 1200;

    const animate = (now) => {
      const elapsed = now - startTime;
      const p = Math.min(elapsed / duration, 1);
      setProgress(value * easeOutCubic(p));
      if (p < 1) {
        frameRef.current = requestAnimationFrame(animate);
      }
    };

    frameRef.current = requestAnimationFrame(animate);
    return () => {
      if (frameRef.current) cancelAnimationFrame(frameRef.current);
    };
  }, [value]);

  const offset = circumference - (progress / 100) * circumference;
  const bgStroke = bgCircle || (isDark ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.06)");

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="transform -rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={bgStroke}
            strokeWidth={strokeWidth}
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ transition: "stroke-dashoffset 0.1s linear" }}
          />
        </svg>
        {children && (
          <div className="absolute inset-0 flex items-center justify-center">
            {children}
          </div>
        )}
      </div>
      {label && (
        <p className="text-sm font-semibold text-gray-900 dark:text-white text-center leading-tight">
          {label}
        </p>
      )}
      {subtitle && (
        <p className="text-xs text-gray-500 dark:text-gray-400 text-center leading-tight">
          {subtitle}
        </p>
      )}
    </div>
  );
}
