export const PAYMENT_METHODS = ["cash", "card", "upi", "bank_transfer"];

export const SORT_FIELDS = ["amount", "date", "category_id", "title"];

export const DEFAULT_CURRENCY = "INR";

export const API_PATHS = {
  auth: {
    register: "/auth/register",
    login: "/auth/login",
    refresh: "/auth/refresh",
    logout: "/auth/logout",
    profile: "/auth/profile",
    changePassword: "/auth/change-password",
    forgotPassword: "/auth/forgot-password",
    resetPassword: "/auth/reset-password",
    validate: "/auth/validate",
    avatar: "/auth/avatar",
    activity: "/auth/activity",
  },
  expenses: {
    base: "/expenses/",
    sort: {
      single: "/expenses/sort/single",
      multi: "/expenses/sort/multi",
    },
    undo: "/expenses/undo",
    undoStatus: "/expenses/undo/status",
    undoClear: "/expenses/undo/clear",
    summaries: {
      categoryTotals: "/expenses/summary/category-totals",
      categoryCounts: "/expenses/summary/category-counts",
      monthlyTotals: "/expenses/summary/monthly-totals",
    },
    search: {
      title: "/expenses/search/title",
      description: "/expenses/search/description",
      category: "/expenses/search/category",
      id: "/expenses/search/id",
      date: "/expenses/search/date",
      dateRange: "/expenses/search/date-range",
    },
  },
  incomes: {
    base: "/incomes/",
    undo: "/incomes/undo",
  },
  analytics: {
    overview: "/analytics/overview",
    categories: "/analytics/categories",
    timeSeries: "/analytics/time-series",
    dashboard: "/analytics/dashboard",
  },
  categories: {
    base: "/categories/",
  },
  budgets: {
    base: "/budgets/",
    status: "/budgets/status",
  },
  imports: {
    upload: "/import/upload",
    preview: "/import/preview",
    confirm: "/import/confirm",
    history: "/import/history",
    detail: (id) => `/import/${id}`,
    supportedBanks: "/import/supported-banks",
  },
};

export const IMPORT_FIELDS = [
  { key: "title", label: "Title", required: true, description: "Transaction name" },
  { key: "amount", label: "Amount", required: true, description: "Transaction amount" },
  { key: "date", label: "Date", required: true, description: "Transaction date" },
  { key: "description", label: "Description", required: false, description: "Additional details" },
  { key: "category", label: "Category", required: false, description: "Auto-categorized if mapped" },
  { key: "type", label: "Type", required: false, description: "Debit/Credit indicator" },
  { key: "balance", label: "Balance", required: false, description: "Running balance" },
];
