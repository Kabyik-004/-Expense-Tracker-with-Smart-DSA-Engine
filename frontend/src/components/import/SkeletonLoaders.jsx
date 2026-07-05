function SkeletonBar({ className = "" }) {
  return (
    <div className={`animate-skeleton-pulse rounded-lg bg-gray-200 dark:bg-gray-700/60 ${className}`} aria-hidden="true" />
  );
}

function SkeletonCircle({ size = "w-10 h-10" }) {
  return (
    <div className={`${size} rounded-full animate-skeleton-pulse bg-gray-200 dark:bg-gray-700/60`} aria-hidden="true" />
  );
}

export function SummarySkeleton() {
  return (
    <div className="space-y-5 animate-fade-in" role="status" aria-label="Loading summary">
      <div className="flex items-center gap-3">
        <SkeletonCircle size="w-10 h-10" />
        <div className="space-y-2">
          <SkeletonBar className="h-4 w-44" />
          <SkeletonBar className="h-3 w-64" />
        </div>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-7 gap-3">
        {Array.from({ length: 7 }).map((_, i) => (
          <div key={i} className="rounded-2xl border border-gray-200/40 dark:border-gray-800/30 bg-white/40 dark:bg-gray-900/30 backdrop-blur-xl p-4 space-y-3">
            <SkeletonCircle size="w-9 h-9" />
            <SkeletonBar className="h-7 w-16" />
            <SkeletonBar className="h-3 w-20" />
          </div>
        ))}
      </div>
      <div className="flex justify-center pt-2">
        <SkeletonBar className="h-10 w-52 rounded-2xl" />
      </div>
    </div>
  );
}

export function PreviewSkeleton() {
  return (
    <div className="space-y-4 animate-fade-in" role="status" aria-label="Loading preview">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="rounded-2xl border border-gray-200/40 dark:border-gray-800/30 bg-white/30 dark:bg-gray-900/20 backdrop-blur-xl p-5">
            <div className="flex items-center gap-3">
              <SkeletonCircle size="w-10 h-10" />
              <div className="space-y-2">
                <SkeletonBar className="h-3 w-14" />
                <SkeletonBar className="h-5 w-10" />
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="rounded-2xl border border-gray-200/40 dark:border-gray-800/30 bg-white/30 dark:bg-gray-900/20 backdrop-blur-xl overflow-hidden">
        <div className="p-4 border-b border-gray-100 dark:border-gray-800/50">
          <div className="flex gap-6">
            {Array.from({ length: 6 }).map((_, i) => (
              <SkeletonBar key={i} className="h-4 flex-1" />
            ))}
          </div>
        </div>
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="p-4 border-b border-gray-100 dark:border-gray-800/30 last:border-0">
            <div className="flex gap-6 items-center">
              <SkeletonBar className="h-3.5 w-8" />
              <SkeletonBar className="h-3.5 flex-1" />
              <SkeletonBar className="h-3.5 w-24" />
              <SkeletonBar className="h-3.5 w-16" />
              <SkeletonBar className="h-3.5 w-20" />
              <SkeletonBar className="h-3.5 w-16" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function ImportProgressSkeleton() {
  return (
    <div className="space-y-4 animate-fade-in" role="status" aria-label="Importing transactions">
      <div className="flex items-center justify-center py-12">
        <div className="flex flex-col items-center gap-4">
          <div className="relative">
            <div className="w-16 h-16 border-4 border-indigo-200 dark:border-indigo-800/50 border-t-indigo-600 rounded-full animate-spin" />
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-6 h-6 rounded-full bg-indigo-100 dark:bg-indigo-900/50 animate-ping" />
            </div>
          </div>
          <div className="space-y-2 text-center">
            <SkeletonBar className="h-4 w-40 mx-auto" />
            <SkeletonBar className="h-3 w-56 mx-auto" />
          </div>
        </div>
      </div>
    </div>
  );
}
