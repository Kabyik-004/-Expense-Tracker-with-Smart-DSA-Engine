import {
  FiLayers,
  FiSearch,
  FiCrosshair,
  FiFilter,
} from "react-icons/fi";

const algorithms = [
  {
    icon: FiLayers,
    title: "Stack",
    purpose:
      "LIFO-based undo engine that reverses expense and income operations in constant time.",
    complexity: "O(1) push / pop",
    uses: [
      { label: "Undo Expense" },
      { label: "Undo Income" },
      { label: "Stack Status" },
    ],
    gradient: "from-red-500 to-orange-500",
  },
  {
    icon: FiSearch,
    title: "Linear Search",
    purpose:
      "Sequential scan matching transactions by title, description or category with case-insensitive comparison.",
    complexity: "O(n)",
    uses: [
      { label: "Search by Title" },
      { label: "Search by Description" },
      { label: "Search by Category" },
    ],
    gradient: "from-blue-500 to-cyan-500",
  },
  {
    icon: FiCrosshair,
    title: "Binary Search",
    purpose:
      "Divide-and-conquer lookup on sorted data for instant retrieval by ID, exact date or date range.",
    complexity: "O(log n)",
    uses: [
      { label: "Search by ID" },
      { label: "Search by Date" },
      { label: "Date Range Query" },
    ],
    gradient: "from-purple-500 to-pink-500",
  },
  {
    icon: FiFilter,
    title: "Merge Sort",
    purpose:
      "Stable divide-and-conquer sorting across one or multiple fields with guaranteed O(n log n) performance.",
    complexity: "O(n log n)",
    uses: [
      { label: "Single Field Sort" },
      { label: "Multi Field Sort" },
      { label: "Stable Ordering" },
    ],
    gradient: "from-emerald-500 to-teal-500",
  },
];

export default function DSASection() {
  return (
    <section
      id="algorithms"
      className="relative py-24 lg:py-32 bg-gradient-to-br from-indigo-50/80 via-white to-purple-50/80 dark:from-indigo-950 dark:via-gray-950 dark:to-purple-950 overflow-hidden"
    >
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-10 left-10 w-72 h-72 rounded-full bg-indigo-400/10 dark:bg-indigo-500/5 blur-3xl" />
        <div className="absolute bottom-10 right-10 w-96 h-96 rounded-full bg-purple-400/10 dark:bg-purple-500/5 blur-3xl" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] rounded-full bg-gradient-to-r from-violet-400/5 to-fuchsia-400/5 blur-3xl" />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <p className="text-indigo-600 dark:text-indigo-400 font-semibold text-sm tracking-wide uppercase mb-3">
            Smart DSA Engine
          </p>
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white tracking-tight">
            Algorithms That Power{" "}
            <span className="bg-gradient-to-r from-indigo-600 to-purple-600 dark:from-indigo-400 dark:to-purple-400 bg-clip-text text-transparent">
              Every Feature
            </span>
          </h2>
          <p className="mt-4 text-lg text-gray-600 dark:text-gray-400">
            Unlike traditional trackers, this app implements core computer
            science data structures and algorithms directly into the user
            experience — making search, sort, and undo operations
            production-grade.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {algorithms.map((algo) => {
            const Icon = algo.icon;
            return (
              <article
                key={algo.title}
                className="group relative bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl border border-gray-200/50 dark:border-gray-700/50 p-6 lg:p-8 transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl hover:shadow-indigo-500/10 hover:border-indigo-300/50 dark:hover:border-indigo-600/50"
              >
                <div className="flex items-start gap-5">
                  <div
                    className={`shrink-0 w-12 h-12 rounded-xl bg-gradient-to-br ${algo.gradient} flex items-center justify-center shadow-lg`}
                  >
                    <Icon className="w-5 h-5 text-white" />
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 flex-wrap mb-1">
                      <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                        {algo.title}
                      </h3>
                      <span className="px-2.5 py-0.5 text-[11px] font-mono font-semibold rounded-full bg-indigo-100 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300 border border-indigo-200/50 dark:border-indigo-700/50">
                        {algo.complexity}
                      </span>
                    </div>

                    <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                      {algo.purpose}
                    </p>

                    <div className="mt-4 flex flex-wrap gap-2">
                      {algo.uses.map((use) => (
                        <span
                          key={use.label}
                          className="px-3 py-1 text-xs font-medium rounded-lg bg-gray-100 dark:bg-gray-700/50 text-gray-700 dark:text-gray-300 border border-gray-200/50 dark:border-gray-600/50 transition-colors duration-200 group-hover:bg-indigo-50 dark:group-hover:bg-indigo-900/30 group-hover:text-indigo-700 dark:group-hover:text-indigo-300 group-hover:border-indigo-200/50 dark:group-hover:border-indigo-700/50"
                        >
                          {use.label}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="absolute inset-x-6 bottom-0 h-0.5 bg-gradient-to-r from-indigo-500 to-purple-500 scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left rounded-full" />
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}
