import { useState, useEffect, useCallback, useRef } from "react";
import { useAuth } from "../hooks/useAuth";
import { useNavigate, useLocation } from "react-router-dom";
import api from "../services/api";
import { formatCurrency, formatDate } from "../utils/helpers";
import {
  FiTrendingUp,
  FiTrendingDown,
  FiDollarSign,
  FiCreditCard,
  FiPlus,
  FiArrowRight,
  FiBarChart2,
  FiSettings,
  FiRefreshCw,
  FiAlertCircle,
} from "react-icons/fi";

export default function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [data, setData] = useState(null);
  const [recentTransactions, setRecentTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const fetching = useRef(false);

  const fetchData = useCallback(async () => {
    if (fetching.current) return;
    fetching.current = true;
    setLoading(true);
    setError(null);
    try {
      if (!localStorage.getItem("access_token")) {
        navigate("/login", { replace: true });
        return;
      }
      const [dashRes, expRes] = await Promise.all([
        api.get("/analytics/dashboard"),
        api.get("/expenses/"),
      ]);
      if (dashRes.data.success) setData(dashRes.data.data);
      if (expRes.data.success) setRecentTransactions(expRes.data.data.expenses || []);
    } catch (err) {
      let msg;
      if (err.code === "ECONNABORTED") {
        msg = "Request timed out — Render may be cold-starting. Click Retry in 30s.";
      } else if (err.response) {
        msg = err.response.data?.message || `Server error (${err.response.status})`;
      } else if (err.request) {
        msg = "Backend unreachable — check if Render is running";
      } else {
        msg = err.message || "Failed to load dashboard data";
      }
      setError(msg);
    } finally {
      setLoading(false);
      fetching.current = false;
    }
  }, [navigate]);

  useEffect(() => {
    fetchData();
  }, [fetchData, location.pathname]);

  useEffect(() => {
    const handleFocus = () => fetchData();
    window.addEventListener("focus", handleFocus);
    return () => window.removeEventListener("focus", handleFocus);
  }, [fetchData]);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2" />
              <div className="h-8 bg-gray-200 rounded w-1/2" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 flex items-start gap-4">
          <FiAlertCircle className="w-6 h-6 text-red-500 shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="text-sm font-semibold text-red-800">Failed to load dashboard</h3>
            <p className="text-sm text-red-600 mt-1">{error}</p>
          </div>
          <button
            onClick={fetchData}
            className="shrink-0 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm font-medium flex items-center gap-2"
          >
            <FiRefreshCw className="w-4 h-4" /> Retry
          </button>
        </div>
      </div>
    );
  }

  const s = data?.summary || {};
  const balance = s.balance || 0;
  const totalIncome = s.total_income || 0;
  const totalExpense = s.total_expense || 0;

  const stats = [
    {
      label: "Total Income",
      value: formatCurrency(totalIncome),
      icon: FiTrendingUp,
      color: "text-green-600",
      bg: "bg-green-50",
      trend: "+12.5%",
      trendColor: "text-green-600",
    },
    {
      label: "Total Expenses",
      value: formatCurrency(totalExpense),
      icon: FiTrendingDown,
      color: "text-red-600",
      bg: "bg-red-50",
      trend: "+8.2%",
      trendColor: "text-red-600",
    },
    {
      label: "Balance",
      value: formatCurrency(balance),
      icon: FiDollarSign,
      color: balance >= 0 ? "text-indigo-600" : "text-red-600",
      bg: balance >= 0 ? "bg-indigo-50" : "bg-red-50",
      trend: balance >= 0 ? "Positive" : "Negative",
      trendColor: balance >= 0 ? "text-green-600" : "text-red-600",
    },
  ];

  const quickActions = [
    {
      label: "Add Expense",
      icon: FiPlus,
      color: "bg-red-100 text-red-600 hover:bg-red-200",
      path: "/expenses",
      action: () => navigate("/expenses"),
    },
    {
      label: "Add Income",
      icon: FiCreditCard,
      color: "bg-green-100 text-green-600 hover:bg-green-200",
      path: "/incomes",
      action: () => navigate("/incomes"),
    },
    {
      label: "View Analytics",
      icon: FiBarChart2,
      color: "bg-indigo-100 text-indigo-600 hover:bg-indigo-200",
      path: "/analytics",
      action: () => navigate("/analytics"),
    },
    {
      label: "Settings",
      icon: FiSettings,
      color: "bg-gray-100 text-gray-600 hover:bg-gray-200",
      path: "/settings",
      action: () => navigate("/settings"),
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Welcome{user?.full_name ? `, ${user.full_name}` : ""}
          </h1>
          <p className="text-gray-500 mt-1">Here's your financial overview</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={fetchData}
            className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors flex items-center gap-2"
            title="Refresh dashboard data"
          >
            <FiRefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4" role="list" aria-label="Financial statistics">
        {stats.map((stat, _index) => (
          <article
            key={stat.label}
            className="bg-white rounded-xl shadow-sm p-6 border border-gray-100 hover:shadow-md transition-shadow duration-200"
            role="listitem"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-gray-500 font-medium">{stat.label}</p>
                <p className={`text-2xl font-bold mt-1 ${stat.color}`}>{stat.value}</p>
                <p className={`text-xs font-medium mt-2 ${stat.trendColor} flex items-center gap-1`}>
                  <span className="text-gray-400">vs last month</span>
                  {stat.trend}
                </p>
              </div>
              <div className={`p-3 rounded-xl ${stat.bg}`}>
                <stat.icon className={`w-6 h-6 ${stat.color}`} aria-hidden="true" />
              </div>
            </div>
          </article>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <section className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="p-6 border-b border-gray-100 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <h2 className="text-lg font-semibold text-gray-900">Recent Transactions</h2>
            <button
              onClick={() => navigate("/expenses")}
              className="text-sm text-indigo-600 hover:underline font-medium flex items-center gap-1"
            >
              View all <FiArrowRight className="w-4 h-4" />
            </button>
          </div>
          <div className="divide-y divide-gray-100">
            {recentTransactions.length === 0 ? (
              <div className="p-12 text-center">
                <FiCreditCard className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500">No transactions yet</p>
                <button
                  onClick={() => navigate("/expenses")}
                  className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors"
                >
                  Add your first expense
                </button>
              </div>
            ) : (
              recentTransactions.map((txn) => (
                <article
                  key={txn.id}
                  className="p-4 hover:bg-gray-50 transition-colors flex items-center gap-4"
                >
                  <div
                    className="w-10 h-10 rounded-full flex items-center justify-center bg-red-100 text-red-600"
                  >
                    <FiTrendingDown className="w-5 h-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 truncate">{txn.title}</p>
                    <p className="text-sm text-gray-500 flex items-center gap-2">
                      <span>{txn.category_name || "Uncategorized"}</span>
                      <span className="text-gray-300">•</span>
                      <span>{formatDate(txn.date)}</span>
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-red-600">
                      -{formatCurrency(txn.amount)}
                    </p>
                    <p className="text-xs text-gray-400">{txn.payment_method || "Cash"}</p>
                  </div>
                </article>
              ))
            )}
          </div>
        </section>

        <aside className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 space-y-4">
          <h2 className="text-lg font-semibold text-gray-900">Quick Actions</h2>
          <div className="space-y-2" role="list" aria-label="Quick actions">
            {quickActions.map((action) => (
              <button
                key={action.label}
                onClick={action.action}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 hover:shadow-md ${
                  action.color
                }`}
                role="listitem"
              >
                <action.icon className="w-5 h-5" aria-hidden="true" />
                <span className="font-medium">{action.label}</span>
              </button>
            ))}
          </div>

          <div className="pt-4 border-t border-gray-100">
            <h3 className="text-sm font-medium text-gray-900 mb-3">Spending Insights</h3>
            <div className="space-y-3">
              <div className="p-3 bg-indigo-50 rounded-lg">
                <p className="text-sm font-medium text-indigo-900">Top Category</p>
                <p className="text-lg font-semibold text-indigo-600 mt-1">
                  {data?.categories?.most_used?.category_name || "—"}
                </p>
                <p className="text-xs text-indigo-500 mt-1">
                  {formatCurrency(
                    data?.categories?.distribution?.find(
                      d => d.category_id === data?.categories?.most_used?.category_id
                    )?.total_amount || 0
                  )} total
                </p>
              </div>
              <div className="p-3 bg-green-50 rounded-lg">
                <p className="text-sm font-medium text-green-900">Savings Rate</p>
                <p className="text-lg font-semibold text-green-600 mt-1">
                  {totalIncome > 0
                    ? `${(((totalIncome - totalExpense) / totalIncome) * 100).toFixed(1)}%`
                    : "—"}
                </p>
                <p className="text-xs text-green-500 mt-1">of income saved</p>
              </div>
            </div>
          </div>
        </aside>
      </div>

      <section className="bg-white rounded-xl shadow-sm border border-gray-100 p-6" aria-labelledby="charts-heading">
        <h2 id="charts-heading" className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <FiBarChart2 className="w-5 h-5 text-indigo-600" />
          Charts & Analytics
        </h2>
        <div className="aspect-[4/3] bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl flex items-center justify-center relative overflow-hidden">
          <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg%20width%3D%2260%22%20height%3D%2260%22%20viewBox%3D%220%200%2060%2060%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Cg%20fill%3D%22none%22%20fill-rule%3D%22evenodd%22%3E%3Cg%20fill%3D%22%239C92AC%22%20fill-opacity%3D%220.05%22%3E%3Cpath%20d%3D%22M36%2034v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6%2034v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6%204V0H4v4H0v2h4v4h2V6h4V4H6z%22%2F%3E%3C%2Fg%3E%3C%2Fg%3E%3C%2Fsvg%3E')] opacity-50" />
          <div className="relative z-10 text-center p-8">
            <FiBarChart2 className="w-16 h-16 text-indigo-200 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">Charts coming soon</p>
            <p className="text-gray-400 text-sm mt-1">Expense trends, category breakdown, monthly comparison</p>
            <button
              onClick={() => navigate("/analytics")}
              className="mt-6 px-6 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors inline-flex items-center gap-2"
            >
              View Analytics <FiArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}