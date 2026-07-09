import { useState, useEffect } from "react";
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Filler } from "chart.js";
import { Pie, Bar, Line, Doughnut } from "react-chartjs-2";
import api from "../services/api";
import { formatCurrency } from "../utils/helpers";
import {
  FiBarChart2,
  FiPieChart,
  FiTrendingUp,
  FiActivity,
  FiDollarSign,
  FiArrowUp,
  FiArrowDown,
} from "react-icons/fi";
import { SkeletonAnalytics } from "../components/shared/skeletons";
import EmptyState from "../components/shared/EmptyState";
import CategoryIcon from "../components/shared/CategoryIcon";
import { useTheme } from "../context/ThemeContext";

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Filler);

const LIGHT_COLORS = [
  "#059669", "#06b6d4", "#f59e0b", "#ef4444", "#10b981",
  "#047857", "#14b8a6", "#0ea5e9", "#f97316", "#84cc16",
  "#8b5cf6", "#6b7280",
];

const DARK_COLORS = [
  "#34d399", "#22d3ee", "#fbbf24", "#f87171", "#4ade80",
  "#6ee7b7", "#2dd4bf", "#38bdf8", "#fb923c", "#a3e635",
  "#a78bfa", "#a1a1aa",
];

function gradientBg(ctx, c1, c2) {
  if (!ctx?.chart?.chartArea) return c1;
  const { top, bottom } = ctx.chart.chartArea;
  const g = ctx.chart.ctx.createLinearGradient(0, top, 0, bottom);
  g.addColorStop(0, c1);
  g.addColorStop(1, c2);
  return g;
}

function getChartOptions(isDark) {
  const textColor = isDark ? "#A1A1AA" : "#64748B";
  const gridColor = isDark ? "rgba(255, 255, 255, 0.05)" : "rgba(0, 0, 0, 0.04)";
  const tooltipBg = isDark ? "rgba(17, 17, 17, 0.96)" : "rgba(15, 23, 42, 0.95)";
  const tooltipBorder = isDark ? "#27272A" : "transparent";

  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 800, easing: "easeOutQuart" },
    plugins: {
      legend: {
        position: "bottom",
        labels: {
          padding: 16,
          usePointStyle: true,
          boxWidth: 8,
          font: { size: 11 },
          color: textColor,
        },
      },
      tooltip: {
        backgroundColor: tooltipBg,
        borderColor: tooltipBorder,
        borderWidth: isDark ? 1 : 0,
        padding: 12,
        cornerRadius: 12,
        titleFont: { size: 13, weight: "600" },
        titleColor: isDark ? "#FAFAFA" : "#fff",
        bodyFont: { size: 12 },
        bodyColor: isDark ? "#A1A1AA" : "#fff",
        displayColors: true,
        boxPadding: 4,
        usePointStyle: true,
        caretSize: 8,
        caretPadding: 6,
      },
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { font: { size: 10 }, color: textColor },
      },
      y: {
        beginAtZero: true,
        grid: { color: gridColor, drawTicks: false },
        border: { dash: [4, 4], color: isDark ? "#27272A" : "#E2E8F0" },
        ticks: { font: { size: 10 }, padding: 8, color: textColor },
      },
    },
  };
}

export default function Analytics() {
  const { resolvedTheme } = useTheme();
  const isDark = resolvedTheme === "dark";
  const COLORS = isDark ? DARK_COLORS : LIGHT_COLORS;
  const chartOpts = getChartOptions(isDark);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [summary, setSummary] = useState(null);
  const [categoryData, setCategoryData] = useState(null);
  const [timeSeries, setTimeSeries] = useState(null);
  const [extremes, setExtremes] = useState(null);
  const [timeRange, setTimeRange] = useState("monthly");
  const [animate, setAnimate] = useState(false);

  const fetchData = () => {
    setLoading(true);
    setError(null);
    Promise.all([
      api.get("/analytics/dashboard"),
      api.get("/analytics/categories"),
      api.get("/analytics/time-series"),
    ])
      .then(([dashRes, catRes, tsRes]) => {
        if (dashRes.data.success) {
          const d = dashRes.data.data;
          setSummary(d.summary);
          setExtremes(d.extremes);
          if (!catRes.data.success) setCategoryData(d.categories);
          if (!tsRes.data.success) setTimeSeries(d.time_series);
        }
        if (catRes.data.success) setCategoryData(catRes.data.data);
        if (tsRes.data.success) setTimeSeries(tsRes.data.data);
      })
      .catch(() => setError("Failed to load analytics data"))
      .finally(() => {
        setLoading(false);
        setTimeout(() => setAnimate(true), 100);
      });
  };

  useEffect(() => {
    fetchData();
  }, []);

  const s = summary || {};
  const e = extremes || {};
  const dist = categoryData?.category_distribution || categoryData?.distribution || [];
  const top5 = categoryData?.top_5_categories || categoryData?.top_5 || [];
  const monthly = timeSeries?.monthly || {};
  const daily = timeSeries?.daily || {};

  const monthlyEntries = Object.entries(monthly)
    .sort(([a], [b]) => a.localeCompare(b))
    .slice(-12);
  const dailyEntries = Object.entries(daily)
    .sort(([a], [b]) => a.localeCompare(b))
    .slice(-30);

  const timeLabels = timeRange === "monthly" ? monthlyEntries.map(([m]) => {
    const [y, mon] = m.split("-");
    const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
    return `${months[parseInt(mon) - 1]} ${y}`;
  }) : dailyEntries.map(([d]) => {
    const parts = d.split("-");
    return `${parseInt(parts[1])}/${parseInt(parts[2])}`;
  });

  const timeValues = timeRange === "monthly"
    ? monthlyEntries.map(([, v]) => v.total)
    : dailyEntries.map(([, v]) => v.total);

  const hasTrend = timeLabels.length > 0 && timeValues.some(v => v > 0);

  const pieBorderColor = isDark ? "#18181B" : "#fff";

  const pieData = {
    labels: dist.map((d) => d.category_name || `#${d.category_id}`),
    datasets: [{
      data: dist.map((d) => d.total_amount),
      backgroundColor: COLORS.slice(0, dist.length),
      borderWidth: 2,
      borderColor: pieBorderColor,
      hoverOffset: 10,
    }],
  };

  const doughnutData = {
    labels: ["Total Income", "Total Expenses"],
    datasets: [{
      data: [s.total_income || 0, s.total_expense || 0],
      backgroundColor: isDark ? ["#4ade80", "#f87171"] : ["#10b981", "#ef4444"],
      borderWidth: 3,
      borderColor: pieBorderColor,
      hoverOffset: 12,
      spacing: 4,
    }],
  };

  const emeraldBar = isDark ? "#34d399" : "#059669";
  const emeraldBarRgba = isDark ? "rgba(52, 211, 153, " : "rgba(5, 150, 105, ";

  const barData = {
    labels: timeLabels,
    datasets: [{
      label: "Expenses",
      data: timeValues,
      backgroundColor: (ctx) => gradientBg(ctx, `${emeraldBarRgba}0.85)`, `${emeraldBarRgba}0.2)`),
      borderColor: emeraldBar,
      borderWidth: 1,
      borderRadius: 6,
      borderSkipped: false,
    }],
  };

  const areaData = {
    labels: timeLabels,
    datasets: [{
      label: "Expense Trend",
      data: timeValues,
      fill: true,
      backgroundColor: (ctx) => gradientBg(ctx, `${emeraldBarRgba}0.35)`, `${emeraldBarRgba}0)`),
      borderColor: emeraldBar,
      borderWidth: 2.5,
      pointBackgroundColor: emeraldBar,
      pointBorderColor: pieBorderColor,
      pointBorderWidth: 2,
      pointRadius: 3,
      pointHoverRadius: 7,
      tension: 0.4,
    }],
  };

  const statCards = [
    {
      label: "Total Income",
      value: s.total_income,
      color: "text-green-600 dark:text-green-400",
      bg: "bg-green-50 dark:bg-green-900/30",
      icon: FiArrowUp,
      change: s.total_income > 0 ? `${formatCurrency(s.total_income)} total` : "—",
    },
    {
      label: "Total Expenses",
      value: s.total_expense,
      color: "text-red-600 dark:text-red-400",
      bg: "bg-red-50 dark:bg-red-900/30",
      icon: FiArrowDown,
      change: s.total_expense > 0 ? `${formatCurrency(s.total_expense)} total` : "—",
    },
    {
      label: "Balance",
      value: s.balance,
      color: (s.balance || 0) >= 0 ? "text-emerald-600 dark:text-emerald-400" : "text-red-600 dark:text-red-400",
      bg: (s.balance || 0) >= 0 ? "bg-emerald-50 dark:bg-emerald-900/30" : "bg-red-50 dark:bg-red-900/30",
      icon: FiDollarSign,
      change: s.total_income > 0
        ? `${(((s.balance || 0) / s.total_income) * 100).toFixed(1)}% saved`
        : "—",
    },
    {
      label: "Average Expense",
      value: e?.average_expense,
      color: "text-emerald-600",
      bg: "bg-emerald-50 dark:bg-emerald-900/30",
      icon: FiActivity,
      change: e?.highest_expense ? `vs highest ${formatCurrency(e.highest_expense.amount)}` : "—",
    },
  ];

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <p className="text-red-500 dark:text-red-400">{error}</p>
        <button onClick={fetchData} className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm hover:bg-emerald-700 transition-colors">
          Retry
        </button>
      </div>
    );
  }

  if (loading) return <SkeletonAnalytics />;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Analytics</h1>
        <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">Visual insights into your spending</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        {statCards.map((card) => (
          <div key={card.label} className={`${card.bg} rounded-xl p-4 sm:p-5 border border-transparent transition-all duration-300 ${animate ? "translate-y-0 opacity-100" : "translate-y-4 opacity-0"}`}>
            <div className="flex items-center justify-between mb-2">
              <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">{card.label}</p>
              <card.icon className={`w-4 h-4 ${card.color}`} />
            </div>
            <p className={`text-lg sm:text-xl font-bold ${card.color}`}>{formatCurrency(card.value)}</p>
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-1 truncate">{card.change}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-4 sm:p-6 transition-all duration-300 hover:shadow-md">
          <div className="flex items-center gap-2 mb-4">
            <FiPieChart className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
            <h2 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">Category Distribution</h2>
          </div>
          <div className="h-[280px] sm:h-[320px] flex items-center justify-center">
            {dist.length > 0 ? (
              <Pie data={pieData} options={{
                ...chartOpts,
                plugins: {
                  ...chartOpts.plugins,
                  legend: { ...chartOpts.plugins.legend, position: "right" },
                },
                spacing: 4,
              }} />
            ) : (
              <EmptyState icon={<FiPieChart className="w-6 h-6" />} title="No category data" color="emerald" />
            )}
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-4 sm:p-6 transition-all duration-300 hover:shadow-md">
          <div className="flex items-center gap-2 mb-4">
            <FiDollarSign className="w-5 h-5 text-green-600 dark:text-green-400" />
            <h2 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">Income vs Expenses</h2>
          </div>
          <div className="h-[280px] sm:h-[320px] flex items-center justify-center">
            {(s.total_income || s.total_expense) ? (
              <Doughnut data={doughnutData} options={{
                ...chartOpts,
                cutout: "68%",
                spacing: 6,
                plugins: {
                  ...chartOpts.plugins,
                  legend: { ...chartOpts.plugins.legend, position: "bottom" },
                },
              }} />
            ) : (
              <EmptyState icon={<FiDollarSign className="w-6 h-6" />} title="No data to compare" description="Add income and expenses to see the comparison" color="green" />
            )}
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-4 sm:p-6 transition-all duration-300 hover:shadow-md lg:col-span-2">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
            <div className="flex items-center gap-2">
              <FiBarChart2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
              <h2 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">Expense Trends</h2>
            </div>
            <div className="flex items-center bg-gray-100 dark:bg-gray-700 rounded-lg p-0.5 gap-0.5">
              {["monthly", "daily"].map((range) => (
                <button
                  key={range}
                  onClick={() => setTimeRange(range)}
                  className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors capitalize ${
                    timeRange === range ? "bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm" : "text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
                  }`}
                >
                  {range === "monthly" ? "Monthly" : "Daily"}
                </button>
              ))}
            </div>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="h-[260px] sm:h-[300px]">
              {hasTrend ? (
                <Bar data={barData} options={{
                  ...chartOpts,
                  scales: {
                    x: { grid: { display: false }, ticks: { font: { size: 10 }, color: chartOpts.plugins.legend.labels.color } },
                    y: {
                      beginAtZero: true,
                      grid: { color: chartOpts.scales.y.grid.color, drawTicks: false },
                      border: { dash: [4, 4], color: chartOpts.scales.y.border.color },
                      ticks: { font: { size: 10 }, padding: 8, callback: (v) => `₹${v}`, color: chartOpts.plugins.legend.labels.color },
                    },
                  },
                  plugins: {
                    legend: { display: false },
                    tooltip: {
                      ...chartOpts.plugins.tooltip,
                      callbacks: { label: (ctx) => `₹${ctx.parsed.y.toLocaleString("en-IN")}` },
                    },
                  },
                }} />
              ) : (
                <div className="flex items-center justify-center h-full">
                  <EmptyState icon={<FiBarChart2 className="w-6 h-6" />} title="No expense data" color="emerald" />
                </div>
              )}
            </div>
            <div className="h-[260px] sm:h-[300px]">
              {hasTrend ? (
                <Line data={areaData} options={{
                  ...chartOpts,
                  scales: {
                    x: { grid: { display: false }, ticks: { font: { size: 10 }, color: chartOpts.plugins.legend.labels.color } },
                    y: {
                      beginAtZero: true,
                      grid: { color: chartOpts.scales.y.grid.color, drawTicks: false },
                      border: { dash: [4, 4], color: chartOpts.scales.y.border.color },
                      ticks: { font: { size: 10 }, padding: 8, callback: (v) => `₹${v}`, color: chartOpts.plugins.legend.labels.color },
                    },
                  },
                  plugins: {
                    legend: { display: false },
                    tooltip: {
                      ...chartOpts.plugins.tooltip,
                      callbacks: { label: (ctx) => `₹${ctx.parsed.y.toLocaleString("en-IN")}` },
                    },
                  },
                  elements: { point: { hoverRadius: 7 } },
                }} />
              ) : (
                <div className="flex items-center justify-center h-full">
                  <EmptyState icon={<FiTrendingUp className="w-6 h-6" />} title="No trend data" color="emerald" />
                </div>
              )}
            </div>
          </div>
        </div>

        {top5.length > 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-4 sm:p-6 transition-all duration-300 hover:shadow-md lg:col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <FiTrendingUp className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
              <h2 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">Top Spending Categories</h2>
            </div>
            <div className="space-y-3">
              {top5.map((cat, idx) => {
                const pct = s.total_expense > 0 ? ((cat.total_amount / s.total_expense) * 100) : 0;
                return (
                  <div key={idx}>
                    <div className="flex items-center justify-between mb-1.5">
                      <div className="flex items-center gap-2">
                        <div className="relative shrink-0">
                          <CategoryIcon name={cat.category_name} size="sm" />
                          <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full flex items-center justify-center text-[9px] font-bold text-white ring-2 ring-white dark:ring-gray-800" style={{ backgroundColor: COLORS[idx % COLORS.length] }}>
                            {idx + 1}
                          </span>
                        </div>
                        <span className="text-sm font-medium text-gray-900 dark:text-white">{cat.category_name || `Category #${cat.category_id}`}</span>
                      </div>
                      <div className="text-right">
                        <span className="text-sm font-semibold text-gray-900 dark:text-white">{formatCurrency(cat.total_amount)}</span>
                        <span className="text-xs text-gray-400 dark:text-gray-500 ml-2">({cat.expense_count} expenses)</span>
                      </div>
                    </div>
                    <div className="w-full bg-gray-100 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-700"
                        style={{ width: `${animate ? Math.min(pct, 100) : 0}%`, backgroundColor: COLORS[idx % COLORS.length] }}
                      />
                    </div>
                    <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">{pct.toFixed(1)}% of total expenses</p>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}