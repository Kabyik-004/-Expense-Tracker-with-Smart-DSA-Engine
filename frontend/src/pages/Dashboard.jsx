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
import { SkeletonDashboard } from "../components/shared/skeletons";
import EmptyState from "../components/shared/EmptyState";
import AnimatedCounter from "../components/shared/AnimatedCounter";
import CategoryIcon from "../components/shared/CategoryIcon";
import AnimatedCircularProgress from "../components/shared/AnimatedCircularProgress";
import * as budgetService from "../services/budgetService";

export default function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [data, setData] = useState(null);
  const [budgetStatus, setBudgetStatus] = useState(null);
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
      const now = new Date();
      const [dashRes, expRes, budRes] = await Promise.all([
        api.get("/analytics/dashboard"),
        api.get("/expenses/"),
        budgetService.getBudgetStatus(now.getMonth() + 1, now.getFullYear()),
      ]);
      if (dashRes.data.success) setData(dashRes.data.data);
      if (expRes.data.success) setRecentTransactions(expRes.data.data.expenses || []);
      if (budRes.success) setBudgetStatus(budRes.data);
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

  if (loading) return <SkeletonDashboard />;

  if (error) {
    return (
      <div className="space-y-6">
        <div className="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-xl p-6 flex items-start gap-4">
          <FiAlertCircle className="w-6 h-6 text-red-500 shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="text-sm font-semibold text-red-800 dark:text-red-300">Failed to load dashboard</h3>
            <p className="text-sm text-red-600 dark:text-red-400 mt-1">{error}</p>
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

  const incomePct = totalIncome > 0 ? ((totalExpense / totalIncome) * 100) : 0;

  const gradientSchemes = {
    income: {
      accent: "from-green-400 to-emerald-500",
      iconBg: "from-green-400 to-emerald-500",
      text: "text-green-600 dark:text-green-400",
      trend: "text-gray-400 dark:text-gray-500",
    },
    expense: {
      accent: "from-red-400 to-rose-500",
      iconBg: "from-red-400 to-rose-500",
      text: "text-red-600 dark:text-red-400",
      trend: "text-gray-400 dark:text-gray-500",
    },
    balance: {
      accent: balance >= 0 ? "from-emerald-400 to-emerald-500" : "from-red-400 to-rose-500",
      iconBg: balance >= 0 ? "from-emerald-400 to-emerald-500" : "from-red-400 to-rose-500",
      text: balance >= 0 ? "text-emerald-600 dark:text-emerald-400" : "text-red-600 dark:text-red-400",
      trend: balance >= 0 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400",
    },
  };

  const stats = [
    {
      label: "Total Income",
      rawValue: totalIncome,
      icon: FiTrendingUp,
      scheme: gradientSchemes.income,
      trend: totalIncome > 0 ? `${formatCurrency(totalIncome)} period` : "—",
    },
    {
      label: "Total Expenses",
      rawValue: totalExpense,
      icon: FiTrendingDown,
      scheme: gradientSchemes.expense,
      trend: totalExpense > 0 ? `${incomePct.toFixed(1)}% of income` : "—",
    },
    {
      label: "Balance",
      rawValue: balance,
      icon: FiDollarSign,
      scheme: gradientSchemes.balance,
      trend: totalIncome > 0 ? `${((Math.abs(balance) / totalIncome) * 100).toFixed(1)}% ${balance >= 0 ? "saved" : "overspent"}` : "—",
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
      color: "bg-emerald-100 text-emerald-600 hover:bg-emerald-200",
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
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Welcome{user?.full_name ? `, ${user.full_name}` : ""}
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Here's your financial overview</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={fetchData}
            className="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center gap-2"
            title="Refresh dashboard data"
          >
            <FiRefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4" role="list" aria-label="Financial statistics">
        {stats.map((stat) => (
          <article
            key={stat.label}
            className="relative group bg-white/70 dark:bg-gray-800/70 backdrop-blur-xl rounded-xl border border-white/40 dark:border-gray-700/30 shadow-lg shadow-black/5 dark:shadow-black/20 hover:shadow-xl hover:shadow-black/10 hover:-translate-y-0.5 transition-all duration-300 overflow-hidden"
            role="listitem"
          >
            <div className={`h-1 w-full bg-gradient-to-r ${stat.scheme.accent} opacity-80`} />
            <div className="p-6">
              <div className="flex items-start justify-between">
                <div className="space-y-1.5">
                  <p className="text-sm font-medium text-gray-500 dark:text-gray-400 tracking-wide">{stat.label}</p>
                  <p className={`text-2xl font-bold tabular-nums ${stat.scheme.text}`}>
                    {stat.rawValue !== 0 ? (
                      <AnimatedCounter value={stat.rawValue} formatter={formatCurrency} />
                    ) : (
                      formatCurrency(0)
                    )}
                  </p>
                  <p className={`text-xs font-medium mt-1.5 ${stat.scheme.trend}`}>{stat.trend}</p>
                </div>
                <div className={`p-3 rounded-xl bg-gradient-to-br ${stat.scheme.iconBg} shadow-lg shadow-black/10 dark:shadow-black/30 group-hover:scale-110 group-hover:shadow-xl transition-all duration-300 animate-float-subtle motion-reduce:animate-none`}>
                  <stat.icon className="w-6 h-6 text-white" aria-hidden="true" />
                </div>
              </div>
            </div>
          </article>
        ))}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white/70 dark:bg-gray-800/70 backdrop-blur-xl rounded-xl border border-white/40 dark:border-gray-700/30 shadow-lg shadow-black/5 dark:shadow-black/20 p-5 sm:p-6 flex flex-col items-center gap-4 transition-all duration-300 hover:shadow-xl">
          <AnimatedCircularProgress
            value={budgetStatus?.total_budget > 0 ? Math.min(budgetStatus.overall_percentage, 100) : 0}
            size={130}
            strokeWidth={9}
            color="url(#budgetGradient)"
            label="Monthly Budget"
            subtitle={budgetStatus?.total_budget > 0 ? `${formatCurrency(budgetStatus.total_spent)} / ${formatCurrency(budgetStatus.total_budget)}` : "No budget set"}
          >
            <div className="text-center">
              <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400 tabular-nums">
                {budgetStatus?.total_budget > 0 ? `${Math.round(budgetStatus.overall_percentage)}%` : "—"}
              </p>
              <p className="text-[10px] text-gray-400 dark:text-gray-500 mt-0.5">used</p>
            </div>
          </AnimatedCircularProgress>
          <svg width="0" height="0" className="absolute">
            <defs>
              <linearGradient id="budgetGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#059669" />
                <stop offset="100%" stopColor="#047857" />
              </linearGradient>
            </defs>
          </svg>
        </div>

        <div className="bg-white/70 dark:bg-gray-800/70 backdrop-blur-xl rounded-xl border border-white/40 dark:border-gray-700/30 shadow-lg shadow-black/5 dark:shadow-black/20 p-5 sm:p-6 flex flex-col items-center gap-4 transition-all duration-300 hover:shadow-xl">
          <AnimatedCircularProgress
            value={totalIncome > 0 ? Math.max(0, Math.min(((totalIncome - totalExpense) / totalIncome) * 100, 100)) : 0}
            size={130}
            strokeWidth={9}
            color="url(#savingsGradient)"
            label="Savings Rate"
            subtitle={totalIncome > 0 ? `${formatCurrency(totalIncome - totalExpense)} saved` : "No income data"}
          >
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600 dark:text-green-400 tabular-nums">
                {totalIncome > 0 ? `${((totalIncome - totalExpense) / totalIncome * 100).toFixed(0)}%` : "—"}
              </p>
              <p className="text-[10px] text-gray-400 dark:text-gray-500 mt-0.5">saved</p>
            </div>
          </AnimatedCircularProgress>
          <svg width="0" height="0" className="absolute">
            <defs>
              <linearGradient id="savingsGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#10b981" />
                <stop offset="100%" stopColor="#059669" />
              </linearGradient>
            </defs>
          </svg>
        </div>

        <div className="bg-white/70 dark:bg-gray-800/70 backdrop-blur-xl rounded-xl border border-white/40 dark:border-gray-700/30 shadow-lg shadow-black/5 dark:shadow-black/20 p-5 sm:p-6 flex flex-col items-center gap-4 transition-all duration-300 hover:shadow-xl sm:col-span-2 lg:col-span-1">
          <AnimatedCircularProgress
            value={totalIncome > 0 ? Math.min((totalExpense / totalIncome) * 100, 100) : 0}
            size={130}
            strokeWidth={9}
            color={totalIncome > 0 && (totalExpense / totalIncome) > 0.8 ? "url(#spendingHighGradient)" : "url(#spendingLowGradient)"}
            label="Spending Ratio"
            subtitle={totalIncome > 0 ? `${formatCurrency(totalExpense)} of ${formatCurrency(totalIncome)}` : "No data"}
          >
            <div className="text-center">
              <p className="text-2xl font-bold tabular-nums" style={{ color: totalIncome > 0 && (totalExpense / totalIncome) > 0.8 ? "#ef4444" : "#f59e0b" }}>
                {totalIncome > 0 ? `${(totalExpense / totalIncome * 100).toFixed(0)}%` : "—"}
              </p>
              <p className="text-[10px] text-gray-400 dark:text-gray-500 mt-0.5">of income</p>
            </div>
          </AnimatedCircularProgress>
          <svg width="0" height="0" className="absolute">
            <defs>
              <linearGradient id="spendingLowGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#f59e0b" />
                <stop offset="100%" stopColor="#d97706" />
              </linearGradient>
              <linearGradient id="spendingHighGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#ef4444" />
                <stop offset="100%" stopColor="#dc2626" />
              </linearGradient>
            </defs>
          </svg>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <section className="lg:col-span-2 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
          <div className="p-6 border-b border-gray-100 dark:border-gray-700 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Recent Transactions</h2>
            <button
              onClick={() => navigate("/expenses")}
              className="link-underline text-sm text-emerald-600 font-medium flex items-center gap-1"
            >
              View all <FiArrowRight className="w-4 h-4" />
            </button>
          </div>
          <div className="divide-y divide-gray-100 dark:divide-gray-700">
            {recentTransactions.length === 0 ? (
              <EmptyState
                icon={<FiCreditCard className="w-7 h-7" />}
                title="No transactions yet"
                description="Your recent expenses will appear here once you add your first one."
                action={{ label: "Add your first expense", onClick: () => navigate("/expenses") }}
                color="emerald"
              />
            ) : (
              recentTransactions.map((txn) => (
                <article
                  key={txn.id}
                  className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors flex items-center gap-4"
                >
                  <CategoryIcon name={txn.category_name} size="md" />
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 dark:text-white truncate">{txn.title}</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400 flex items-center gap-2">
                      <span>{txn.category_name || "Uncategorized"}</span>
                      <span className="text-gray-300 dark:text-gray-600">•</span>
                      <span>{formatDate(txn.date)}</span>
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-red-600 dark:text-red-400">
                       -{formatCurrency(txn.amount)}
                    </p>
                    <p className="text-xs text-gray-400 dark:text-gray-500">{txn.payment_method || "Cash"}</p>
                  </div>
                </article>
              ))
            )}
          </div>
        </section>

        <aside className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6 space-y-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Quick Actions</h2>
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

          <div className="pt-4 border-t border-gray-100 dark:border-gray-700">
            <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-3">Spending Insights</h3>
            <div className="space-y-3">
              <div className="p-3 bg-emerald-50 dark:bg-emerald-900/30 rounded-lg">
                <p className="text-sm font-medium text-emerald-900 dark:text-emerald-300">Top Category</p>
                <div className="flex items-center gap-2 mt-2">
                  <CategoryIcon name={data?.categories?.most_used?.category_name} size="sm" />
                  <p className="text-lg font-semibold text-emerald-600 dark:text-emerald-400">
                    {data?.categories?.most_used?.category_name || "—"}
                  </p>
                </div>
                <p className="text-xs text-emerald-500 dark:text-emerald-400 mt-1">
                  {formatCurrency(
                    data?.categories?.distribution?.find(
                      d => d.category_id === data?.categories?.most_used?.category_id
                    )?.total_amount || 0
                  )} total
                </p>
              </div>
              <div className="p-3 bg-green-50 dark:bg-green-900/30 rounded-lg">
                <p className="text-sm font-medium text-green-900 dark:text-green-300">Savings Rate</p>
                <p className="text-lg font-semibold text-green-600 dark:text-green-400 mt-1">
                  {totalIncome > 0
                    ? `${(((totalIncome - totalExpense) / totalIncome) * 100).toFixed(1)}%`
                    : "—"}
                </p>
                <p className="text-xs text-green-500 dark:text-green-400 mt-1">of income saved</p>
              </div>
            </div>
          </div>
        </aside>
      </div>

      <section className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6" aria-labelledby="charts-heading">
        <h2 id="charts-heading" className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <FiBarChart2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
          Charts & Analytics
        </h2>
        <div className="bg-gradient-to-br from-emerald-50 dark:from-emerald-900/20 to-emerald-50 dark:to-emerald-900/20 rounded-xl">
          <EmptyState
            icon={<FiBarChart2 className="w-7 h-7" />}
            title="Charts coming soon"
            description="Expense trends, category breakdown, monthly comparison"
            action={{ label: "View Analytics", onClick: () => navigate("/analytics"), icon: <FiArrowRight className="w-4 h-4" /> }}
            color="emerald"
            size="large"
          />
        </div>
      </section>
      <style>{`
        @keyframes float-subtle {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-4px); }
        }
        .animate-float-subtle {
          animation: float-subtle 3s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}