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
  FiUpload,
  FiLogOut,
} from "react-icons/fi";

import ThemeSwitch from "./components/shared/ThemeSwitch";

import { AuthProvider } from "./context/AuthContext";
import { useAuth } from "./hooks/useAuth";
import { ExpenseProvider } from "./context/ExpenseContext";
import { ToastProvider } from "./components/shared/Toast";
import FloatingActionButton from "./components/shared/FloatingActionButton";
import PageTransition from "./components/shared/PageTransition";
import ProfileMenu from "./components/shared/ProfileMenu";
import ErrorBoundary from "./components/shared/ErrorBoundary";

import { lazy, Suspense } from "react";
import dashboardLogo from "./assets/dashboard-logo.png";

const LandingPage = lazy(() => import("./pages/LandingPage"));
const Login = lazy(() => import("./pages/Login"));
const Register = lazy(() => import("./pages/Register"));
const ForgotPassword = lazy(() => import("./pages/ForgotPassword"));
const VerifyOTP = lazy(() => import("./pages/VerifyOTP"));
const ResetPassword = lazy(() => import("./pages/ResetPassword"));
const Dashboard = lazy(() => import("./pages/Dashboard"));
const Expenses = lazy(() => import("./pages/Expenses"));
const Incomes = lazy(() => import("./pages/Incomes"));
const Analytics = lazy(() => import("./pages/Analytics"));
const Settings = lazy(() => import("./pages/Settings"));
const Budgets = lazy(() => import("./pages/Budgets"));
const ImportPage = lazy(() => import("./pages/ImportStatement"));

const navItems = [
  { path: "/dashboard", label: "Dashboard", icon: FiHome },
  { path: "/expenses", label: "Expenses", icon: FiDollarSign },
  { path: "/incomes", label: "Incomes", icon: FiTrendingUp },
  { path: "/budgets", label: "Budgets", icon: FiTarget },
  { path: "/analytics", label: "Analytics", icon: FiBarChart2 },
  { path: "/import", label: "Smart Import", icon: FiUpload },
  { path: "/settings", label: "Settings", icon: FiSettings },
];

function LoadingScreen() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-950">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600"></div>
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
      <aside className="w-64 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-r border-gray-200/50 dark:border-gray-800/50 flex flex-col">
          <div className="p-6 border-b border-gray-100 dark:border-gray-800 flex items-center gap-3">
            <img src={dashboardLogo} alt="Expense Tracker" className="w-8 h-8 object-contain" />
            <div>
              <h1 className="text-lg font-bold text-emerald-600">
                Expense Tracker
              </h1>
              <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">Smart DSA Engine</p>
            </div>
          </div>

        <nav className="flex-1 p-4 space-y-1">
          {navItems.map(({ path, label, icon: Icon }) => (
            <Link
              key={path}
              to={path}
              className={`flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                location.pathname === path
                  ? "bg-emerald-50 dark:bg-emerald-900/50 text-emerald-700 dark:text-emerald-300"
                  : "text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800"
              }`}
            >
              <Icon className="icon-rotate w-4 h-4" />
              {label}
            </Link>
          ))}
        </nav>

        <div className="p-3 border-t border-gray-100 dark:border-gray-800 space-y-3">
          <ProfileMenu user={user} onLogout={handleLogout} />

          <div className="px-4">
            <p className="text-[10px] font-medium text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-1.5">Theme</p>
            <ThemeSwitch />
          </div>
        </div>
      </aside>

      <main className="flex-1 p-8 overflow-auto">
        <ExpenseProvider>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<PageTransition><Dashboard /></PageTransition>} />
            <Route path="/expenses" element={<PageTransition><Expenses /></PageTransition>} />
            <Route path="/incomes" element={<PageTransition><Incomes /></PageTransition>} />
            <Route path="/budgets" element={<PageTransition><Budgets /></PageTransition>} />
            <Route path="/analytics" element={<PageTransition><Analytics /></PageTransition>} />
            <Route path="/import" element={<PageTransition><ErrorBoundary><ImportPage /></ErrorBoundary></PageTransition>} />
            <Route path="/settings" element={<PageTransition><Settings /></PageTransition>} />
          </Routes>
        </ExpenseProvider>
      </main>
      <FloatingActionButton />
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
                <PageTransition><Login /></PageTransition>
              </PublicRoute>
            }
          />

          <Route
            path="/register"
            element={
              <PublicRoute>
                <PageTransition><Register /></PageTransition>
              </PublicRoute>
            }
          />

          <Route
            path="/forgot-password"
            element={
              <PublicRoute>
                <PageTransition><ForgotPassword /></PageTransition>
              </PublicRoute>
            }
          />

          <Route
            path="/verify-otp"
            element={
              <PublicRoute>
                <PageTransition><VerifyOTP /></PageTransition>
              </PublicRoute>
            }
          />

          <Route
            path="/reset-password"
            element={
              <PublicRoute>
                <PageTransition><ResetPassword /></PageTransition>
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