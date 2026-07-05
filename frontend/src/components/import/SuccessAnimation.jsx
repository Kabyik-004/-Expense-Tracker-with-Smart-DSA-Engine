import { useEffect, useState } from "react";
import { FiCheck } from "react-icons/fi";

const COLORS = ["#6366f1", "#8b5cf6", "#a855f7", "#d946ef", "#10b981", "#f59e0b", "#ef4444", "#06b6d4"];

function Particle({ index }) {
  const angle = (index / 20) * 360;
  const dist = 60 + Math.random() * 60;
  const x = Math.cos((angle * Math.PI) / 180) * dist;
  const y = Math.sin((angle * Math.PI) / 180) * dist;
  const size = 3 + Math.random() * 4;
  const color = COLORS[index % COLORS.length];
  const delay = Math.random() * 0.15;

  return (
    <div
      className="absolute left-1/2 top-1/2 pointer-events-none"
      style={{ animation: `particle-burst 0.7s ${delay}s ease-out forwards`, opacity: 0 }}
    >
      <div
        className="rounded-full"
        style={{
          width: size,
          height: size,
          backgroundColor: color,
          transform: `translate(${x}px, ${y}px)`,
        }}
      />
    </div>
  );
}

export default function SuccessAnimation({ show = false, onComplete }) {
  const [visible, setVisible] = useState(false);
  const particles = 20;

  useEffect(() => {
    if (!show) { setVisible(false); return; }
    setVisible(true);
    const t = setTimeout(() => {
      setVisible(false);
      onComplete?.();
    }, 1800);
    return () => clearTimeout(t);
  }, [show, onComplete]);

  if (!visible) return null;

  return (
    <div className="flex justify-center py-4" role="status" aria-label="Import successful">
      <div className="relative">
        <div className="relative flex items-center justify-center w-20 h-20">
          <div className="absolute inset-0 rounded-full bg-emerald-100 dark:bg-emerald-900/40 animate-success-ring" />
          <div className="absolute inset-2 rounded-full bg-emerald-200 dark:bg-emerald-800/40 animate-success-ring" style={{ animationDelay: "0.15s" }} />
          <div className="relative z-10 w-12 h-12 rounded-full bg-gradient-to-br from-emerald-400 to-green-500 flex items-center justify-center shadow-lg shadow-emerald-500/30 animate-success-check">
            <FiCheck className="w-6 h-6 text-white" />
          </div>
        </div>
        {Array.from({ length: particles }).map((_, i) => (
          <Particle key={i} index={i} />
        ))}
      </div>
    </div>
  );
}
