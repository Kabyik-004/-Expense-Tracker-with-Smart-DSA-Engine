import { useState, useEffect, useRef, useCallback } from "react";
import { FiShield, FiServer, FiGrid, FiCpu, FiSmartphone, FiUploadCloud } from "react-icons/fi";

const stats = [
  {
    icon: FiServer,
    value: 20,
    suffix: "+",
    label: "REST APIs",
    gradient: "from-emerald-600 to-blue-600",
    iconBg: "bg-emerald-500/20",
  },
  {
    icon: FiGrid,
    value: 10,
    suffix: "+",
    label: "Major Modules",
    gradient: "from-emerald-600 to-pink-600",
    iconBg: "bg-emerald-500/20",
  },
  {
    icon: FiCpu,
    value: 8,
    suffix: "+",
    label: "Algorithms",
    gradient: "from-emerald-500 to-teal-600",
    iconBg: "bg-emerald-500/20",
  },
  {
    icon: FiSmartphone,
    value: 100,
    suffix: "%",
    label: "Responsive",
    gradient: "from-orange-500 to-rose-600",
    iconBg: "bg-orange-500/20",
  },
  {
    icon: FiUploadCloud,
    value: 3,
    suffix: "+",
    label: "File Formats",
    gradient: "from-emerald-500 to-emerald-600",
    iconBg: "bg-emerald-500/20",
  },
  {
    icon: FiShield,
    value: null,
    suffix: null,
    label: "Authentication",
    badge: "JWT",
    gradient: "from-cyan-500 to-blue-600",
    iconBg: "bg-cyan-500/20",
  },
];

function AnimatedCounter({ target, suffix, duration = 2000 }) {
  const [count, setCount] = useState(0);
  const ref = useRef(null);
  const hasAnimated = useRef(false);

  const animate = useCallback(() => {
    if (hasAnimated.current) return;
    hasAnimated.current = true;

    const start = performance.now();

    function step(now) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = Math.min(Math.floor(eased * target), target);
      setCount(current);
      if (progress < 1) {
        requestAnimationFrame(step);
      }
    }

    requestAnimationFrame(step);
  }, [target, duration]);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          animate();
          observer.unobserve(el);
        }
      },
      { threshold: 0.3 }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [animate]);

  return (
    <span ref={ref} className="tabular-nums">
      {count}
      {suffix}
    </span>
  );
}

export default function Stats() {
  return (
    <section className="relative py-24 lg:py-32 bg-white dark:bg-gray-950">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <p className="text-emerald-600 dark:text-emerald-400 font-semibold text-sm tracking-wide uppercase mb-3">
            By the Numbers
          </p>
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white tracking-tight">
            Built with{" "}
            <span className="text-emerald-600 dark:text-emerald-400">Precision</span>
          </h2>
          <p className="mt-4 text-lg text-gray-600 dark:text-gray-400">
            Every component, API and algorithm is crafted for performance and
            reliability.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-4 max-w-5xl mx-auto">
          {stats.map((stat) => (
            <article
              key={stat.label}
              className={`group relative overflow-hidden rounded-2xl bg-gradient-to-br ${stat.gradient} p-6 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl`}
            >
              <div className="absolute inset-0 bg-white/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

              <div className="relative z-10">
                <div
                  className={`inline-flex items-center justify-center w-10 h-10 rounded-xl ${stat.iconBg} backdrop-blur-sm mb-4`}
                >
                  <stat.icon className="w-5 h-5 text-white" />
                </div>

                {stat.value !== null ? (
                  <p className="text-3xl lg:text-4xl font-bold text-white tracking-tight">
                    <AnimatedCounter
                      target={stat.value}
                      suffix={stat.suffix}
                    />
                  </p>
                ) : (
                  <p className="text-2xl lg:text-3xl font-bold text-white tracking-tight">
                    {stat.badge}
                  </p>
                )}

                <p className="text-sm text-white/80 mt-1.5 font-medium">
                  {stat.label}
                </p>
              </div>

              <div className="absolute -bottom-4 -right-4 w-24 h-24 rounded-full bg-white/5 blur-xl group-hover:scale-150 transition-transform duration-500" />
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
