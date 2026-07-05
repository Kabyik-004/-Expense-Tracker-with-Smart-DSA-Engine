import { FiDollarSign, FiTrendingUp, FiTrendingDown, FiUploadCloud, FiCheck } from "react-icons/fi";

function BrowserFrame({ label, children }) {
  return (
    <figure className="group">
      <div className="relative rounded-t-xl overflow-hidden bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-md transition-all duration-300 group-hover:shadow-xl group-hover:-translate-y-0.5">
        <div className="flex items-center gap-1.5 px-4 py-3 bg-gray-50 dark:bg-gray-800/80 border-b border-gray-200 dark:border-gray-700">
          <span className="w-3 h-3 rounded-full bg-red-400" />
          <span className="w-3 h-3 rounded-full bg-yellow-400" />
          <span className="w-3 h-3 rounded-full bg-green-400" />
          <span className="ml-3 px-3 py-0.5 text-[11px] text-gray-400 dark:text-gray-500 bg-gray-200 dark:bg-gray-700 rounded-full truncate max-w-[160px] font-mono">
            expense-tracker.app/{label.toLowerCase()}
          </span>
        </div>
        <div className="bg-white dark:bg-gray-900">{children}</div>
      </div>
      <figcaption className="mt-3 text-center">
        <p className="text-sm font-semibold text-gray-900 dark:text-white">
          {label}
        </p>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
          {label === "Dashboard" && "Financial overview at a glance"}
          {label === "Expenses" && "Track and manage transactions"}
          {label === "Income" && "Monitor your earnings"}
          {label === "Analytics" && "Visual spending insights"}
          {label === "Import" && "Upload & parse statements"}
          {label === "Settings" && "Manage your profile"}
        </p>
      </figcaption>
    </figure>
  );
}

function TableRow({ title, amount, color }) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-800 last:border-0">
      <div className="flex items-center gap-2">
        <div className={`w-1.5 h-1.5 rounded-full ${color}`} />
        <span className="text-[11px] text-gray-600 dark:text-gray-400">{title}</span>
      </div>
      <span className={`text-[11px] font-semibold ${color}`}>{amount}</span>
    </div>
  );
}

export default function Screenshots() {
  return (
    <section id="screenshots" className="relative py-24 lg:py-32 bg-gray-50/50 dark:bg-gray-900/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <p className="text-indigo-600 dark:text-indigo-400 font-semibold text-sm tracking-wide uppercase mb-3">
            Screenshots
          </p>
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white tracking-tight">
            Beautiful{" "}
            <span className="text-indigo-600 dark:text-indigo-400">Interface</span>
          </h2>
          <p className="mt-4 text-lg text-gray-600 dark:text-gray-400">
            Clean, responsive design that works seamlessly across all devices.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-5xl mx-auto">
          <div className="md:col-span-2 lg:col-span-2">
            <BrowserFrame label="Dashboard">
              <div className="p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="h-4 w-28 bg-gray-200 dark:bg-gray-700 rounded" />
                    <div className="h-3 w-20 bg-gray-100 dark:bg-gray-800 rounded mt-1.5" />
                  </div>
                  <div className="h-7 w-16 bg-indigo-100 dark:bg-indigo-900/40 rounded-lg" />
                </div>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { color: "bg-green-500", label: "Income", value: "₹84K", bar: "w-3/4" },
                    { color: "bg-red-500", label: "Expenses", value: "₹63K", bar: "w-2/3" },
                    { color: "bg-indigo-500", label: "Balance", value: "₹21K", bar: "w-1/3" },
                  ].map((s) => (
                    <div key={s.label} className="p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-800">
                      <div className="flex items-center gap-1.5 mb-2">
                        {s.label === "Income" && <FiTrendingUp className="w-3 h-3 text-green-500" />}
                        {s.label === "Expenses" && <FiTrendingDown className="w-3 h-3 text-red-500" />}
                        {s.label === "Balance" && <FiDollarSign className="w-3 h-3 text-indigo-500" />}
                        <span className="text-[10px] text-gray-400 dark:text-gray-500">{s.label}</span>
                      </div>
                      <p className="text-sm font-bold text-gray-800 dark:text-gray-200">{s.value}</p>
                    </div>
                  ))}
                </div>
                <div className="p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-800">
                  <div className="flex items-end gap-1 h-16">
                    {[35, 55, 40, 70, 45, 60, 50, 75, 55, 65, 80, 60].map((h, i) => (
                      <div key={i} className="flex-1 rounded-t bg-gradient-to-t from-indigo-400 to-indigo-300 dark:from-indigo-600 dark:to-indigo-500" style={{ height: `${h}%` }} />
                    ))}
                  </div>
                  <div className="flex justify-between mt-1.5">
                    {["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"].map((m) => (
                      <span key={m} className="text-[9px] text-gray-400 dark:text-gray-600">{m}</span>
                    ))}
                  </div>
                </div>
              </div>
            </BrowserFrame>
          </div>

          <div className="lg:col-span-1">
            <BrowserFrame label="Expenses">
              <div className="p-4 space-y-3">
                <div className="flex gap-1.5 mb-3">
                  {["All", "Food", "Travel", "Shop"].map((t) => (
                    <span key={t} className={`px-2 py-0.5 text-[10px] rounded-full font-medium ${t === "All" ? "bg-indigo-100 dark:bg-indigo-900/40 text-indigo-600 dark:text-indigo-400" : "bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400"}`}>
                      {t}
                    </span>
                  ))}
                </div>
                <input className="w-full px-2.5 py-1.5 text-[11px] border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800 text-gray-400 dark:text-gray-500" readOnly value="Search transactions..." />
                <div className="space-y-1">
                  <TableRow title="Grocery Store" amount="-₹2,450" color="text-red-500" />
                  <TableRow title="Uber Ride" amount="-₹450" color="text-red-500" />
                  <TableRow title="Netflix" amount="-₹649" color="text-red-500" />
                  <TableRow title="Domino's" amount="-₹899" color="text-red-500" />
                  <TableRow title="Zomato" amount="-₹320" color="text-red-500" />
                </div>
              </div>
            </BrowserFrame>
          </div>

          <div className="lg:col-span-1">
            <BrowserFrame label="Income">
              <div className="p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] text-gray-400 dark:text-gray-500 uppercase tracking-wider font-semibold">Sources</span>
                  <span className="text-[10px] text-gray-400 dark:text-gray-500">This Month</span>
                </div>
                <div className="space-y-1">
                  <TableRow title="Salary" amount="₹55,000" color="text-green-600" />
                  <TableRow title="Freelance" amount="₹12,000" color="text-green-600" />
                  <TableRow title="Dividends" amount="₹3,200" color="text-green-600" />
                  <TableRow title="Rental" amount="₹8,500" color="text-green-600" />
                  <TableRow title="Interest" amount="₹1,800" color="text-green-600" />
                </div>
                <div className="pt-2 border-t border-gray-100 dark:border-gray-800 flex items-center justify-between">
                  <span className="text-[11px] text-gray-500 dark:text-gray-400 font-medium">Total</span>
                  <span className="text-xs font-bold text-green-600">₹80,500</span>
                </div>
              </div>
            </BrowserFrame>
          </div>

          <div className="lg:col-span-1">
            <BrowserFrame label="Analytics">
              <div className="p-4 space-y-4">
                <div className="flex gap-2">
                  {["Week", "Month", "Year"].map((t) => (
                    <span key={t} className={`flex-1 text-center px-2 py-1 text-[10px] rounded-md font-medium ${t === "Month" ? "bg-indigo-100 dark:bg-indigo-900/40 text-indigo-600 dark:text-indigo-400" : "bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400"}`}>
                      {t}
                    </span>
                  ))}
                </div>
                <div className="flex items-end gap-1.5 h-20">
                  {[20, 45, 30, 65, 40, 55, 35].map((h, i) => (
                    <div key={i} className="flex-1 rounded-t bg-gradient-to-t from-indigo-400 to-indigo-300 dark:from-indigo-600 dark:to-indigo-500" style={{ height: `${h}%` }} />
                  ))}
                </div>
                <div className="flex items-center justify-center gap-4">
                  {[
                    { label: "Food", color: "bg-orange-400", value: "42%" },
                    { label: "Travel", color: "bg-blue-400", value: "18%" },
                    { label: "Bills", color: "bg-purple-400", value: "25%" },
                  ].map((c) => (
                    <div key={c.label} className="flex items-center gap-1.5">
                      <div className={`w-2 h-2 rounded-full ${c.color}`} />
                      <span className="text-[10px] text-gray-500 dark:text-gray-400">{c.label}</span>
                    </div>
                  ))}
                </div>
              </div>
            </BrowserFrame>
          </div>

          <div className="lg:col-span-1">
            <BrowserFrame label="Import">
              <div className="p-5 space-y-3">
                <div className="border-2 border-dashed border-indigo-200 dark:border-indigo-700/60 rounded-xl p-5 text-center">
                  <div className="w-10 h-10 mx-auto rounded-xl bg-indigo-100 dark:bg-indigo-900/40 flex items-center justify-center mb-2">
                    <FiUploadCloud className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                  </div>
                  <p className="text-xs font-semibold text-gray-800 dark:text-gray-200">Upload Statement</p>
                  <p className="text-[10px] text-gray-400 dark:text-gray-500 mt-0.5">CSV, PDF or XLSX</p>
                </div>
                <div className="space-y-1">
                  <div className="flex items-center justify-between py-1.5 border-b border-gray-100 dark:border-gray-800">
                    <div className="flex items-center gap-1.5">
                      <div className="w-5 h-5 rounded bg-green-100 dark:bg-green-900/40 flex items-center justify-center">
                        <FiCheck className="w-3 h-3 text-green-600 dark:text-green-400" />
                      </div>
                      <span className="text-[10px] text-gray-500 dark:text-gray-400">April Statement.pdf</span>
                    </div>
                    <span className="text-[10px] text-green-600 font-medium">Valid</span>
                  </div>
                  <div className="flex items-center justify-between py-1.5 border-b border-gray-100 dark:border-gray-800">
                    <span className="text-[10px] text-gray-400">Bank detected</span>
                    <span className="text-[10px] text-gray-700 dark:text-gray-300 font-medium">HDFC Bank</span>
                  </div>
                  <div className="flex items-center justify-between py-1.5">
                    <span className="text-[10px] text-gray-400">Transactions</span>
                    <span className="text-[10px] text-gray-700 dark:text-gray-300 font-medium">24 found</span>
                  </div>
                </div>
              </div>
            </BrowserFrame>

            <BrowserFrame label="Settings">
              <div className="p-4 space-y-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-400 to-purple-400 flex items-center justify-center text-white text-sm font-bold">
                    K
                  </div>
                  <div>
                    <div className="h-3 w-24 bg-gray-200 dark:bg-gray-700 rounded" />
                    <div className="h-2.5 w-32 bg-gray-100 dark:bg-gray-800 rounded mt-1" />
                  </div>
                </div>
                {[
                  { label: "Full Name", value: "Kabyik Paul" },
                  { label: "Email", value: "kabyik@email.com" },
                  { label: "Currency", value: "INR" },
                ].map((f) => (
                  <div key={f.label} className="p-2.5 rounded-lg bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-800">
                    <p className="text-[10px] text-gray-400 dark:text-gray-500">{f.label}</p>
                    <p className="text-xs font-medium text-gray-700 dark:text-gray-300 mt-0.5">{f.value}</p>
                  </div>
                ))}
                <div className="h-7 w-full rounded-lg bg-gray-200 dark:bg-gray-700" />
              </div>
            </BrowserFrame>
          </div>

          <div className="lg:col-span-1">
            <BrowserFrame label="Budgets">
              <div className="p-4 space-y-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] text-gray-400 dark:text-gray-500 uppercase tracking-wider font-semibold">Monthly Budgets</span>
                  <span className="text-[10px] text-green-500 font-medium">₹21K left</span>
                </div>
                {[
                  { label: "Food & Dining", spent: 82, color: "bg-orange-500" },
                  { label: "Transportation", spent: 45, color: "bg-blue-500" },
                  { label: "Entertainment", spent: 90, color: "bg-red-500" },
                  { label: "Shopping", spent: 30, color: "bg-purple-500" },
                ].map((b) => (
                  <div key={b.label}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[10px] text-gray-500 dark:text-gray-400">{b.label}</span>
                      <span className={`text-[10px] font-medium ${b.spent >= 80 ? "text-red-500" : "text-gray-400"}`}>{b.spent}%</span>
                    </div>
                    <div className="w-full h-1.5 rounded-full bg-gray-100 dark:bg-gray-800 overflow-hidden">
                      <div className={`h-full rounded-full ${b.color} transition-all`} style={{ width: `${b.spent}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </BrowserFrame>
          </div>
        </div>
      </div>
    </section>
  );
}
