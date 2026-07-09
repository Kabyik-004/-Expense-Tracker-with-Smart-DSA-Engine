import { useState, useEffect } from "react";
import { useAuth } from "../hooks/useAuth";
import { formatDate } from "../utils/helpers";
import { useToast } from "../components/shared/Toast";
import * as authService from "../services/authService";
import {
  FiUser,
  FiMail,
  FiCalendar,
  FiCamera,
  FiLock,
  FiKey,
  FiClock,
  FiPlusCircle,
  FiEdit3,
  FiTrash2,
  FiDollarSign,
  FiAtSign,
} from "react-icons/fi";
import { SkeletonSettingsActivity } from "../components/shared/skeletons";
import EmptyState from "../components/shared/EmptyState";

export default function Settings() {
  const { user, setUser } = useAuth();
  const { addToast } = useToast();
  const [activeTab, setActiveTab] = useState("profile");
  const [activities, setActivities] = useState([]);
  const [loadingActivity, setLoadingActivity] = useState(false);

  const tabs = [
    { id: "profile", label: "Profile", icon: FiUser },
    { id: "password", label: "Password", icon: FiLock },
    { id: "activity", label: "Activity", icon: FiClock },
  ];

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Settings</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Manage your account and profile</p>
        </div>
      </div>

      <div className="flex gap-1 bg-gray-100 dark:bg-gray-700 p-1 rounded-xl" role="tablist" aria-label="Settings tabs">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              role="tab"
              aria-selected={isActive}
              aria-controls={`tabpanel-${tab.id}`}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? "bg-white dark:bg-gray-800 text-emerald-600 dark:text-emerald-400 shadow-sm"
                  : "text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {activeTab === "profile" && (
        <div role="tabpanel" id="tabpanel-profile" aria-labelledby="tab-profile">
          <ProfileSection user={user} setUser={setUser} addToast={addToast} />
        </div>
      )}
      {activeTab === "password" && (
        <div role="tabpanel" id="tabpanel-password" aria-labelledby="tab-password">
          <PasswordSection addToast={addToast} />
        </div>
      )}
      {activeTab === "activity" && (
        <div role="tabpanel" id="tabpanel-activity" aria-labelledby="tab-activity">
          <ActivitySection
            activities={activities}
            setActivities={setActivities}
            loading={loadingActivity}
            setLoading={setLoadingActivity}
          />
        </div>
      )}
    </div>
  );
}

function ProfileSection({ user, setUser, addToast }) {
  const [form, setForm] = useState({
    full_name: user?.full_name || "",
    email: user?.email || "",
    username: user?.username || "",
    currency: user?.currency || "INR",
  });
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await authService.updateProfile(form);
      if (res.success) {
        setUser(res.data.user);
        addToast("Profile updated successfully", "success");
      } else {
        addToast(res.message || "Update failed", "error");
      }
    } catch {
      addToast("Update failed", "error");
    } finally {
      setSaving(false);
    }
  };

  const handleAvatarUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const maxSize = 1000000;
    if (file.size > maxSize) {
      addToast("Image must be under 1MB", "error");
      return;
    }

    setUploading(true);
    const reader = new FileReader();

    reader.onload = async () => {
      try {
        const base64 = reader.result;
        const res = await authService.uploadAvatar({ avatar: base64 });
        if (res.success) {
          setUser(res.data.user);
          addToast("Avatar updated", "success");
        } else {
          addToast(res.message || "Upload failed", "error");
        }
      } catch {
        addToast("Upload failed", "error");
      } finally {
        setUploading(false);
      }
    };

    reader.onerror = () => {
      addToast("Failed to read file", "error");
      setUploading(false);
    };

    reader.readAsDataURL(file);
  };

  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
        <div className="flex items-center gap-6">
          <div className="relative">
            <div className="w-20 h-20 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center overflow-hidden ring-2 ring-emerald-200">
              {user?.avatar ? (
                <img
                  src={user.avatar}
                  alt="Avatar"
                  className="w-full h-full object-cover"
                />
              ) : (
                <FiUser className="w-8 h-8 text-emerald-500 dark:text-emerald-400" />
              )}
            </div>
            <label className="absolute -bottom-1 -right-1 w-7 h-7 bg-emerald-600 text-white rounded-full flex items-center justify-center cursor-pointer hover:bg-emerald-700 shadow-sm transition-colors">
              <FiCamera className="w-3.5 h-3.5" />
              <input
                type="file"
                accept="image/*"
                className="hidden"
                onChange={handleAvatarUpload}
                disabled={uploading}
              />
            </label>
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              {user?.full_name || user?.username}
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">{user?.email}</p>
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">
              Member since {user?.created_at ? formatDate(user.created_at) : "—"}
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
        <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <FiEdit3 className="w-4 h-4 text-emerald-500 dark:text-emerald-400" />
          Edit Profile
        </h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Full Name</label>
              <input
                type="text"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm"
                value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Username</label>
              <input
                type="text"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm"
                value={form.username}
                onChange={(e) => setForm({ ...form, username: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Email</label>
              <input
                type="email"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Currency</label>
              <select
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm"
                value={form.currency}
                onChange={(e) => setForm({ ...form, currency: e.target.value })}
              >
                <option value="INR">INR (₹)</option>
                <option value="USD">USD ($)</option>
                <option value="EUR">EUR (€)</option>
                <option value="GBP">GBP (£)</option>
              </select>
            </div>
          </div>
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 text-sm font-medium transition-colors"
          >
            {saving ? "Saving..." : "Save Changes"}
          </button>
        </form>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
        <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <FiDollarSign className="w-4 h-4 text-emerald-500 dark:text-emerald-400" />
          Account Details
        </h3>
        <div className="space-y-3">
          {[
            { label: "User ID", value: user?.id, icon: FiAtSign },
            { label: "Username", value: user?.username, icon: FiUser },
            { label: "Email", value: user?.email, icon: FiMail },
            { label: "Currency", value: user?.currency, icon: FiDollarSign },
            { label: "Member Since", value: user?.created_at ? formatDate(user.created_at) : "—", icon: FiCalendar },
          ].map((item) => {
            const Icon = item.icon;
            return (
              <div key={item.label} className="flex items-center gap-3 text-sm">
                <div className="w-8 h-8 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Icon className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-gray-500 dark:text-gray-400">{item.label}</p>
                  <p className="font-medium text-gray-900 dark:text-white truncate">{item.value ?? "—"}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function PasswordSection({ addToast }) {
  const [form, setForm] = useState({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState({});

  const validate = () => {
    const errs = {};
    if (!form.current_password) errs.current_password = "Current password is required";
    if (!form.new_password) errs.new_password = "New password is required";
    else if (form.new_password.length < 8) errs.new_password = "Must be at least 8 characters";
    else if (!/[A-Z]/.test(form.new_password)) errs.new_password = "Must contain an uppercase letter";
    else if (!/[a-z]/.test(form.new_password)) errs.new_password = "Must contain a lowercase letter";
    else if (!/[0-9]/.test(form.new_password)) errs.new_password = "Must contain a digit";
    if (form.new_password !== form.confirm_password) errs.confirm_password = "Passwords do not match";
    return errs;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const errs = validate();
    setErrors(errs);
    if (Object.keys(errs).length > 0) return;

    setSaving(true);
    try {
      const res = await authService.changePassword({
        current_password: form.current_password,
        new_password: form.new_password,
      });
      if (res.success) {
        addToast("Password changed successfully", "success");
        setForm({ current_password: "", new_password: "", confirm_password: "" });
      } else {
        addToast(res.message || "Failed to change password", "error");
      }
    } catch {
      addToast("Failed to change password", "error");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
      <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
        <FiKey className="w-4 h-4 text-emerald-500 dark:text-emerald-400" />
        Change Password
      </h3>
      <form onSubmit={handleSubmit} className="space-y-4 max-w-md">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Current Password</label>
          <input
            type="password"
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm ${
              errors.current_password ? "border-red-300" : "border-gray-300 dark:border-gray-600"
            }`}
            value={form.current_password}
            onChange={(e) => setForm({ ...form, current_password: e.target.value })}
          />
          {errors.current_password && <p className="text-xs text-red-500 dark:text-red-400 mt-1">{errors.current_password}</p>}
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">New Password</label>
          <input
            type="password"
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm ${
              errors.new_password ? "border-red-300" : "border-gray-300 dark:border-gray-600"
            }`}
            value={form.new_password}
            onChange={(e) => setForm({ ...form, new_password: e.target.value })}
          />
          {errors.new_password && <p className="text-xs text-red-500 dark:text-red-400 mt-1">{errors.new_password}</p>}
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Confirm New Password</label>
          <input
            type="password"
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm ${
              errors.confirm_password ? "border-red-300" : "border-gray-300 dark:border-gray-600"
            }`}
            value={form.confirm_password}
            onChange={(e) => setForm({ ...form, confirm_password: e.target.value })}
          />
          {errors.confirm_password && <p className="text-xs text-red-500 dark:text-red-400 mt-1">{errors.confirm_password}</p>}
        </div>
        <button
          type="submit"
          disabled={saving}
          className="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 text-sm font-medium transition-colors"
        >
          {saving ? "Updating..." : "Update Password"}
        </button>
      </form>
    </div>
  );
}

function ActivitySection({ activities, setActivities, loading, setLoading }) {
  const { addToast } = useToast();

  useEffect(() => {
    setLoading(true);
    authService
      .getRecentActivity()
      .then((res) => {
        if (res.success) setActivities(res.data.activities);
      })
      .catch(() => addToast("Failed to load activity", "error"))
      .finally(() => setLoading(false));
  }, [setLoading, setActivities, addToast]);

  const getIcon = (action, entityType) => {
    if (action === "create" && entityType === "expense") return FiPlusCircle;
    if (action === "create" && entityType === "income") return FiPlusCircle;
    if (action === "update") return FiEdit3;
    if (action === "delete") return FiTrash2;
    return FiClock;
  };

  const getColor = (action) => {
    if (action === "create") return "text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900/30";
    if (action === "update") return "text-blue-600 dark:text-blue-400 bg-blue-100 dark:bg-blue-900/30";
    if (action === "delete") return "text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-900/30";
    return "text-gray-600 dark:text-gray-300 bg-gray-100 dark:bg-gray-700";
  };

  const getLabel = (action) => {
    if (action === "create") return "Created";
    if (action === "update") return "Updated";
    if (action === "delete") return "Deleted";
    return action;
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
      <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
        <FiClock className="w-4 h-4 text-emerald-500 dark:text-emerald-400" />
        Recent Activity
      </h3>

      {loading ? <SkeletonSettingsActivity rows={3} /> : activities.length === 0 ? (
        <EmptyState icon={<FiClock className="w-6 h-6" />} title="No recent activity" description="Your account actions will appear here" color="gray" />
      ) : (
        <div className="space-y-1">
          {activities.map((act) => {
            const Icon = getIcon(act.action, act.entity_type);
            const colorClass = getColor(act.action);
            return (
              <div
                key={act.id}
                className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
              >
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${colorClass}`}>
                  <Icon className="w-4 h-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-900 dark:text-white">
                    <span className="font-medium">{getLabel(act.action)}</span>{" "}
                    {act.entity_type}
                    {act.details && (
                      <span className="text-gray-500 dark:text-gray-400"> — {act.details}</span>
                    )}
                  </p>
                  <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">
                    {act.created_at ? formatDate(act.created_at) : "—"}
                  </p>
                </div>
                <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                  act.action === "create" ? "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300" :
                  act.action === "update" ? "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300" :
                  act.action === "delete" ? "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300" :
                  "bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300"
                }`}>
                  {act.action}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
