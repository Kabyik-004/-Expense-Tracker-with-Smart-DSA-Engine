import { useState, useEffect } from "react";
import { useToast } from "../components/shared/Toast";
import { formatCurrency } from "../utils/helpers";
import * as budgetService from "../services/budgetService";
import api from "../services/api";
import {
  FiTarget,
  FiAlertTriangle,
  FiAlertOctagon,
  FiPlus,
  FiTrash2,
  FiChevronLeft,
  FiChevronRight,
} from "react-icons/fi";

const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

export default function Budgets() {
  const { addToast } = useToast();
  const [status, setStatus] = useState(null);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ amount: "", category_id: "" });
  const [saving, setSaving] = useState(false);
  const now = new Date();
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [year, setYear] = useState(now.getFullYear());

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const [sRes, cRes] = await Promise.all([
          budgetService.getBudgetStatus(month, year),
          api.get("/categories/"),
        ]);
        if (sRes.success) setStatus(sRes.data);
        if (cRes.data.success) setCategories(cRes.data.data.categories);
      } catch {
        addToast("Failed to load budgets", "error");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [month, year, addToast]);

  const handleSetBudget = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = {
        amount: parseFloat(form.amount),
        month,
        year,
        category_id: form.category_id ? parseInt(form.category_id) : null,
      };
      const res = await budgetService.setBudget(payload);
      if (res.success) {
        addToast(res.message, "success");
        setShowForm(false);
        setForm({ amount: "", category_id: "" });
        fetchStatus(month, year);
      } else {
        addToast(res.message || "Failed to set budget", "error");
      }
    } catch {
      addToast("Failed to set budget", "error");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      const res = await budgetService.deleteBudget(id);
      if (res.success) {
        addToast("Budget deleted", "success");
        fetchStatus(month, year);
      }
    } catch {
      addToast("Failed to delete budget", "error");
    }
  };

  const changeMonth = (delta) => {
    let m = month + delta;
    let y = year;
    if (m < 1) { m = 12; y -= 1; }
    if (m > 12) { m = 1; y += 1; }
    setMonth(m);
    setYear(y);
  };

  const warningAlerts = status?.budgets?.filter((b) => b.warning && !b.exceeded) || [];
  const exceededAlerts = status?.budgets?.filter((b) => b.exceeded) || [];

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Budgets</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Set and track your monthly spending limits</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium transition-colors"
        >
          <FiPlus className="w-4 h-4" />
          Set Budget
        </button>
      </div>

      <div className="flex items-center justify-center gap-4 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-3">
        <button onClick={() => changeMonth(-1)} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"><FiChevronLeft className="w-4 h-4 text-gray-500 dark:text-gray-400" /></button>
        <span className="text-lg font-semibold text-gray-900 dark:text-white min-w-[140px] text-center">{MONTHS[month - 1]} {year}</span>
        <button onClick={() => changeMonth(1)} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"><FiChevronRight className="w-4 h-4 text-gray-500 dark:text-gray-400" /></button>
      </div>

      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6 animate-pulse">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-3" />
              <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded mb-2" />
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2" />
            </div>
          ))}
        </div>
      ) : status ? (
        <>
          {exceededAlerts.length > 0 && (
            <div className="bg-red-50 dark:bg-red-900/30 border border-red-200 rounded-xl p-4 space-y-2">
              <div className="flex items-center gap-2 text-red-700 dark:text-red-300 font-medium">
                <FiAlertOctagon className="w-5 h-5" />
                Exceeded Budget{exceededAlerts.length > 1 ? "s" : ""}
              </div>
              {exceededAlerts.map((b) => (
                <div key={b.budget.id} className="flex justify-between text-sm text-red-600 dark:text-red-400 pl-7">
                  <span>{b.budget.category_name || "Overall"}</span>
                  <span className="font-medium">{formatCurrency(b.spent - b.budget.amount)} over</span>
                </div>
              ))}
            </div>
          )}

          {warningAlerts.length > 0 && (
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 space-y-2">
              <div className="flex items-center gap-2 text-amber-700 font-medium">
                <FiAlertTriangle className="w-5 h-5" />
                Budget Warning{warningAlerts.length > 1 ? "s" : ""}
              </div>
              {warningAlerts.map((b) => (
                <div key={b.budget.id} className="flex justify-between text-sm text-amber-600 pl-7">
                  <span>{b.budget.category_name || "Overall"}</span>
                  <span className="font-medium">{b.percentage}% used</span>
                </div>
              ))}
            </div>
          )}

          {status.total_budget > 0 && (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                  <FiTarget className="w-4 h-4 text-indigo-500 dark:text-indigo-400" />
                  Overall Budget
                </h3>
              </div>
              <BudgetProgressBar
                percentage={status.overall_percentage}
                spent={status.total_spent}
                remaining={status.total_remaining}
              />
            </div>
          )}

          {status.budgets && status.budgets.length > 0 && (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Category Budgets</h3>
              <div className="space-y-5">
                {status.budgets.map((b) => (
                  <div key={b.budget.id} className="relative">
                    <div className="flex items-center justify-between mb-1.5">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-gray-900 dark:text-white">
                          {b.budget.category_icon ? `${b.budget.category_icon} ` : ""}
                          {b.budget.category_name || "Overall"}
                        </span>
                        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                          b.exceeded ? "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300" :
                          b.warning ? "bg-amber-100 text-amber-700" :
                          "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300"
                        }`}>
                          {b.exceeded ? "Exceeded" : b.warning ? "Warning" : "On Track"}
                        </span>
                      </div>
                      <button
                        onClick={() => handleDelete(b.budget.id)}
                        className="p-1 text-gray-300 hover:text-red-500 dark:hover:text-red-400 transition-colors"
                        title="Delete budget"
                      >
                        <FiTrash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                    <BudgetProgressBar
                      percentage={b.percentage}
                      spent={b.spent}
                      remaining={b.remaining}
                    />
                  </div>
                ))}
              </div>
            </div>
          )}

          {(!status.budgets || status.budgets.length === 0) && (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-12 text-center">
              <FiTarget className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500 dark:text-gray-400 font-medium">No budgets set for {MONTHS[month - 1]} {year}</p>
              <p className="text-gray-400 dark:text-gray-500 text-sm mt-1">Click "Set Budget" to create one</p>
            </div>
          )}
        </>
      ) : null}

      {showForm && (
        <div className="fixed inset-0 bg-black/30 dark:bg-black/70 flex items-center justify-center z-50" onClick={() => setShowForm(false)}>
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 w-full max-w-md mx-4 shadow-xl" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Set Budget</h3>
            <form onSubmit={handleSetBudget} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Category (optional)</label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
                  value={form.category_id}
                  onChange={(e) => setForm({ ...form, category_id: e.target.value })}
                >
                  <option value="">Overall Budget</option>
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.id}>
                      {cat.icon || "📦"} {cat.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Budget Amount</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  required
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
                  placeholder="e.g. 50000"
                  value={form.amount}
                  onChange={(e) => setForm({ ...form, amount: e.target.value })}
                />
              </div>
              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 text-sm font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 text-sm font-medium"
                >
                  {saving ? "Saving..." : "Save Budget"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

function BudgetProgressBar({ percentage, spent, remaining }) {
  const pct = Math.min(percentage, 100);
  const barColor = percentage > 100 ? "bg-red-500" : percentage >= 80 ? "bg-amber-500" : "bg-green-500";
  const barBg = percentage > 100 ? "bg-red-100 dark:bg-red-900/30" : percentage >= 80 ? "bg-amber-100" : "bg-green-100 dark:bg-green-900/30";

  return (
    <div>
      <div className={`w-full ${barBg} rounded-full h-3 mb-2`}>
        <div
          className={`${barColor} h-3 rounded-full transition-all duration-500 ease-out`}
          style={{ width: `${Math.min(pct, 100)}%` }}
        />
      </div>
      <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
        <span>{formatCurrency(spent)} spent</span>
        <span className="font-semibold text-gray-700 dark:text-gray-200">{pct}%</span>
        <span>{formatCurrency(remaining)} left</span>
      </div>
    </div>
  );
}
