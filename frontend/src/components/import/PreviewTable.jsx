import { useState, useMemo, useCallback } from "react";
import {
  FiSearch,
  FiX,
  FiChevronUp,
  FiChevronDown,
  FiChevronsLeft,
  FiChevronLeft,
  FiChevronRight,
  FiChevronsRight,
  FiEdit2,
  FiTrash2,
  FiCheck,
  FiCheckSquare,
  FiSquare,
  FiAlertCircle,
  FiCopy,
  FiInfo,
} from "react-icons/fi";

const PAGE_SIZE = 10;

const CATEGORIES = [
  "Food & Dining", "Transportation", "Shopping", "Entertainment",
  "Bills & Utilities", "Health", "Education", "Rent", "Groceries",
  "Income", "Transfer", "Other",
];

const TYPE_FILTERS = [
  { value: "all", label: "All" },
  { value: "debit", label: "Debit" },
  { value: "credit", label: "Credit" },
  { value: "duplicate", label: "Duplicates" },
  { value: "invalid", label: "Invalid" },
];

const DUPLICATE_ACTIONS = [
  { value: "import", label: "Import Anyway", desc: "Add as new expense" },
  { value: "skip", label: "Skip", desc: "Do not import this row" },
  { value: "replace", label: "Replace", desc: "Overwrite existing expense" },
];

function resolveType(tx) {
  if (!tx.valid) return "invalid";
  if (tx.duplicate) return "duplicate";
  if ((tx.debit || 0) > 0) return "debit";
  return "credit";
}

function formatAmount(val) {
  if (val === null || val === undefined) return "—";
  return new Intl.NumberFormat("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(val);
}

function formatDateDisplay(dateStr) {
  if (!dateStr) return "—";
  return dateStr;
}

function getStatusBadge(tx) {
  if (!tx.valid) {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-300" title={(tx.errors || []).join("; ")}>
        <FiAlertCircle className="w-3 h-3" />
        {tx.errors?.[0] || "Invalid"}
      </span>
    );
  }
  if (tx.duplicate) {
    const score = tx.duplicate_best_score || 0;
    const color = score >= 80 ? "bg-orange-100 dark:bg-orange-900/40 text-orange-700 dark:text-orange-300" : "bg-amber-100 dark:bg-amber-900/40 text-amber-700 dark:text-amber-300";
    return (
      <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold ${color}`}>
        <FiCopy className="w-3 h-3" />
        Duplicate
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-100 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-300">
      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
      Valid
    </span>
  );
}

function sortData(data, field, direction) {
  if (!field) return data;
  return [...data].sort((a, b) => {
    let va, vb;
    if (field === "date") { va = a.date || ""; vb = b.date || ""; }
    else if (field === "amount") { va = a.amount ?? 0; vb = b.amount ?? 0; }
    else if (field === "description") { va = (a.description || "").toLowerCase(); vb = (b.description || "").toLowerCase(); }
    else if (field === "category") { va = (a.suggested_category || "").toLowerCase(); vb = (b.suggested_category || "").toLowerCase(); }
    else if (field === "type") { va = resolveType(a); vb = resolveType(b); }
    else { va = a[field]; vb = b[field]; }
    if (va < vb) return direction === "asc" ? -1 : 1;
    if (va > vb) return direction === "asc" ? 1 : -1;
    return 0;
  });
}

export default function PreviewTable({
  transactions,
  onUpdate,
  onDelete,
  onCategoryChange,
  onSelectionChange,
  onDuplicateAction,
}) {
  const [search, setSearch] = useState("");
  const [sortField, setSortField] = useState("row_index");
  const [sortDir, setSortDir] = useState("asc");
  const [typeFilter, setTypeFilter] = useState("all");
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState(new Set());
  const [editRow, setEditRow] = useState(null);
  const [editField, setEditField] = useState(null);
  const [editValue, setEditValue] = useState("");
  const [dupActions, setDupActions] = useState({});

  const filtered = useMemo(() => {
    let data = transactions || [];
    if (search.trim()) {
      const q = search.toLowerCase().trim();
      data = data.filter((t) => {
        const desc = (t.description || "").toLowerCase();
        const cat = (t.suggested_category || "").toLowerCase();
        const ref = (t.reference_number || "").toLowerCase();
        return desc.includes(q) || cat.includes(q) || ref.includes(q);
      });
    }
    if (typeFilter !== "all") {
      data = data.filter((t) => resolveType(t) === typeFilter);
    }
    data = sortData(data, sortField, sortDir);
    return data;
  }, [transactions, search, typeFilter, sortField, sortDir]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const safePage = Math.min(page, totalPages);
  const paged = filtered.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE);

  const duplicateCount = useMemo(() =>
    (transactions || []).filter((t) => t.duplicate).length,
  [transactions]);

  const toggleSort = useCallback((field) => {
    if (sortField === field) { setSortDir((d) => (d === "asc" ? "desc" : "asc")); }
    else { setSortField(field); setSortDir("asc"); }
    setPage(1);
  }, [sortField]);

  const handleSelect = useCallback((index) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(index)) next.delete(index);
      else next.add(index);
      onSelectionChange?.(Array.from(next));
      return next;
    });
  }, [onSelectionChange]);

  const handleSelectAll = useCallback(() => {
    const pageIndices = paged.map((t) => t.row_index);
    const allSelected = pageIndices.every((i) => selected.has(i));
    setSelected((prev) => {
      const next = new Set(prev);
      if (allSelected) { pageIndices.forEach((i) => next.delete(i)); }
      else { pageIndices.forEach((i) => next.add(i)); }
      onSelectionChange?.(Array.from(next));
      return next;
    });
  }, [paged, selected, onSelectionChange]);

  const startEdit = useCallback((rowIndex, field, currentValue) => {
    setEditRow(rowIndex);
    setEditField(field);
    setEditValue(currentValue ?? "");
  }, []);

  const saveEdit = useCallback((rowIndex, field) => {
    if (field === "category") { onCategoryChange?.(rowIndex, editValue); }
    else { onUpdate?.(rowIndex, field, editValue); }
    setEditRow(null); setEditField(null); setEditValue("");
  }, [editValue, onUpdate, onCategoryChange]);

  const cancelEdit = useCallback(() => {
    setEditRow(null); setEditField(null); setEditValue("");
  }, []);

  const handleDupAction = useCallback((rowIndex, action) => {
    setDupActions((prev) => ({ ...prev, [rowIndex]: action }));
    onDuplicateAction?.(rowIndex, action);
  }, [onDuplicateAction]);

  const SortIcon = ({ field }) => {
    if (sortField !== field) return <FiChevronUp className="w-3 h-3 opacity-0 group-hover:opacity-40" />;
    return sortDir === "asc"
      ? <FiChevronUp className="w-3 h-3 text-emerald-600 dark:text-emerald-400" />
      : <FiChevronDown className="w-3 h-3 text-emerald-600 dark:text-emerald-400" />;
  };

  return (
    <div className="w-full space-y-4">
      {/* Toolbar */}
      <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
        <div className="relative flex-1 max-w-md w-full">
          <FiSearch className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-gray-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            placeholder="Search transactions..."
            className="w-full pl-10 pr-9 py-2.5 rounded-xl border border-gray-200/60 dark:border-gray-700/50 bg-white/60 dark:bg-gray-900/40 backdrop-blur-sm text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-400/30 focus:border-emerald-400/50 input-focus"
          />
          {search && (
            <button onClick={() => setSearch("")} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
              <FiX className="w-4 h-4" />
            </button>
          )}
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <div className="flex items-center gap-1 bg-white/40 dark:bg-gray-900/30 rounded-xl border border-gray-200/50 dark:border-gray-700/40 p-1">
            {TYPE_FILTERS.map((f) => (
              <button
                key={f.value}
                onClick={() => { setTypeFilter(f.value); setPage(1); }}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  typeFilter === f.value
                    ? "bg-emerald-100 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-300 shadow-sm"
                    : "text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
                } ${f.value === "duplicate" && duplicateCount > 0 ? "ring-1 ring-orange-300 dark:ring-orange-600" : ""}`}
              >
                {f.label}
                {f.value === "duplicate" && duplicateCount > 0 && (
                  <span className="ml-1.5 px-1.5 py-0.5 rounded-full text-[10px] bg-orange-200 dark:bg-orange-800/50 text-orange-700 dark:text-orange-300">{duplicateCount}</span>
                )}
              </button>
            ))}
          </div>

          <span className="text-xs text-gray-400 dark:text-gray-500 whitespace-nowrap">
            {selected.size > 0 ? `${selected.size} selected` : `${filtered.length} rows`}
          </span>
        </div>
      </div>

      {/* Duplicate alert banner */}
      {duplicateCount > 0 && typeFilter !== "duplicate" && (
        <div className="flex items-center gap-3 px-4 py-3 rounded-2xl bg-orange-50/80 dark:bg-orange-950/30 border border-orange-200/50 dark:border-orange-800/40 backdrop-blur-sm">
          <FiCopy className="w-5 h-5 text-orange-600 dark:text-orange-400 shrink-0" />
          <p className="text-sm text-orange-800 dark:text-orange-200">
            {duplicateCount} transaction{duplicateCount > 1 ? "s" : ""} matched existing records.
            <button onClick={() => setTypeFilter("duplicate")} className="ml-2 font-semibold underline underline-offset-2 hover:text-orange-900 dark:hover:text-orange-100">
              Review
            </button>
          </p>
        </div>
      )}

      {/* Table */}
      <div className="overflow-x-auto rounded-2xl border border-gray-200/40 dark:border-gray-800/30 bg-white/40 dark:bg-gray-900/30 backdrop-blur-xl">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200/40 dark:border-gray-800/30">
              <th className="w-10 px-3 py-3.5 text-left">
                <button onClick={handleSelectAll} className="text-gray-400 hover:text-emerald-600 dark:hover:text-emerald-400">
                  {paged.every((t) => selected.has(t.row_index))
                    ? <FiCheckSquare className="w-4 h-4" />
                    : <FiSquare className="w-4 h-4" />
                  }
                </button>
              </th>
              {[
                { key: "row_index", label: "#", sortable: false },
                { key: "date", label: "Date", sortable: true },
                { key: "description", label: "Description", sortable: true },
                { key: "category", label: "Category", sortable: true },
                { key: "type", label: "Type", sortable: true },
                { key: "amount", label: "Amount", sortable: true },
                { key: "status", label: "Status", sortable: false },
                { key: "duplicate_action", label: "Dup Action", sortable: false },
                { key: "actions", label: "", sortable: false },
              ].map((col) => (
                <th
                  key={col.key}
                  className={`px-3 py-3.5 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider ${
                    col.sortable ? "cursor-pointer select-none group" : ""
                  } ${col.key === "actions" ? "w-16 text-right" : "text-left"} ${col.key === "duplicate_action" ? "w-28" : ""}`}
                  onClick={() => col.sortable && toggleSort(col.key)}
                >
                  <div className="flex items-center gap-1">
                    {col.label}
                    {col.sortable && <SortIcon field={col.key} />}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paged.length === 0 ? (
              <tr>
                <td colSpan={9} className="px-3 py-12 text-center text-sm text-gray-400 dark:text-gray-500">
                  {search || typeFilter !== "all"
                    ? "No transactions match the current filters."
                    : "No transactions to preview."}
                </td>
              </tr>
            ) : (
              paged.map((tx) => {
                const ttype = resolveType(tx);
                const isSelected = selected.has(tx.row_index);
                const isEditing = editRow === tx.row_index;
                const currDupAction = dupActions[tx.row_index] || tx.duplicate_action || "import";
                const dupMatch = tx.duplicate_matches?.[0];

                const rowClasses = `border-b border-gray-100/60 dark:border-gray-800/30 transition-colors ${
                  isSelected ? "bg-emerald-50/50 dark:bg-emerald-950/20" : ""
                } ${
                  !tx.valid ? "bg-red-50/30 dark:bg-red-950/15" : ""
                } ${
                  tx.duplicate ? "bg-orange-50/20 dark:bg-orange-950/10" : ""
                } hover:bg-gray-50/50 dark:hover:bg-gray-800/20`;

                return (
                  <tr key={tx.row_index} className={rowClasses}>
                    <td className="px-3 py-2.5">
                      <button onClick={() => handleSelect(tx.row_index)} className="text-gray-400 hover:text-emerald-600 dark:hover:text-emerald-400">
                        {isSelected ? <FiCheckSquare className="w-4 h-4 text-emerald-600" /> : <FiSquare className="w-4 h-4" />}
                      </button>
                    </td>
                    <td className="px-3 py-2.5 text-xs text-gray-400 dark:text-gray-500">{tx.row_index + 1}</td>

                    {/* Date */}
                    <td className="px-3 py-2.5">
                      {isEditing && editField === "date" ? (
                        <input autoFocus value={editValue} onChange={(e) => setEditValue(e.target.value)} onBlur={() => saveEdit(tx.row_index, "date")} onKeyDown={(e) => e.key === "Enter" && saveEdit(tx.row_index, "date")} className="w-28 px-2 py-1 rounded-lg border border-emerald-300 dark:border-emerald-600 bg-white dark:bg-gray-800 text-xs font-mono focus:outline-none focus:ring-2 focus:ring-emerald-400/30" />
                      ) : (
                        <button onClick={() => startEdit(tx.row_index, "date", tx.date)} className="text-xs font-mono text-gray-700 dark:text-gray-200 hover:text-emerald-600 dark:hover:text-emerald-400">
                          {formatDateDisplay(tx.date)}
                        </button>
                      )}
                    </td>

                    {/* Description */}
                    <td className="px-3 py-2.5 max-w-[240px]">
                      {isEditing && editField === "description" ? (
                        <input autoFocus value={editValue} onChange={(e) => setEditValue(e.target.value)} onBlur={() => saveEdit(tx.row_index, "description")} onKeyDown={(e) => e.key === "Enter" && saveEdit(tx.row_index, "description")} className="w-full px-2 py-1 rounded-lg border border-emerald-300 dark:border-emerald-600 bg-white dark:bg-gray-800 text-xs focus:outline-none focus:ring-2 focus:ring-emerald-400/30" />
                      ) : (
                        <button onClick={() => startEdit(tx.row_index, "description", tx.description)} className="text-xs text-gray-700 dark:text-gray-200 truncate block w-full text-left hover:text-emerald-600 dark:hover:text-emerald-400">
                          {tx.description || <span className="text-gray-400 dark:text-gray-500 italic">—</span>}
                        </button>
                      )}
                    </td>

                    {/* Category */}
                    <td className="px-3 py-2.5">
                      {isEditing && editField === "category" ? (
                        <select autoFocus value={editValue} onChange={(e) => setEditValue(e.target.value)} onBlur={() => saveEdit(tx.row_index, "category")} className="px-2 py-1 rounded-lg border border-emerald-300 dark:border-emerald-600 bg-white dark:bg-gray-800 text-xs focus:outline-none focus:ring-2 focus:ring-emerald-400/30">
                          {CATEGORIES.map((c) => (<option key={c} value={c}>{c}</option>))}
                        </select>
                      ) : (
                        <button onClick={() => startEdit(tx.row_index, "category", tx.suggested_category)} className="group inline-flex items-center gap-1.5">
                          <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                            tx.category_confidence >= 0.8 ? "bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300" : tx.category_confidence >= 0.5 ? "bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300" : "bg-gray-100 dark:bg-gray-800/60 text-gray-600 dark:text-gray-400"
                          }`}>
                            {tx.suggested_category || "Other"}
                          </span>
                          <FiEdit2 className="w-3 h-3 text-gray-300 dark:text-gray-600 opacity-0 group-hover:opacity-100 transition-opacity" />
                        </button>
                      )}
                    </td>

                    {/* Type */}
                    <td className="px-3 py-2.5">
                      <span className={`text-xs font-semibold ${ttype === "credit" ? "text-emerald-600 dark:text-emerald-400" : ttype === "debit" ? "text-red-600 dark:text-red-400" : ttype === "duplicate" ? "text-orange-600 dark:text-orange-400" : "text-gray-400"}`}>
                        {ttype === "credit" ? "Credit" : ttype === "debit" ? "Debit" : ttype === "duplicate" ? "Dup" : "—"}
                      </span>
                    </td>

                    {/* Amount */}
                    <td className="px-3 py-2.5">
                      {isEditing && editField === "amount" ? (
                        <input autoFocus value={editValue} onChange={(e) => setEditValue(e.target.value)} onBlur={() => saveEdit(tx.row_index, "amount")} onKeyDown={(e) => e.key === "Enter" && saveEdit(tx.row_index, "amount")} className="w-24 px-2 py-1 rounded-lg border border-emerald-300 dark:border-emerald-600 bg-white dark:bg-gray-800 text-xs font-mono text-right focus:outline-none focus:ring-2 focus:ring-emerald-400/30" />
                      ) : (
                        <button onClick={() => startEdit(tx.row_index, "amount", tx.amount)} className={`text-xs font-mono tabular-nums w-full text-right hover:text-emerald-600 dark:hover:text-emerald-400 ${ttype === "debit" ? "text-red-600 dark:text-red-400" : "text-emerald-600 dark:text-emerald-400"}`}>
                          {ttype === "credit" ? "+" : ttype === "debit" ? "−" : ""}
                          {formatAmount(tx.amount)}
                        </button>
                      )}
                    </td>

                    {/* Status */}
                    <td className="px-3 py-2.5">
                      <div className="flex items-center gap-1.5">
                        {getStatusBadge(tx)}
                        {tx.duplicate && dupMatch && (
                          <span className="group relative">
                            <FiInfo className="w-3.5 h-3.5 text-gray-400 hover:text-orange-500 cursor-help" />
                            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-56 px-3 py-2 rounded-xl bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 text-[11px] shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10 pointer-events-none">
                              <p className="font-semibold mb-1">Matched expense #{dupMatch.expense_id}</p>
                              <p>{dupMatch.expense_title}</p>
                              <p className="text-gray-300 dark:text-gray-600 mt-0.5">₹{formatAmount(dupMatch.expense_amount)} on {dupMatch.expense_date}</p>
                              {dupMatch.reasons?.map((r, i) => (
                                <p key={i} className="text-gray-400 dark:text-gray-500 mt-0.5">• {r}</p>
                              ))}
                              <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-gray-900 dark:border-t-gray-100" />
                            </div>
                          </span>
                        )}
                      </div>
                    </td>

                    {/* Duplicate action dropdown */}
                    <td className="px-3 py-2.5">
                      {tx.duplicate ? (
                        <select
                          value={currDupAction}
                          onChange={(e) => handleDupAction(tx.row_index, e.target.value)}
                          className="px-2 py-1 rounded-lg text-[11px] font-medium border border-gray-200/60 dark:border-gray-700/50 bg-white/60 dark:bg-gray-800/60 focus:outline-none focus:ring-2 focus:ring-orange-400/30 cursor-pointer"
                        >
                          {DUPLICATE_ACTIONS.map((a) => (
                            <option key={a.value} value={a.value} title={a.desc}>{a.label}</option>
                          ))}
                        </select>
                      ) : (
                        <span className="text-[11px] text-gray-300 dark:text-gray-600">—</span>
                      )}
                    </td>

                    {/* Actions */}
                    <td className="px-3 py-2.5 text-right">
                      <div className="flex items-center justify-end gap-1">
                        {isEditing ? (
                          <>
                            <button onClick={() => saveEdit(tx.row_index, editField)} className="p-1.5 rounded-lg text-emerald-600 hover:bg-emerald-50 dark:hover:bg-emerald-900/20">
                              <FiCheck className="w-3.5 h-3.5" />
                            </button>
                            <button onClick={cancelEdit} className="p-1.5 rounded-lg text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800">
                              <FiX className="w-3.5 h-3.5" />
                            </button>
                          </>
                        ) : (
                          <button onClick={() => onDelete?.(tx.row_index)} className="p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20">
                            <FiTrash2 className="w-3.5 h-3.5" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
          <span>
            {filtered.length > 0
              ? `${(safePage - 1) * PAGE_SIZE + 1}–${Math.min(safePage * PAGE_SIZE, filtered.length)} of ${filtered.length}`
              : "0 results"}
          </span>
          <div className="flex items-center gap-1">
            <button onClick={() => setPage(1)} disabled={safePage <= 1} className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-30 disabled:cursor-not-allowed"><FiChevronsLeft className="w-4 h-4" /></button>
            <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={safePage <= 1} className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-30 disabled:cursor-not-allowed"><FiChevronLeft className="w-4 h-4" /></button>
            {Array.from({ length: Math.min(7, totalPages) }, (_, i) => {
              let pageNum;
              if (totalPages <= 7) { pageNum = i + 1; }
              else if (safePage <= 4) { pageNum = i + 1; }
              else if (safePage >= totalPages - 3) { pageNum = totalPages - 6 + i; }
              else { pageNum = safePage - 3 + i; }
              return (
                <button key={pageNum} onClick={() => setPage(pageNum)} className={`w-8 h-8 rounded-lg text-xs font-semibold transition-colors ${safePage === pageNum ? "bg-emerald-100 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-300" : "hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 dark:text-gray-400"}`}>
                  {pageNum}
                </button>
              );
            })}
            <button onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={safePage >= totalPages} className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-30 disabled:cursor-not-allowed"><FiChevronRight className="w-4 h-4" /></button>
            <button onClick={() => setPage(totalPages)} disabled={safePage >= totalPages} className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-30 disabled:cursor-not-allowed"><FiChevronsRight className="w-4 h-4" /></button>
          </div>
        </div>
      )}
    </div>
  );
}
