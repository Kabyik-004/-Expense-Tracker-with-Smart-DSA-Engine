import { useState, useEffect, useRef, useMemo } from "react";
import { useExpenses } from "../hooks/useExpenses";
import { useDebounce } from "../hooks/useDebounce";
import { formatCurrency, formatDate } from "../utils/helpers";
import { PAYMENT_METHODS } from "../utils/constants";
import { useToast } from "../components/shared/Toast";
import { SkeletonExpensesTable } from "../components/shared/skeletons";
import EmptyState from "../components/shared/EmptyState";
import CategoryIcon from "../components/shared/CategoryIcon";
import api from "../services/api";
import {
  FiPlus,
  FiSearch,
  FiX,
  FiEdit2,
  FiTrash2,
  FiChevronLeft,
  FiChevronRight,
  FiChevronsLeft,
  FiChevronsRight,
  FiFilter,
  FiRefreshCw,
  FiArrowUp,
  FiArrowDown,
  FiEye,
  FiSliders,
} from "react-icons/fi";

const SORT_OPTIONS = [
  { value: "date", label: "Date" },
  { value: "amount", label: "Amount" },
  { value: "title", label: "Title" },
  { value: "category_id", label: "Category" },
];

const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
const CURRENT_YEAR = new Date().getFullYear();
const YEARS = Array.from({ length: 10 }, (_, i) => CURRENT_YEAR - i);

const initialForm = {
  title: "",
  amount: "",
  description: "",
  category_id: "",
  date: new Date().toISOString().split("T")[0],
  payment_method: "cash",
};

export default function Expenses() {
  const { addToast } = useToast();
  const {
    allExpenses,
    fetchExpenses,
    addExpense,
    editExpense,
    removeExpense,
    undoLastExpense,
    handleSort,
    loading,
    page,
    setPage,
    sortField,
    sortAscending,
    undoStackSize,
    fetchUndoStatus,
  } = useExpenses();

  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(initialForm);
  const [formErrors, setFormErrors] = useState({});
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [undoTarget, setUndoTarget] = useState(null);
  const [detailTarget, setDetailTarget] = useState(null);
  const [searchInput, setSearchInput] = useState("");
  const [showFilters, setShowFilters] = useState(false);
  const [categories, setCategories] = useState([]);

  const [filters, setFilters] = useState({
    category: "",
    dateFrom: "",
    dateTo: "",
    amountMin: "",
    amountMax: "",
    month: "",
    year: "",
  });

  const searchRef = useRef(null);

  const debouncedSearch = useDebounce(searchInput, 400);

  useEffect(() => {
    fetchExpenses();
    fetchUndoStatus();
    api.get("/categories/").then((res) => {
      if (res.data.success) setCategories(res.data.data.categories || []);
    }).catch(() => {});
  }, [fetchExpenses, fetchUndoStatus]);

  const activeFilterCount = Object.values(filters).filter(Boolean).length;

  const filtered = useMemo(() => {
    let result = [...allExpenses];
    if (debouncedSearch) {
      const q = debouncedSearch.toLowerCase();
      result = result.filter((e) =>
        e.title?.toLowerCase().includes(q) ||
        e.description?.toLowerCase().includes(q)
      );
    }
    if (filters.category) {
      result = result.filter((e) => String(e.category_id) === filters.category);
    }
    if (filters.dateFrom) {
      result = result.filter((e) => e.date && e.date >= filters.dateFrom);
    }
    if (filters.dateTo) {
      result = result.filter((e) => e.date && e.date <= filters.dateTo);
    }
    if (filters.amountMin) {
      result = result.filter((e) => parseFloat(e.amount) >= parseFloat(filters.amountMin));
    }
    if (filters.amountMax) {
      result = result.filter((e) => parseFloat(e.amount) <= parseFloat(filters.amountMax));
    }
    if (filters.month) {
      result = result.filter((e) => {
        if (!e.date) return false;
        const m = String(parseInt(e.date.split("-")[1]) - 1).padStart(2, "0");
        return m === filters.month;
      });
    }
    if (filters.year) {
      result = result.filter((e) => e.date && e.date.startsWith(filters.year));
    }
    if (sortField) {
      result.sort((a, b) => {
        let va = a[sortField], vb = b[sortField];
        if (sortField === "amount") { va = parseFloat(va) || 0; vb = parseFloat(vb) || 0; }
        else if (sortField === "date") { va = va || ""; vb = vb || ""; }
        else { va = (va || "").toString().toLowerCase(); vb = (vb || "").toString().toLowerCase(); }
        return va < vb ? (sortAscending ? -1 : 1) : va > vb ? (sortAscending ? 1 : -1) : 0;
      });
    }
    return result;
  }, [allExpenses, debouncedSearch, filters, sortField, sortAscending]);

  const totalFilteredPages = Math.ceil(filtered.length / 10) || 1;
  const paginatedFiltered = filtered.slice((page - 1) * 10, page * 10);
  const hasActiveFilters = !!debouncedSearch || activeFilterCount > 0;

  const clearFilters = () => {
    setSearchInput("");
    setFilters({ category: "", dateFrom: "", dateTo: "", amountMin: "", amountMax: "", month: "", year: "" });
    setPage(1);
  };

  const resetForm = () => {
    setForm(initialForm);
    setEditing(null);
    setShowForm(false);
    setFormErrors({});
  };

  useEffect(() => {
    if (!showForm && searchInput) searchRef.current?.focus();
  }, [showForm, searchInput]);

  const validateForm = () => {
    const errors = {};
    if (!form.title.trim()) errors.title = "Title is required";
    if (!form.amount || parseFloat(form.amount) <= 0) errors.amount = "Amount must be positive";
    if (!form.date) errors.date = "Date is required";
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;
    const payload = { ...form, amount: parseFloat(form.amount) };
    const res = editing ? await editExpense(editing, payload) : await addExpense(payload);
    if (res.success) resetForm();
  };

  const handleEdit = (exp) => {
    setForm({
      title: exp.title,
      amount: exp.amount.toString(),
      description: exp.description || "",
      category_id: exp.category_id || "",
      date: exp.date?.split("T")[0] || "",
      payment_method: exp.payment_method || "cash",
    });
    setEditing(exp.id);
    setShowForm(true);
    setFormErrors({});
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    const res = await removeExpense(deleteTarget.id);
    if (res?.success) {
      addToast("Expense deleted", "success", {
        onUndo: async () => {
          const undoRes = await undoLastExpense();
          if (undoRes?.success) {
            addToast("Expense restored", "success");
          } else {
            addToast("Failed to undo", "error");
          }
          fetchUndoStatus();
        },
        duration: 6000,
      });
    }
    setDeleteTarget(null);
  };

  const handleUndoConfirm = async () => {
    const res = await undoLastExpense();
    if (res?.success) {
      addToast("Last action undone", "success");
    } else {
      addToast("Nothing to undo", "info");
    }
    setUndoTarget(null);
    fetchUndoStatus();
  };

  const toggleSort = (field) => {
    handleSort(field);
  };

  const getSortIcon = (field) => {
    if (sortField !== field) return null;
    return sortAscending ? <FiArrowUp className="w-3 h-3 inline ml-1" /> : <FiArrowDown className="w-3 h-3 inline ml-1" />;
  };

  const updateFilter = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
    setPage(1);
  };

  const DetailModal = ({ expense, onClose }) => {
    if (!expense) return null;
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 dark:bg-black/70 backdrop-blur-sm" onClick={onClose}>
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-lg p-6 space-y-5 animate-fade-in" onClick={(e) => e.stopPropagation()}>
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">{expense.title}</h2>
            <button onClick={onClose} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"><FiX className="w-5 h-5 text-gray-500 dark:text-gray-400" /></button>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-indigo-50 dark:bg-indigo-900/30 rounded-xl">
              <p className="text-xs text-indigo-500 dark:text-indigo-400 font-medium">Amount</p>
              <p className="text-2xl font-bold text-red-600 dark:text-red-400 mt-1">{formatCurrency(expense.amount)}</p>
            </div>
            <div className="p-4 bg-green-50 dark:bg-green-900/30 rounded-xl">
              <p className="text-xs text-green-500 dark:text-green-400 font-medium">Date</p>
              <p className="text-lg font-semibold text-gray-900 dark:text-white mt-1">{formatDate(expense.date)}</p>
            </div>
            <div className="p-4 bg-purple-50 dark:bg-purple-900/30 rounded-xl">
              <p className="text-xs text-purple-500 dark:text-purple-400 font-medium">Category</p>
              <div className="flex items-center gap-2 mt-1">
                <CategoryIcon name={expense.category_name} size="sm" />
                <p className="text-lg font-semibold text-gray-900 dark:text-white">{expense.category_name || `#${expense.category_id}`}</p>
              </div>
            </div>
            <div className="p-4 bg-orange-50 dark:bg-orange-900/30 rounded-xl">
              <p className="text-xs text-orange-500 dark:text-orange-400 font-medium">Payment</p>
              <p className="text-lg font-semibold text-gray-900 dark:text-white mt-1 capitalize">{expense.payment_method || "Cash"}</p>
            </div>
          </div>
          {expense.description && (
            <div><p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Description</p><p className="text-gray-900 dark:text-white">{expense.description}</p></div>
          )}
          <div className="flex justify-end gap-2 pt-2">
            <button onClick={() => { onClose(); handleEdit(expense); }} className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium flex items-center gap-2">
              <FiEdit2 className="w-4 h-4" /> Edit
            </button>
          </div>
        </div>
      </div>
    );
  };

  const DeleteModal = ({ target, onConfirm, onCancel }) => {
    if (!target) return null;
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 dark:bg-black/70 backdrop-blur-sm" onClick={onCancel}>
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-sm p-6 animate-fade-in" onClick={(e) => e.stopPropagation()}>
          <div className="text-center">
            <div className="w-14 h-14 bg-red-100 dark:bg-red-900/50 rounded-full flex items-center justify-center mx-auto mb-4"><FiTrash2 className="w-6 h-6 text-red-600 dark:text-red-400" /></div>
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">Delete Expense</h3>
            <p className="text-gray-500 dark:text-gray-400 text-sm mb-2">Are you sure you want to delete this expense?</p>
            <p className="font-medium text-gray-900 dark:text-white">"{target.title}"</p>
            <p className="text-red-600 dark:text-red-400 font-semibold mt-1">-{formatCurrency(target.amount)}</p>
          </div>
          <div className="flex gap-3 mt-6">
            <button onClick={onCancel} className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 font-medium">Cancel</button>
            <button onClick={onConfirm} className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium">Delete</button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Expenses</h1>
          <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">
            {hasActiveFilters ? `${filtered.length} results` : `${allExpenses.length} total expenses`}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {undoStackSize > 0 && (
            <button onClick={() => setUndoTarget(true)} className="px-3 py-2 text-sm bg-orange-50 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 rounded-lg hover:bg-orange-100 dark:hover:bg-orange-900/50 font-medium flex items-center gap-1.5" title={`${undoStackSize} undo available`}>
              <FiRefreshCw className="w-4 h-4" /> Undo ({undoStackSize})
            </button>
          )}
          <button onClick={() => { resetForm(); setShowForm(!showForm); }} className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors ${showForm ? "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600" : "bg-indigo-600 text-white hover:bg-indigo-700"}`}>
            {showForm ? <FiX className="w-4 h-4" /> : <FiPlus className="w-4 h-4" />}
            {showForm ? "Cancel" : "Add Expense"}
          </button>
        </div>
      </div>

      {showForm && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-5 sm:p-6 space-y-4 animate-fade-in">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{editing ? "Edit Expense" : "Add New Expense"}</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Title *</label>
                <input type="text" required className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 ${formErrors.title ? "border-red-400 dark:border-red-500 bg-red-50 dark:bg-red-900/30" : "border-gray-300 dark:border-gray-600"}`} value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="Groceries" />
                {formErrors.title && <p className="text-xs text-red-500 dark:text-red-400 mt-1">{formErrors.title}</p>}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Amount *</label>
                <input type="number" step="0.01" min="0.01" required className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 ${formErrors.amount ? "border-red-400 dark:border-red-500 bg-red-50 dark:bg-red-900/30" : "border-gray-300 dark:border-gray-600"}`} value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} placeholder="500.00" />
                {formErrors.amount && <p className="text-xs text-red-500 dark:text-red-400 mt-1">{formErrors.amount}</p>}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Date *</label>
                <input type="date" required className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 ${formErrors.date ? "border-red-400 dark:border-red-500 bg-red-50 dark:bg-red-900/30" : "border-gray-300 dark:border-gray-600"}`} value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Category</label>
                <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400" value={form.category_id} onChange={(e) => setForm({ ...form, category_id: e.target.value })}>
                  <option value="">Select category</option>
                  {categories.map((cat) => <option key={cat.id} value={cat.id}>{cat.name}</option>)}
                  <option value="other">Other</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Payment Method</label>
                <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400" value={form.payment_method} onChange={(e) => setForm({ ...form, payment_method: e.target.value })}>
                  {PAYMENT_METHODS.map((m) => (
                    <option key={m} value={m}>{m.replace("_", " ").replace(/\b\w/g, l => l.toUpperCase())}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Description</label>
                <input type="text" className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Optional notes" />
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-2">
              {editing && <button type="button" onClick={resetForm} className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 text-sm font-medium">Cancel</button>}
              <button type="submit" className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium flex items-center gap-2">
                {editing ? <FiEdit2 className="w-4 h-4" /> : <FiPlus className="w-4 h-4" />}
                {editing ? "Update Expense" : "Create Expense"}
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
        <div className="p-4 border-b border-gray-100 dark:border-gray-700 space-y-3">
          <div className="flex flex-col sm:flex-row gap-2">
            <div className="relative flex-1">
              <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-gray-500" />
              <input
                ref={searchRef}
                type="text"
                className="w-full pl-10 pr-10 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 text-sm"
                placeholder="Live search expenses..."
                value={searchInput}
                onChange={(e) => { setSearchInput(e.target.value); setPage(1); }}
              />
              {searchInput && (
                <button type="button" onClick={() => { setSearchInput(""); setPage(1); }} className="absolute right-3 top-1/2 -translate-y-1/2">
                  <FiX className="w-4 h-4 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300" />
                </button>
              )}
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`px-3 py-2 rounded-lg text-sm border font-medium flex items-center gap-1.5 transition-colors ${showFilters || activeFilterCount > 0 ? "bg-indigo-50 dark:bg-indigo-900/30 border-indigo-200 dark:border-indigo-700 text-indigo-700 dark:text-indigo-300" : "border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700/50"}`}
              >
                <FiSliders className="w-4 h-4" /> Filters{activeFilterCount > 0 && ` (${activeFilterCount})`}
              </button>
              {hasActiveFilters && (
                <button onClick={clearFilters} className="px-3 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg border border-gray-300 dark:border-gray-600 font-medium">
                  Clear
                </button>
              )}
            </div>
          </div>

          {showFilters && (
            <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-xl space-y-4 animate-fade-in">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-600 dark:text-gray-300 mb-1">Category</label>
                  <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400" value={filters.category} onChange={(e) => updateFilter("category", e.target.value)}>
                    <option value="">All Categories</option>
                    {categories.map((cat) => <option key={cat.id} value={cat.id}>{cat.name}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 dark:text-gray-300 mb-1">Date From</label>
                  <input type="date" className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400" value={filters.dateFrom} onChange={(e) => updateFilter("dateFrom", e.target.value)} />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 dark:text-gray-300 mb-1">Date To</label>
                  <input type="date" className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400" value={filters.dateTo} onChange={(e) => updateFilter("dateTo", e.target.value)} />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 dark:text-gray-300 mb-1">Min Amount</label>
                  <input type="number" min="0" step="0.01" className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400" value={filters.amountMin} onChange={(e) => updateFilter("amountMin", e.target.value)} placeholder="₹0" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 dark:text-gray-300 mb-1">Max Amount</label>
                  <input type="number" min="0" step="0.01" className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400" value={filters.amountMax} onChange={(e) => updateFilter("amountMax", e.target.value)} placeholder="₹99999" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 dark:text-gray-300 mb-1">Month</label>
                  <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400" value={filters.month} onChange={(e) => updateFilter("month", e.target.value)}>
                    <option value="">All Months</option>
                    {MONTHS.map((m, i) => <option key={i} value={String(i).padStart(2, "0")}>{m}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 dark:text-gray-300 mb-1">Year</label>
                  <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400" value={filters.year} onChange={(e) => updateFilter("year", e.target.value)}>
                    <option value="">All Years</option>
                    {YEARS.map((y) => <option key={y} value={y}>{y}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 dark:text-gray-300 mb-1">Sort By</label>
                  <div className="flex gap-1">
                    {SORT_OPTIONS.slice(0, 3).map((opt) => (
                      <button
                        key={opt.value}
                        onClick={() => toggleSort(opt.value)}
                        className={`flex-1 px-2 py-2 rounded-lg text-xs font-medium transition-colors flex items-center justify-center gap-0.5 ${sortField === opt.value ? "bg-indigo-100 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300" : "bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700/50"}`}
                      >
                        {opt.label}
                        {getSortIcon(opt.value)}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="flex items-center gap-2 overflow-x-auto pb-1">
            <span className="text-sm text-gray-500 dark:text-gray-400 font-medium mr-1 shrink-0">Sort:</span>
            {SORT_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                onClick={() => toggleSort(opt.value)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium whitespace-nowrap transition-colors flex items-center gap-1 ${sortField === opt.value ? "bg-indigo-100 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300" : "bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"}`}
              >
                {opt.label}
                {getSortIcon(opt.value)}
              </button>
            ))}
          </div>

          {hasActiveFilters && (
            <div className="flex items-center gap-2 text-sm text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/30 px-3 py-2 rounded-lg flex-wrap">
              <FiFilter className="w-4 h-4 shrink-0" />
              <span>Filtered to <strong>{filtered.length}</strong> of {allExpenses.length} expenses</span>
              {debouncedSearch && <span className="text-indigo-400">· search: "{debouncedSearch}"</span>}
              {filters.category && <span className="text-indigo-400">· category: {categories.find(c => String(c.id) === filters.category)?.name || filters.category}</span>}
              {filters.month && <span className="text-indigo-400">· month: {MONTHS[parseInt(filters.month)]}</span>}
              {filters.year && <span className="text-indigo-400">· year: {filters.year}</span>}
              {(filters.amountMin || filters.amountMax) && <span className="text-indigo-400">· amount: {filters.amountMin || "0"} - {filters.amountMax || "∞"}</span>}
            </div>
          )}
        </div>

        {loading ? (
          <div className="animate-pulse">
            <div className="hidden md:block overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-100 dark:border-gray-700 bg-gray-50/80 dark:bg-gray-900/80">
                    {["Title", "Amount", "Date", "Category", "Payment", "Actions"].map((h) => (
                      <th key={h} className="px-4 py-3">
                        <div className="h-3 bg-gray-200 dark:bg-gray-600 rounded w-16" />
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {[1, 2, 3, 4, 5].map((i) => (
                    <tr key={i} className="border-b border-gray-50 dark:border-gray-700">
                      {[1, 2, 3, 4, 5, 6].map((j) => (
                        <td key={j} className="px-4 py-3.5">
                          <div className={`h-4 bg-gray-200 dark:bg-gray-700 rounded ${j === 0 ? "w-3/4" : j === 5 ? "w-1/4" : "w-1/2"}`} />
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="md:hidden divide-y divide-gray-100 dark:divide-gray-700">
              {[1, 2, 3].map((i) => (
                <div key={i} className="p-4 space-y-2">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded-full shrink-0" />
                    <div className="flex-1 space-y-1">
                      <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2" />
                      <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/3" />
                    </div>
                    <div className="h-5 bg-gray-200 dark:bg-gray-700 rounded w-16" />
                  </div>
                  <div className="flex gap-2 pt-2 border-t border-gray-50 dark:border-gray-700">
                    {[1, 2, 3].map((k) => (
                      <div key={k} className="flex-1 h-8 bg-gray-200 dark:bg-gray-700 rounded-lg" />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : filtered.length === 0 ? (
          <EmptyState
            icon={<FiSearch className="w-7 h-7" />}
            title={hasActiveFilters ? "No matching expenses" : "No expenses yet"}
            description={hasActiveFilters ? "Try adjusting your filters to find what you're looking for." : "Add your first expense to get started with tracking."}
            action={hasActiveFilters ? undefined : { label: "Add Expense", onClick: () => { resetForm(); setShowForm(true); } }}
            secondaryAction={hasActiveFilters ? { label: "Clear Filters", onClick: clearFilters } : undefined}
            color="indigo"
          />
        ) : (
          <>
            <div className="hidden md:block overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-100 dark:border-gray-700 bg-gray-50/80 dark:bg-gray-800/80">
                    {["Title", "Amount", "Date", "Category", "Payment", "Actions"].map((h, i) => (
                      <th key={h} className={`px-4 py-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider ${i < 4 ? "cursor-pointer select-none hover:text-gray-700 dark:hover:text-gray-200" : ""} ${i === 5 ? "text-right" : "text-left"}`} onClick={() => i < 4 && toggleSort(SORT_OPTIONS[i].value)}>
                        {h}{i < 4 && getSortIcon(SORT_OPTIONS[i].value)}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {paginatedFiltered.map((exp) => (
                    <tr key={exp.id} className="border-b border-gray-50 dark:border-gray-700 hover:bg-gray-50/70 dark:hover:bg-gray-700/70 transition-colors group">
                      <td className="px-4 py-3.5">
                        <div className="flex items-center gap-3">
                          <CategoryIcon name={exp.category_name} size="sm" />
                          <div>
                            <p className="text-sm font-medium text-gray-900 dark:text-white">{exp.title}</p>
                            {exp.description && <p className="text-xs text-gray-400 dark:text-gray-500 truncate max-w-[200px]">{exp.description}</p>}
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3.5"><span className="text-sm font-semibold text-red-600 dark:text-red-400">{formatCurrency(exp.amount)}</span></td>
                      <td className="px-4 py-3.5 text-sm text-gray-500 dark:text-gray-400">{formatDate(exp.date)}</td>
                      <td className="px-4 py-3.5">
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300">
                          <CategoryIcon name={exp.category_name} size="sm" className="!w-5 !h-5" />
                          {exp.category_name || `#${exp.category_id}`}
                        </span>
                      </td>
                      <td className="px-4 py-3.5"><span className="text-sm text-gray-500 dark:text-gray-400 capitalize">{exp.payment_method || "Cash"}</span></td>
                      <td className="px-4 py-3.5 text-right">
                        <div className="flex items-center justify-end gap-1 opacity-60 group-hover:opacity-100 transition-opacity">
                          <button onClick={() => setDetailTarget(exp)} className="p-2 text-gray-400 dark:text-gray-500 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/30 rounded-lg" title="View"><FiEye className="w-4 h-4" /></button>
                          <button onClick={() => handleEdit(exp)} className="p-2 text-gray-400 dark:text-gray-500 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-lg" title="Edit"><FiEdit2 className="w-4 h-4" /></button>
                          <button onClick={() => setDeleteTarget(exp)} className="p-2 text-gray-400 dark:text-gray-500 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg" title="Delete"><FiTrash2 className="w-4 h-4" /></button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="md:hidden divide-y divide-gray-100 dark:divide-gray-700">
              {paginatedFiltered.map((exp) => (
                <div key={exp.id} className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                      <CategoryIcon name={exp.category_name} size="md" />
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">{exp.title}</p>
                        {exp.description && <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">{exp.description}</p>}
                        <div className="flex items-center gap-2 mt-1.5">
                          <span className="inline-flex items-center gap-1 text-xs bg-indigo-100 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300 px-2 py-0.5 rounded-full">
                            <CategoryIcon name={exp.category_name} size="sm" className="!w-4 !h-4" />
                            {exp.category_name || `#${exp.category_id}`}
                          </span>
                          <span className="text-xs text-gray-400 dark:text-gray-500 capitalize">{exp.payment_method || "Cash"}</span>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-red-600 dark:text-red-400">{formatCurrency(exp.amount)}</p>
                      <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">{formatDate(exp.date)}</p>
                    </div>
                  </div>
                  <div className="flex gap-2 mt-3 pt-3 border-t border-gray-50 dark:border-gray-700">
                    <button onClick={() => setDetailTarget(exp)} className="flex-1 text-xs py-1.5 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 font-medium flex items-center justify-center gap-1"><FiEye className="w-3.5 h-3.5" /> View</button>
                    <button onClick={() => handleEdit(exp)} className="flex-1 text-xs py-1.5 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 rounded-lg hover:bg-indigo-100 dark:hover:bg-indigo-900/50 font-medium flex items-center justify-center gap-1"><FiEdit2 className="w-3.5 h-3.5" /> Edit</button>
                    <button onClick={() => setDeleteTarget(exp)} className="flex-1 text-xs py-1.5 bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/50 font-medium flex items-center justify-center gap-1"><FiTrash2 className="w-3.5 h-3.5" /> Delete</button>
                  </div>
                </div>
              ))}
            </div>

            {totalFilteredPages > 1 && (
              <div className="px-4 py-4 border-t border-gray-100 dark:border-gray-700 flex flex-col sm:flex-row items-center justify-between gap-3">
                <p className="text-sm text-gray-500 dark:text-gray-400">Page {page} of {totalFilteredPages} ({filtered.length} results)</p>
                <div className="flex items-center gap-1.5">
                  <button onClick={() => setPage(1)} disabled={page === 1} className="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-30 disabled:cursor-not-allowed"><FiChevronsLeft className="w-4 h-4" /></button>
                  <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page === 1} className="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-30 disabled:cursor-not-allowed"><FiChevronLeft className="w-4 h-4" /></button>
                  {(() => {
                    const pages = [];
                    const start = Math.max(1, page - 2);
                    const end = Math.min(totalFilteredPages, page + 2);
                    for (let i = start; i <= end; i++) {
                      pages.push(
                        <button key={i} onClick={() => setPage(i)} className={`min-w-[36px] h-9 rounded-lg text-sm font-medium transition-colors ${i === page ? "bg-indigo-600 text-white" : "text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"}`}>{i}</button>
                      );
                    }
                    return pages;
                  })()}
                  <button onClick={() => setPage(Math.min(totalFilteredPages, page + 1))} disabled={page === totalFilteredPages} className="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-30 disabled:cursor-not-allowed"><FiChevronRight className="w-4 h-4" /></button>
                  <button onClick={() => setPage(totalFilteredPages)} disabled={page === totalFilteredPages} className="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-30 disabled:cursor-not-allowed"><FiChevronsRight className="w-4 h-4" /></button>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      <DetailModal expense={detailTarget} onClose={() => setDetailTarget(null)} />
      <DeleteModal target={deleteTarget} onConfirm={handleDelete} onCancel={() => setDeleteTarget(null)} />

      {undoTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 dark:bg-black/70 backdrop-blur-sm" onClick={() => setUndoTarget(null)}>
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-sm p-6 animate-fade-in" onClick={(e) => e.stopPropagation()}>
            <div className="text-center">
              <div className="w-14 h-14 bg-orange-100 dark:bg-orange-900/50 rounded-full flex items-center justify-center mx-auto mb-4"><FiRefreshCw className="w-6 h-6 text-orange-600 dark:text-orange-400" /></div>
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">Undo Last Action</h3>
              <p className="text-gray-500 dark:text-gray-400 text-sm">This will reverse your last expense operation ({undoStackSize} undo{undoStackSize > 1 ? "s" : ""} available).</p>
            </div>
            <div className="flex gap-3 mt-6">
              <button onClick={() => setUndoTarget(null)} className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 font-medium">Cancel</button>
              <button onClick={handleUndoConfirm} className="flex-1 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 font-medium flex items-center justify-center gap-2"><FiRefreshCw className="w-4 h-4" /> Undo</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}