import { FiFile, FiCheckCircle } from "react-icons/fi";

const BANKS = [
  {
    id: "hdfc", name: "HDFC Bank",
    gradient: "from-blue-600 to-blue-800",
    formats: ["CSV"],
    color: "blue",
  },
  {
    id: "icici", name: "ICICI Bank",
    gradient: "from-orange-500 to-red-600",
    formats: ["CSV"],
    color: "orange",
  },
  {
    id: "sbi", name: "State Bank of India",
    gradient: "from-sky-600 to-blue-700",
    formats: ["CSV"],
    color: "sky",
  },
  {
    id: "axis", name: "Axis Bank",
    gradient: "from-red-600 to-rose-700",
    formats: ["CSV"],
    color: "red",
  },
  {
    id: "kotak", name: "Kotak Mahindra Bank",
    gradient: "from-purple-600 to-violet-700",
    formats: ["CSV"],
    color: "purple",
  },
  {
    id: "yes", name: "Yes Bank",
    gradient: "from-rose-500 to-pink-600",
    formats: ["CSV"],
    color: "pink",
  },
];

export default function SupportedBanks() {
  return (
    <section className="w-full">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-8 h-8 rounded-xl bg-indigo-100 dark:bg-indigo-900/40 flex items-center justify-center">
          <FiCheckCircle className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Supported Banks
        </h3>
        <span className="px-2.5 py-0.5 text-[11px] font-bold bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300 rounded-full tracking-wide uppercase">
          {BANKS.length} Banks
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {BANKS.map((bank) => (
          <div
            key={bank.id}
            className="group relative overflow-hidden rounded-2xl border border-gray-200/50 dark:border-gray-700/40 bg-white/50 dark:bg-gray-900/40 backdrop-blur-xl p-5 transition-all duration-300 hover:shadow-xl hover:shadow-indigo-500/5 hover:border-indigo-200/60 dark:hover:border-indigo-600/30 card-hover"
          >
            {/* Gradient accent bar */}
            <div className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r ${bank.gradient} opacity-80`} />

            <div className="flex items-start gap-4 mt-1">
              {/* Bank icon circle */}
              <div className={`w-12 h-12 rounded-2xl bg-gradient-to-br ${bank.gradient} flex items-center justify-center shadow-lg shrink-0 text-white font-bold text-lg tracking-tight`}>
                {bank.name.split(" ").map((w) => w[0]).join("").slice(0, 2)}
              </div>

              <div className="min-w-0 flex-1">
                <h4 className="font-semibold text-gray-900 dark:text-white text-sm leading-tight">
                  {bank.name}
                </h4>
                <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">
                  Statement import
                </p>

                {/* Format tags */}
                <div className="flex flex-wrap gap-1.5 mt-2.5">
                  {bank.formats.map((fmt) => (
                    <span
                      key={fmt}
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-gray-100 dark:bg-gray-800/60 text-gray-600 dark:text-gray-300 border border-gray-200/50 dark:border-gray-700/30"
                    >
                      <FiFile className="w-3 h-3" />
                      {fmt}
                    </span>
                  ))}
                </div>
              </div>

              {/* Status dot */}
              <div className="shrink-0 mt-1">
                <span className="block w-2 h-2 rounded-full bg-emerald-400 shadow-sm shadow-emerald-400/50" />
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
