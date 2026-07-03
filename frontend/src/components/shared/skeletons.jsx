export function SkeletonLine({ className = "" }) {
  return <div className={`h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse ${className}`} />;
}

export function SkeletonBadge({ className = "" }) {
  return <div className={`h-5 w-16 bg-gray-200 dark:bg-gray-700 rounded-full animate-pulse ${className}`} />;
}

export function SkeletonAvatar({ size = "w-8 h-8", className = "" }) {
  return <div className={`${size} bg-gray-200 dark:bg-gray-700 rounded-full animate-pulse shrink-0 ${className}`} />;
}

export function SkeletonCard({ children, className = "" }) {
  return (
    <div className={`bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6 ${className}`}>
      {children}
    </div>
  );
}

export function SkeletonProgressBar({ className = "" }) {
  return (
    <div className={`w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 animate-pulse ${className}`}>
      <div className="h-3 rounded-full bg-gray-300 dark:bg-gray-600" style={{ width: "60%" }} />
    </div>
  );
}

export function SkeletonStatCard() {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6 animate-pulse">
      <div className="flex items-start justify-between">
        <div className="flex-1 space-y-2">
          <SkeletonLine className="w-1/2" />
          <SkeletonLine className="w-3/4 h-6" />
          <SkeletonLine className="w-1/3" />
        </div>
        <div className="w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded-xl shrink-0" />
      </div>
    </div>
  );
}

export function SkeletonTableRow({ cols = 5 }) {
  return (
    <tr className="border-b border-gray-50 dark:border-gray-700 animate-pulse">
      {Array.from({ length: cols }).map((_, i) => (
        <td key={i} className="px-4 py-3.5">
          <div className={`h-4 bg-gray-200 dark:bg-gray-700 rounded ${i === 0 ? "w-3/4" : i === cols - 1 ? "w-1/3" : "w-1/2"}`} />
        </td>
      ))}
    </tr>
  );
}

export function SkeletonTable({ rows = 5, cols = 5, className = "" }) {
  return (
    <div className={`animate-pulse ${className}`}>
      <div className="border-b border-gray-100 dark:border-gray-700 bg-gray-50/80 dark:bg-gray-900/80">
        <div className="flex px-4 py-3 gap-4">
          {Array.from({ length: cols }).map((_, i) => (
            <div key={i} className={`h-3 bg-gray-200 dark:bg-gray-600 rounded w-16 flex-1`} />
          ))}
        </div>
      </div>
      {Array.from({ length: rows }).map((_, i) => (
        <SkeletonTableRow key={i} cols={cols} />
      ))}
    </div>
  );
}

export function SkeletonChart({ className = "" }) {
  return (
    <div className={`bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6 animate-pulse ${className}`}>
      <div className="flex items-center gap-2 mb-4">
        <div className="w-5 h-5 bg-gray-200 dark:bg-gray-700 rounded" />
        <SkeletonLine className="w-1/3" />
      </div>
      <div className="h-[280px] sm:h-[320px] bg-gray-100 dark:bg-gray-700/50 rounded-xl flex items-center justify-center">
        <div className="w-16 h-16 bg-gray-200 dark:bg-gray-600 rounded-full" />
      </div>
    </div>
  );
}

export function SkeletonDashboard() {
  return (
    <div className="space-y-6">
      <div className="animate-pulse">
        <SkeletonLine className="w-1/4 h-8 mb-6" />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <SkeletonStatCard key={i} />
        ))}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden animate-pulse">
          <div className="p-6 border-b border-gray-100 dark:border-gray-700">
            <SkeletonLine className="w-1/4" />
          </div>
          <div className="p-6 space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-center gap-4">
                <SkeletonAvatar size="w-10 h-10" />
                <div className="flex-1 space-y-1">
                  <SkeletonLine className="w-1/2" />
                  <SkeletonLine className="w-1/4" />
                </div>
                <SkeletonLine className="w-20" />
              </div>
            ))}
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6 animate-pulse space-y-4">
          <SkeletonLine className="w-1/2" />
          {[1, 2, 3, 4].map((i) => (
            <SkeletonLine key={i} className="w-full h-10" />
          ))}
          <div className="pt-4 border-t border-gray-100 dark:border-gray-700 space-y-3">
            <SkeletonLine className="w-1/3" />
            <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg space-y-2">
              <SkeletonLine className="w-1/4" />
              <SkeletonLine className="w-1/2 h-6" />
              <SkeletonLine className="w-1/3" />
            </div>
            <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg space-y-2">
              <SkeletonLine className="w-1/4" />
              <SkeletonLine className="w-1/2 h-6" />
              <SkeletonLine className="w-1/3" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export function SkeletonAnalytics() {
  return (
    <div className="space-y-6">
      <div className="animate-pulse">
        <SkeletonLine className="w-1/4 h-7 mb-1" />
        <SkeletonLine className="w-1/3" />
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        {[1, 2, 3, 4].map((i) => (
          <SkeletonStatCard key={i} />
        ))}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SkeletonChart />
        <SkeletonChart />
        <div className="lg:col-span-2 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6 animate-pulse">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-5 h-5 bg-gray-200 dark:bg-gray-700 rounded" />
            <SkeletonLine className="w-1/4" />
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="h-[250px] bg-gray-100 dark:bg-gray-700/50 rounded-xl" />
            <div className="h-[250px] bg-gray-100 dark:bg-gray-700/50 rounded-xl" />
          </div>
        </div>
      </div>
    </div>
  );
}

export function SkeletonExpensesTable({ rows = 5 }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b border-gray-100 dark:border-gray-700 space-y-3 animate-pulse">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <div className="w-full h-10 bg-gray-200 dark:bg-gray-700 rounded-lg" />
          </div>
          <div className="w-24 h-10 bg-gray-200 dark:bg-gray-700 rounded-lg" />
        </div>
        <div className="flex gap-2">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-8 w-20 bg-gray-200 dark:bg-gray-700 rounded-lg" />
          ))}
        </div>
      </div>
      <div className="hidden md:block overflow-x-auto">
        <SkeletonTable rows={rows} cols={6} />
      </div>
      <div className="md:hidden divide-y divide-gray-100 dark:divide-gray-700 animate-pulse">
        {[1, 2, 3].map((i) => (
          <div key={i} className="p-4 space-y-2">
            <div className="flex items-start gap-3">
              <SkeletonAvatar size="w-10 h-10" />
              <div className="flex-1 space-y-1">
                <SkeletonLine className="w-1/2" />
                <SkeletonLine className="w-1/3" />
              </div>
              <SkeletonLine className="w-16" />
            </div>
            <div className="flex gap-2 pt-2 border-t border-gray-50 dark:border-gray-700">
              {[1, 2, 3].map((j) => (
                <div key={j} className="flex-1 h-8 bg-gray-200 dark:bg-gray-700 rounded-lg" />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function SkeletonIncomesTable({ rows = 5 }) {
  return <SkeletonExpensesTable rows={rows} />;
}

export function SkeletonBudgets() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between animate-pulse">
        <div className="space-y-1">
          <SkeletonLine className="w-32 h-7" />
          <SkeletonLine className="w-48" />
        </div>
        <SkeletonLine className="w-28 h-10" />
      </div>
      <div className="flex items-center justify-center animate-pulse">
        <div className="w-full max-w-xs h-12 bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 flex items-center justify-center gap-4">
          <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-lg" />
          <SkeletonLine className="w-24" />
          <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-lg" />
        </div>
      </div>
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6 animate-pulse space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <SkeletonLine className="w-32" />
                <SkeletonBadge />
              </div>
              <SkeletonLine className="w-6 h-6" />
            </div>
            <SkeletonProgressBar />
            <div className="flex justify-between">
              <SkeletonLine className="w-20" />
              <SkeletonLine className="w-12" />
              <SkeletonLine className="w-20" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function SkeletonSettingsActivity({ rows = 3 }) {
  return (
    <div className="space-y-3 animate-pulse">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex items-center gap-3">
          <SkeletonAvatar size="w-8 h-8" className="rounded-lg" />
          <div className="flex-1 space-y-1">
            <SkeletonLine className="w-3/4" />
            <SkeletonLine className="w-1/4" />
          </div>
        </div>
      ))}
    </div>
  );
}
