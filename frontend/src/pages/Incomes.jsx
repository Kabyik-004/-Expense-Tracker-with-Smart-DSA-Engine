import { useState, useEffect } from "react";
import { formatCurrency, formatDate } from "../utils/helpers";
import * as incomeService from "../services/incomeService";
import { useToast } from "../components/shared/Toast";
import {
  FiPlus,
  FiX,
  FiEdit2,
  FiTrash2,
  FiRefreshCw,
  FiTrendingUp,
  FiRepeat,
  FiFileText,
  FiChevronLeft,
  FiChevronRight,
  FiChevronsLeft,
  FiChevronsRight,
} from "react-icons/fi";

const ITEMS_PER_PAGE = 10;

const initialForm = {
  source: "",
  amount: "",
  description: "",
  date: new Date().toISOString().split("T")[0],
  is_recurring: false,
  notes: "",
};

export default function Incomes() {
  const { addToast } = useToast();
  const [incomes, setIncomes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(initialForm);
  const [formErrors, setFormErrors] = useState({});
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [undoTarget, setUndoTarget] = useState(null);
  const [page, setPage] = useState(1);
  const [detailTarget, setDetailTarget] = useState(null);

  const fetchIncomes = async () => {
    setLoading(true);
    try {
      const res = await incomeService.getIncomes();
      if (res.success) {
        const sorted = (res.data.incomes || []).sort(
          (a, b) => new Date(b.date || 0) - new Date(a.date || 0)
        );
        setIncomes(sorted);
      }
    } catch {} finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchIncomes(); }, []);

  const totalPages = Math.ceil(incomes.length / ITEMS_PER_PAGE) || 1;
  const paginatedIncomes = incomes.slice(
    (page - 1) * ITEMS_PER_PAGE,
    page * ITEMS_PER_PAGE
  );

  const resetForm = () => {
    setForm(initialForm);
    setEditing(null);
    setShowForm(false);
    setFormErrors({});
  };

  const validateForm = () => {
    const errors = {};
    if (!form.source.trim()) errors.source = "Source is required";
    if (!form.amount || parseFloat(form.amount) <= 0) errors.amount = "Amount must be positive";
    if (!form.date) errors.date = "Date is required";
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;
    const payload = {
      source: form.source,
      amount: parseFloat(form.amount),
      description: form.description || undefined,
      date: form.date || undefined,
      is_recurring: form.is_recurring,
      notes: form.notes || undefined,
    };
    const res = editing
      ? await incomeService.updateIncome(editing, payload)
      : await incomeService.createIncome(payload);
    if (res.success) {
      await fetchIncomes();
      resetForm();
    }
  };

  const handleEdit = (income) => {
    setForm({
      source: income.source,
      amount: income.amount.toString(),
      description: income.description || "",
      date: income.date?.split("T")[0] || "",
      is_recurring: income.is_recurring || false,
      notes: income.notes || "",
    });
    setEditing(income.id);
    setShowForm(true);
    setFormErrors({});
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    const res = await incomeService.deleteIncome(deleteTarget.id);
    if (res.success) {
      await fetchIncomes();
      addToast(res.message || "Income deleted", "success");
      setDeleteTarget(null);
    }
  };

  const handleUndoConfirm = async () => {
    const res = await incomeService.undoIncome();
    if (res.success) {
      await fetchIncomes();
      addToast(res.message || "Last income action undone", "undo");
    } else {
      addToast(res?.message || "Nothing to undo", "info");
    }
    setUndoTarget(null);
  };

  const DetailModal = ({ income, onClose }) => {
    if (!income) return null;
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 dark:bg-black/70 backdrop-blur-sm" onClick={onClose}>
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-lg p-6 space-y-5 animate-fade-in" onClick={(e) => e.stopPropagation()}>
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">{income.source}</h2>
            <button onClick={onClose} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
              <FiX className="w-5 h-5 text-gray-500 dark:text-gray-400" />
            </button>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-green-50 dark:bg-green-900/30 rounded-xl">
              <p className="text-xs text-green-500 dark:text-green-400 font-medium">Amount</p>
              <p className="text-2xl font-bold text-green-600 dark:text-green-400 mt-1">{formatCurrency(income.amount)}</p>
            </div>
            <div className="p-4 bg-indigo-50 dark:bg-indigo-900/30 rounded-xl">
              <p className="text-xs text-indigo-500 dark:text-indigo-400 font-medium">Date</p>
              <p className="text-lg font-semibold text-gray-900 dark:text-white mt-1">{formatDate(income.date)}</p>
            </div>
            <div className="p-4 bg-purple-50 dark:bg-purple-900/30 rounded-xl">
              <p className="text-xs text-purple-500 dark:text-purple-400 font-medium">Recurring</p>
              <p className="text-lg font-semibold text-gray-900 dark:text-white mt-1">{income.is_recurring ? "Yes" : "No"}</p>
            </div>
            <div className="p-4 bg-orange-50 dark:bg-orange-900/30 rounded-xl">
              <p className="text-xs text-orange-500 dark:text-orange-400 font-medium">Source</p>
              <p className="text-lg font-semibold text-gray-900 dark:text-white mt-1 capitalize">{income.source}</p>
            </div>
          </div>
          {income.description && (
            <div>
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Description</p>
              <p className="text-gray-900 dark:text-white">{income.description}</p>
            </div>
          )}
          {income.notes && (
            <div>
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Notes</p>
              <p className="text-gray-900 dark:text-white">{income.notes}</p>
            </div>
          )}
          <div className="flex justify-end gap-2 pt-2">
            <button onClick={() => { onClose(); handleEdit(income); }} className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium flex items-center gap-2">
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
            <div className="w-14 h-14 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
              <FiTrash2 className="w-6 h-6 text-red-600 dark:text-red-400" />
            </div>
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">Delete Income</h3>
            <p className="text-gray-500 dark:text-gray-400 text-sm mb-2">Are you sure you want to delete this income?</p>
            <p className="font-medium text-gray-900 dark:text-white">"{target.source}"</p>
            <p className="text-green-600 dark:text-green-400 font-semibold mt-1">+{formatCurrency(target.amount)}</p>
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
    <div className="space-y-5 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Incomes</h1>
          <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">{incomes.length} total income records</p>
        </div>
        <div className="flex items-center gap-2">
          <button
              onClick={() => setUndoTarget(true)}
            className="px-3 py-2 text-sm bg-orange-50 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 rounded-lg hover:bg-orange-100 dark:hover:bg-orange-900/30 font-medium flex items-center gap-1.5"
          >
            <FiRefreshCw className="w-4 h-4" /> Undo
          </button>
          <button
            onClick={() => { resetForm(); setShowForm(!showForm); }}
            className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors ${
              showForm ? "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-700" : "bg-green-600 text-white hover:bg-green-700"
            }`}
          >
            {showForm ? <FiX className="w-4 h-4" /> : <FiPlus className="w-4 h-4" />}
            {showForm ? "Cancel" : "Add Income"}
          </button>
        </div>
      </div>

      {showForm && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-5 sm:p-6 space-y-4 animate-fade-in">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {editing ? "Edit Income" : "Add New Income"}
          </h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Source *</label>
                <input
                  type="text"
                  required
                  className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 ${formErrors.source ? "border-red-400 bg-red-50 dark:bg-red-900/30" : "border-gray-300 dark:border-gray-600"}`}
                  value={form.source}
                  onChange={(e) => setForm({ ...form, source: e.target.value })}
                  placeholder="Salary, Freelance, etc."
                />
                {formErrors.source && <p className="text-xs text-red-500 dark:text-red-400 mt-1">{formErrors.source}</p>}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Amount *</label>
                <input
                  type="number"
                  step="0.01"
                  min="0.01"
                  required
                  className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 ${formErrors.amount ? "border-red-400 bg-red-50 dark:bg-red-900/30" : "border-gray-300 dark:border-gray-600"}`}
                  value={form.amount}
                  onChange={(e) => setForm({ ...form, amount: e.target.value })}
                  placeholder="5000.00"
                />
                {formErrors.amount && <p className="text-xs text-red-500 dark:text-red-400 mt-1">{formErrors.amount}</p>}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Date</label>
                <input
                  type="date"
                  className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 ${formErrors.date ? "border-red-400 bg-red-50 dark:bg-red-900/30" : "border-gray-300 dark:border-gray-600"}`}
                  value={form.date}
                  onChange={(e) => setForm({ ...form, date: e.target.value })}
                />
              </div>
              <div>
                <label className="flex items-center gap-2 pt-6 cursor-pointer">
                  <input
                    type="checkbox"
                    className="w-4 h-4 text-green-600 dark:text-green-400 border-gray-300 dark:border-gray-600 rounded focus:ring-green-500"
                    checked={form.is_recurring}
                    onChange={(e) => setForm({ ...form, is_recurring: e.target.checked })}
                  />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-200">Recurring Income</span>
                </label>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Description</label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  placeholder="Monthly salary"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Notes</label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  value={form.notes}
                  onChange={(e) => setForm({ ...form, notes: e.target.value })}
                  placeholder="Optional notes"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-2">
              {editing && (
                <button type="button" onClick={resetForm} className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 text-sm font-medium">
                  Cancel
                </button>
              )}
              <button type="submit" className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm font-medium flex items-center gap-2">
                {editing ? <FiEdit2 className="w-4 h-4" /> : <FiPlus className="w-4 h-4" />}
                {editing ? "Update Income" : "Create Income"}
              </button>
            </div>
          </form>
        </div>
      )}

      {loading ? (
        <div className="flex flex-col items-center py-16">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-green-600 mb-4" />
          <p className="text-gray-400 dark:text-gray-500 text-sm">Loading incomes...</p>
        </div>
      ) : incomes.length === 0 ? (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 py-16 text-center">
          <FiTrendingUp className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
          <p className="text-gray-500 dark:text-gray-400 text-lg mb-1">No incomes yet</p>
          <p className="text-gray-400 dark:text-gray-500 text-sm mb-4">Add your first income record</p>
          <button onClick={() => { resetForm(); setShowForm(true); }} className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium inline-flex items-center gap-2">
            <FiPlus className="w-4 h-4" /> Add Income
          </button>
        </div>
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
          <div className="hidden md:block overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-100 dark:border-gray-700 bg-gray-50/80 dark:bg-gray-900/80">
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Source</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Amount</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Date</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Description</th>
                  <th className="text-center px-4 py-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Recurring</th>
                  <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody>
                {paginatedIncomes.map((inc) => (
                  <tr key={inc.id} className="border-b border-gray-50 dark:border-gray-700 hover:bg-gray-50/70 dark:hover:bg-gray-700/50 transition-colors group">
                    <td className="px-4 py-3.5">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center text-green-600 dark:text-green-400 text-xs font-bold shrink-0">
                          {inc.source?.charAt(0)?.toUpperCase() || "I"}
                        </div>
                        <p className="text-sm font-medium text-gray-900 dark:text-white">{inc.source}</p>
                      </div>
                    </td>
                    <td className="px-4 py-3.5">
                      <span className="text-sm font-semibold text-green-600 dark:text-green-400">+{formatCurrency(inc.amount)}</span>
                    </td>
                    <td className="px-4 py-3.5 text-sm text-gray-500 dark:text-gray-400">{formatDate(inc.date)}</td>
                    <td className="px-4 py-3.5 text-sm text-gray-500 dark:text-gray-400 max-w-[200px] truncate">{inc.description || "—"}</td>
                    <td className="px-4 py-3.5 text-center">
                      {inc.is_recurring ? (
                        <span className="inline-flex items-center gap-1 text-xs font-medium text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-900/30 px-2 py-0.5 rounded-full">
                          <FiRepeat className="w-3 h-3" /> Recurring
                        </span>
                      ) : (
                        <span className="text-xs text-gray-400 dark:text-gray-500">Once</span>
                      )}
                    </td>
                    <td className="px-4 py-3.5 text-right">
                      <div className="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button onClick={() => setDetailTarget(inc)} className="p-2 text-gray-400 dark:text-gray-500 hover:text-green-600 dark:hover:text-green-400 hover:bg-green-50 dark:hover:bg-green-900/30 rounded-lg transition-colors" title="View details">
                          <FiFileText className="w-4 h-4" />
                        </button>
                        <button onClick={() => handleEdit(inc)} className="p-2 text-gray-400 dark:text-gray-500 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-lg transition-colors" title="Edit">
                          <FiEdit2 className="w-4 h-4" />
                        </button>
                        <button onClick={() => setDeleteTarget(inc)} className="p-2 text-gray-400 dark:text-gray-500 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg transition-colors" title="Delete">
                          <FiTrash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="md:hidden divide-y divide-gray-100 dark:divide-gray-700">
            {paginatedIncomes.map((inc) => (
              <div key={inc.id} className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center text-green-600 dark:text-green-400 text-sm font-bold shrink-0 mt-0.5">
                      {inc.source?.charAt(0)?.toUpperCase() || "I"}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{inc.source}</p>
                      {inc.description && <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">{inc.description}</p>}
                      <div className="flex items-center gap-2 mt-1.5">
                        <span className="text-xs text-gray-500 dark:text-gray-400">{formatDate(inc.date)}</span>
                        {inc.is_recurring && (
                          <span className="text-xs text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-900/30 px-1.5 py-0.5 rounded-full flex items-center gap-1">
                            <FiRepeat className="w-3 h-3" /> Recurring
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-green-600 dark:text-green-400">+{formatCurrency(inc.amount)}</p>
                  </div>
                </div>
                <div className="flex gap-2 mt-3 pt-3 border-t border-gray-50 dark:border-gray-700">
                  <button onClick={() => setDetailTarget(inc)} className="flex-1 text-xs py-1.5 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 font-medium flex items-center justify-center gap-1">
                    <FiFileText className="w-3.5 h-3.5" /> View
                  </button>
                  <button onClick={() => handleEdit(inc)} className="flex-1 text-xs py-1.5 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 rounded-lg hover:bg-indigo-100 dark:hover:bg-indigo-900/30 font-medium flex items-center justify-center gap-1">
                    <FiEdit2 className="w-3.5 h-3.5" /> Edit
                  </button>
                  <button onClick={() => setDeleteTarget(inc)} className="flex-1 text-xs py-1.5 bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 font-medium flex items-center justify-center gap-1">
                    <FiTrash2 className="w-3.5 h-3.5" /> Delete
                  </button>
                </div>
              </div>
            ))}
          </div>

          {totalPages > 1 && (
            <div className="px-4 py-4 border-t border-gray-100 dark:border-gray-700 flex flex-col sm:flex-row items-center justify-between gap-3">
              <p className="text-sm text-gray-500 dark:text-gray-400">Page {page} of {totalPages} ({incomes.length} results)</p>
              <div className="flex items-center gap-1.5">
                <button onClick={() => setPage(1)} disabled={page === 1} className="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-30 disabled:cursor-not-allowed"><FiChevronsLeft className="w-4 h-4" /></button>
                <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page === 1} className="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-30 disabled:cursor-not-allowed"><FiChevronLeft className="w-4 h-4" /></button>
                {(() => {
                  const pages = [];
                  const start = Math.max(1, page - 2);
                  const end = Math.min(totalPages, page + 2);
                  for (let i = start; i <= end; i++) {
                    pages.push(
                      <button key={i} onClick={() => setPage(i)} className={`min-w-[36px] h-9 rounded-lg text-sm font-medium transition-colors ${i === page ? "bg-green-600 text-white" : "text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"}`}>{i}</button>
                    );
                  }
                  return pages;
                })()}
                <button onClick={() => setPage(Math.min(totalPages, page + 1))} disabled={page === totalPages} className="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-30 disabled:cursor-not-allowed"><FiChevronRight className="w-4 h-4" /></button>
                <button onClick={() => setPage(totalPages)} disabled={page === totalPages} className="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-30 disabled:cursor-not-allowed"><FiChevronsRight className="w-4 h-4" /></button>
              </div>
            </div>
          )}
        </div>
      )}

      <DetailModal income={detailTarget} onClose={() => setDetailTarget(null)} />
      <DeleteModal target={deleteTarget} onConfirm={handleDelete} onCancel={() => setDeleteTarget(null)} />

      {undoTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 dark:bg-black/70 backdrop-blur-sm" onClick={() => setUndoTarget(null)}>
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-sm p-6 animate-fade-in" onClick={(e) => e.stopPropagation()}>
            <div className="text-center">
              <div className="w-14 h-14 bg-orange-100 dark:bg-orange-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
                <FiRefreshCw className="w-6 h-6 text-orange-600 dark:text-orange-400" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">Undo Last Action</h3>
              <p className="text-gray-500 dark:text-gray-400 text-sm">This will reverse your last income operation.</p>
            </div>
            <div className="flex gap-3 mt-6">
              <button onClick={() => setUndoTarget(null)} className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 font-medium">Cancel</button>
              <button onClick={handleUndoConfirm} className="flex-1 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 font-medium flex items-center justify-center gap-2">
                <FiRefreshCw className="w-4 h-4" /> Undo
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
