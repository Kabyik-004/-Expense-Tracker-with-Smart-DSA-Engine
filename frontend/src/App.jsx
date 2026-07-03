import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  Link,
  useLocation,
  useNavigate,
} from "react-router-dom";
import {
  FiHome,
  FiDollarSign,
  FiTrendingUp,
  FiBarChart2,
  FiSettings,
  FiTarget,
  FiLogOut,
} from "react-icons/fi";

import ThemeSwitch from "./components/shared/ThemeSwitch";

import { AuthProvider } from "./context/AuthContext";
import { useAuth } from "./hooks/useAuth";
import { ExpenseProvider } from "./context/ExpenseContext";
import { ToastProvider } from "./components/shared/Toast";

import { lazy, Suspense } from "react";

const LandingPage = lazy(() => import("./pages/LandingPage"));
const Login = lazy(() => import("./pages/Login"));
const Register = lazy(() => import("./pages/Register"));
const Dashboard = lazy(() => import("./pages/Dashboard"));
const Expenses = lazy(() => import("./pages/Expenses"));
const Incomes = lazy(() => import("./pages/Incomes"));
const Analytics = lazy(() => import("./pages/Analytics"));
const Settings = lazy(() => import("./pages/Settings"));
const Budgets = lazy(() => import("./pages/Budgets"));

const navItems = [
  { path: "/dashboard", label: "Dashboard", icon: FiHome },
  { path: "/expenses", label: "Expenses", icon: FiDollarSign },
  { path: "/incomes", label: "Incomes", icon: FiTrendingUp },
  { path: "/budgets", label: "Budgets", icon: FiTarget },
  { path: "/analytics", label: "Analytics", icon: FiBarChart2 },
  { path: "/settings", label: "Settings", icon: FiSettings },
];

function LoadingScreen() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-950">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
    </div>
  );
}

function SuspenseWrapper({ children }) {
  return <Suspense fallback={<LoadingScreen />}>{children}</Suspense>;
}

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) return <LoadingScreen />;

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <SuspenseWrapper>{children}</SuspenseWrapper>;
}

function PublicRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) return <LoadingScreen />;

  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  return <SuspenseWrapper>{children}</SuspenseWrapper>;
}

function AppLayout() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-gray-950">
      <aside className="w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 flex flex-col">
        <div className="p-6 border-b border-gray-100 dark:border-gray-800">
          <h1 className="text-lg font-bold text-indigo-600">
            Expense Tracker
          </h1>
          <p className="text-xs text-gray-400 mt-1">Smart DSA Engine</p>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {navItems.map(({ path, label, icon: Icon }) => (
            <Link
              key={path}
              to={path}
              className={`flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                location.pathname === path
                  ? "bg-indigo-50 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300"
                  : "text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800"
              }`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </Link>
          ))}
        </nav>

        <div className="p-4 border-t border-gray-100 dark:border-gray-800">
          <div className="flex items-center gap-3 mb-3 px-4">
            <div className="w-8 h-8 bg-indigo-100 dark:bg-indigo-900/50 rounded-full flex items-center justify-center text-sm font-medium text-indigo-600 dark:text-indigo-300">
              {user?.full_name?.charAt(0) ||
                user?.username?.charAt(0) ||
                "U"}
            </div>

            <div className="text-sm">
              <p className="font-medium text-gray-900 dark:text-gray-100 truncate max-w-[140px]">
                {user?.full_name || user?.username}
              </p>

              <p className="text-gray-400 text-xs">{user?.email}</p>
            </div>
          </div>

          <div className="px-4 mb-2">
            <p className="text-xs font-medium text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-2">Theme</p>
            <ThemeSwitch />
          </div>

          <button
            onClick={handleLogout}
            className="flex items-center gap-3 px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-red-600 w-full rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            <FiLogOut className="w-4 h-4" />
            Sign out
          </button>
        </div>
      </aside>

      <main className="flex-1 p-8 overflow-auto">
        <ExpenseProvider>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/expenses" element={<Expenses />} />
            <Route path="/incomes" element={<Incomes />} />
            <Route path="/budgets" element={<Budgets />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </ExpenseProvider>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <AuthProvider>
        <ToastProvider>
        <Routes>
          <Route path="/" element={<LandingPage />} />

          <Route
            path="/login"
            element={
              <PublicRoute>
                <Login />
              </PublicRoute>
            }
          />

          <Route
            path="/register"
            element={
              <PublicRoute>
                <Register />
              </PublicRoute>
            }
          />

          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          />
        </Routes>
        </ToastProvider>
      </AuthProvider>
    </Router>
  );
}