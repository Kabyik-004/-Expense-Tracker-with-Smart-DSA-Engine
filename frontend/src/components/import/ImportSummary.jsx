import { useMemo, useCallback, useState } from "react";
import {
  FiCheck,
  FiX,
  FiCopy,
  FiAlertCircle,
  FiTrendingUp,
  FiTrendingDown,
  FiClock,
  FiDownload,
} from "react-icons/fi";
import SuccessAnimation from "./SuccessAnimation";

function formatDur(seconds) {
  if (!seconds || seconds < 0) return "—";
  if (seconds < 1) return `${Math.round(seconds * 1000)}ms`;
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  const m = Math.floor(seconds / 60);
  const s = Math.round(seconds % 60);
  return `${m}m ${s}s`;
}

function csvEscape(val) {
  if (val === null || val === undefined) return "";
  const s = String(val);
  if (s.includes(",") || s.includes('"') || s.includes("\n")) {
    return `"${s.replace(/"/g, '""')}"`;
  }
  return s;
}

export default function ImportSummary({
  importData,
  transactions,
  fileMeta,
  previewMeta,
  parsingTime,
}) {
  const [celebrated, setCelebrated] = useState(false);

  const stats = useMemo(() => {
    const r = importData?.results || {};
    const imported = r.imported || 0;
    const skipped = r.skipped || 0;
    const replaced = r.replaced || 0;
    const errors = r.errors || [];
    const expenseCount = importData?.created_expense_ids?.length || 0;
    const incomeCount = importData?.created_income_ids?.length || 0;
    const duplicateCount = transactions?.filter((t) => t.duplicate).length || 0;
    return { imported, skipped, replaced, errors, expenseCount, incomeCount, duplicateCount };
  }, [importData, transactions]);

  const handleDownloadCsv = useCallback(() => {
    const headers = ["Row", "Date", "Description", "Amount", "Type", "Category", "Status", "Action", "Error"];
    const rows = (transactions || []).map((tx) => [
      (tx.row_index ?? 0) + 1,
      tx.date || "",
      tx.description || "",
      tx.amount != null ? tx.amount.toFixed(2) : "",
      (tx.debit || 0) > 0 ? "Debit" : "Credit",
      tx.suggested_category || "",
      tx.valid ? "Valid" : "Invalid",
      stats.duplicateCount > 0 && tx.duplicate ? "Duplicate" : tx.valid ? "Imported" : "Skipped",
      (tx.errors || []).join("; "),
    ]);

    const csv = [
      headers.join(","),
      ...rows.map((r) => r.map(csvEscape).join(",")),
    ].join("\n");

    const blob = new Blob(["\ufeff" + csv], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `import-report-${fileMeta?.id || "unknown"}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }, [transactions, fileMeta, stats.duplicateCount]);

  const cards = [
    {
      label: "Imported",
      value: stats.imported,
      icon: FiCheck,
      color: "emerald",
      desc: "Transactions imported",
    },
    {
      label: "Expenses",
      value: stats.expenseCount,
      icon: FiTrendingDown,
      color: "red",
      desc: "Debit transactions",
    },
    {
      label: "Income",
      value: stats.incomeCount,
      icon: FiTrendingUp,
      color: "green",
      desc: "Credit transactions",
    },
    {
      label: "Skipped",
      value: stats.skipped,
      icon: FiX,
      color: "gray",
      desc: "Transactions skipped",
    },
    {
      label: "Replaced",
      value: stats.replaced,
      icon: FiCopy,
      color: "orange",
      desc: "Existing records updated",
    },
    {
      label: "Duplicates",
      value: stats.duplicateCount,
      icon: FiAlertCircle,
      color: "amber",
      desc: "Potential duplicates detected",
    },
    {
      label: "Errors",
      value: stats.errors.length,
      icon: FiAlertCircle,
      color: "red",
      desc: "Rows with issues",
    },
    {
      label: "Parsing Time",
      value: formatDur(parsingTime),
      icon: FiClock,
      color: "emerald",
      desc: "File processing duration",
    },
  ];

  const colorClasses = {
    emerald: { bg: "bg-emerald-100 dark:bg-emerald-900/40", icon: "text-emerald-600 dark:text-emerald-400" },
    red: { bg: "bg-red-100 dark:bg-red-900/40", icon: "text-red-600 dark:text-red-400" },
    green: { bg: "bg-green-100 dark:bg-green-900/40", icon: "text-green-600 dark:text-green-400" },
    gray: { bg: "bg-gray-100 dark:bg-gray-800/60", icon: "text-gray-500 dark:text-gray-400" },
    orange: { bg: "bg-orange-100 dark:bg-orange-900/40", icon: "text-orange-600 dark:text-orange-400" },
    amber: { bg: "bg-amber-100 dark:bg-amber-900/40", icon: "text-amber-600 dark:text-amber-400" },
  };

  return (
    <div className="w-full space-y-6 animate-fade-in" role="region" aria-label="Import results summary">
      {/* Success animation */}
      {!celebrated && (
        <SuccessAnimation show={!celebrated} onComplete={() => setCelebrated(true)} />
      )}

      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-[14px] bg-emerald-100 dark:bg-emerald-900/40 flex items-center justify-center">
          <FiCheck className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white" id="import-summary-heading">
            Import Complete
          </h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {stats.imported} transaction{stats.imported !== 1 ? "s" : ""} imported successfully
            {stats.replaced > 0 ? `, ${stats.replaced} replaced` : ""}
            {stats.skipped > 0 ? `, ${stats.skipped} skipped` : ""}
          </p>
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-8 gap-3" role="list" aria-label="Statistics">
        {cards.map((card, idx) => {
          const cc = colorClasses[card.color] || colorClasses.gray;
          const Icon = card.icon;
          return (
            <div
              key={card.label}
              className="relative overflow-hidden rounded-2xl border border-gray-200/40 dark:border-gray-800/30 bg-white/40 dark:bg-gray-900/30 backdrop-blur-xl p-4 transition-all duration-300 hover:shadow-lg hover:border-emerald-200/50 dark:hover:border-emerald-600/30 card-hover"
              role="listitem"
              style={{ animationDelay: `${idx * 40}ms` }}
            >
              <div className="flex items-start justify-between mb-3">
                <div className={`w-9 h-9 rounded-xl ${cc.bg} flex items-center justify-center`}>
                  <Icon className={`w-4 h-4 ${cc.icon}`} aria-hidden="true" />
                </div>
              </div>
              <p className="text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
                {card.value}
              </p>
              <p className="text-[11px] font-medium text-gray-400 dark:text-gray-500 mt-0.5 uppercase tracking-wider">
                {card.label}
              </p>
              <p className="text-[10px] text-gray-400 dark:text-gray-500 mt-0.5">{card.desc}</p>
            </div>
          );
        })}
      </div>

      {/* File metadata bar */}
      {fileMeta && (
        <div className="flex items-center gap-4 flex-wrap text-xs text-gray-400 dark:text-gray-500 px-1" aria-label="File information">
          <span>File: <span className="font-medium text-gray-600 dark:text-gray-300">{fileMeta.filename}</span></span>
          {previewMeta?.detected_bank && (
            <span>Bank: <span className="font-medium text-gray-600 dark:text-gray-300">{previewMeta.detected_bank}</span></span>
          )}
          <span>Parser: <span className="font-medium text-gray-600 dark:text-gray-300">{previewMeta?.parser || "—"}</span></span>
        </div>
      )}

      {/* Errors detail */}
      {stats.errors.length > 0 && (
        <div className="rounded-2xl border border-red-200/40 dark:border-red-800/30 bg-red-50/30 dark:bg-red-950/20 backdrop-blur-sm p-4" role="alert">
          <p className="text-xs font-semibold text-red-700 dark:text-red-300 uppercase tracking-wider mb-2">
            Errors ({stats.errors.length})
          </p>
          <ul className="space-y-1">
            {stats.errors.slice(0, 10).map((e, i) => (
              <li key={i} className="text-xs text-red-600 dark:text-red-400 flex items-start gap-2">
                <span className="shrink-0 mt-0.5" aria-hidden="true">•</span>
                <span>Row {e.row != null ? e.row + 1 : "?"}: {e.error}</span>
              </li>
            ))}
            {stats.errors.length > 10 && (
              <li className="text-xs text-gray-400 dark:text-gray-500">...and {stats.errors.length - 10} more</li>
            )}
          </ul>
        </div>
      )}

      {/* Download report */}
      <div className="flex justify-center">
        <button
          onClick={handleDownloadCsv}
          className="inline-flex items-center gap-2.5 px-6 py-3 text-sm font-semibold text-emerald-700 dark:text-emerald-300 bg-emerald-50/80 dark:bg-emerald-900/30 border border-emerald-200/50 dark:border-emerald-700/40 rounded-2xl hover:bg-emerald-100 dark:hover:bg-emerald-900/50 transition-all backdrop-blur-sm btn-hover"
          aria-label="Download import report as CSV"
        >
          <FiDownload className="w-4 h-4" aria-hidden="true" />
          Download Report (CSV)
        </button>
      </div>
    </div>
  );
}
