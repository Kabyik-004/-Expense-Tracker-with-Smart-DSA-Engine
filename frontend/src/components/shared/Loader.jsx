export default function Loader({
  type = "spinner",
  size = "md",
  color = "border-indigo-600",
  text,
  fullPage = false,
  count = 3,
}) {
  if (type === "skeleton") {
    return (
      <div className={`${fullPage ? "py-16 px-4" : ""} animate-pulse space-y-3`}>
        {Array.from({ length: count }).map((_, i) => (
          <div key={i}>
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-3" />
            <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded mb-2" />
            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2" />
          </div>
        ))}
      </div>
    );
  }

  const spinnerSizes = { sm: "h-8 w-8", md: "h-10 w-10", lg: "h-12 w-12" };

  return (
    <div className={`flex flex-col items-center ${fullPage ? "justify-center min-h-[60vh]" : "py-16"}`}>
      <div className={`animate-spin rounded-full ${spinnerSizes[size] || spinnerSizes.md} border-b-2 ${color} mb-4`} />
      {text && <p className="text-gray-400 dark:text-gray-500 text-sm">{text}</p>}
    </div>
  );
}
