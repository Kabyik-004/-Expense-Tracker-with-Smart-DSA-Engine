import {
  FiDollarSign,
  FiTrendingUp,
  FiBarChart2,
  FiTarget,
  FiLock,
  FiRotateCcw,
  FiSearch,
  FiFilter,
  FiMonitor,
  FiCloud,
  FiUploadCloud,
} from "react-icons/fi";

const features = [
  {
    icon: FiUploadCloud,
    title: "Smart Bank Statement Import",
    description:
      "Upload PDF, CSV or Excel bank statements and automatically extract, categorize and import transactions into your expense tracker with intelligent parsing.",
    color: "text-emerald-600",
    bg: "bg-emerald-100 dark:bg-emerald-900/30",
    premium: true,
  },
  {
    icon: FiDollarSign,
    title: "Expense Management",
    description: "Track every transaction with detailed categories and payment methods.",
    color: "text-red-600",
    bg: "bg-red-100 dark:bg-red-900/30",
  },
  {
    icon: FiTrendingUp,
    title: "Income Tracking",
    description: "Log and monitor multiple income sources with recurring support.",
    color: "text-green-600",
    bg: "bg-green-100 dark:bg-green-900/30",
  },
  {
    icon: FiBarChart2,
    title: "Dashboard Analytics",
    description: "Visualize spending patterns with interactive charts and insights.",
    color: "text-emerald-600",
    bg: "bg-emerald-100 dark:bg-emerald-900/30",
  },
  {
    icon: FiTarget,
    title: "Budget Planning",
    description: "Set monthly budgets per category and track progress in real time.",
    color: "text-emerald-600",
    bg: "bg-emerald-100 dark:bg-emerald-900/30",
  },
  {
    icon: FiLock,
    title: "Secure JWT Authentication",
    description: "Industry-standard authentication with encrypted password hashing.",
    color: "text-amber-600",
    bg: "bg-amber-100 dark:bg-amber-900/30",
  },
  {
    icon: FiRotateCcw,
    title: "Undo Operations",
    description: "Stack-based undo system supporting expense and income rollbacks.",
    color: "text-cyan-600",
    bg: "bg-cyan-100 dark:bg-cyan-900/30",
  },
  {
    icon: FiSearch,
    title: "Search Engine",
    description: "Linear and binary search algorithms for fast transaction lookup.",
    color: "text-blue-600",
    bg: "bg-blue-100 dark:bg-blue-900/30",
  },
  {
    icon: FiFilter,
    title: "Sorting Engine",
    description: "Merge sort, quick sort and heap sort for multi-field ordering.",
    color: "text-teal-600",
    bg: "bg-teal-100 dark:bg-teal-900/30",
  },
  {
    icon: FiMonitor,
    title: "Responsive UI",
    description: "Seamless experience across desktop, tablet and mobile devices.",
    color: "text-emerald-600",
    bg: "bg-emerald-100 dark:bg-emerald-900/30",
  },
  {
    icon: FiCloud,
    title: "Cloud Deployment",
    description: "Deployed on Vercel and Render with PostgreSQL and Docker.",
    color: "text-sky-600",
    bg: "bg-sky-100 dark:bg-sky-900/30",
  },
];

export default function Features() {
  return (
    <section id="features" className="relative py-24 lg:py-32 bg-gray-50/50 dark:bg-gray-900/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <p className="text-emerald-600 dark:text-emerald-400 font-semibold text-sm tracking-wide uppercase mb-3">
            Features
          </p>
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white tracking-tight">
            Built for Modern{" "}
            <span className="text-emerald-600 dark:text-emerald-400">Finance</span>{" "}
            Management
          </h2>
          <p className="mt-4 text-lg text-gray-600 dark:text-gray-400">
            Everything you need to take control of your personal finances in one
            place.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-5">
          {features.map((feature) => (
            <article
              key={feature.title}
              className={`group relative bg-white dark:bg-gray-800/50 rounded-xl border border-gray-100 dark:border-gray-800 p-6 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl ${
                feature.premium
                  ? "hover:border-emerald-300/60 dark:hover:border-emerald-600/60 shadow-emerald-500/5 hover:shadow-emerald-500/10"
                  : "hover:border-emerald-200/50 dark:hover:border-emerald-800/50"
              }`}
            >
              {feature.premium && (
                <div className="absolute -top-2.5 right-4 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-widest rounded-full bg-gradient-to-r from-emerald-600 to-emerald-600 text-white shadow-lg">
                  Premium
                </div>
              )}
              <div
                className={`w-11 h-11 rounded-lg ${feature.bg} flex items-center justify-center mb-4 transition-transform duration-300 group-hover:scale-110 group-hover:rotate-3`}
              >
                <feature.icon className={`w-5 h-5 ${feature.color}`} />
              </div>
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-1.5">
                {feature.title}
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
                {feature.description}
              </p>
              <div className="absolute inset-x-6 bottom-0 h-0.5 bg-gradient-to-r from-emerald-500 to-emerald-500 scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left rounded-full" />
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
