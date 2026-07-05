import { Link } from "react-router-dom";
import { FiTrendingUp, FiTrendingDown, FiDollarSign } from "react-icons/fi";

export default function Hero() {
  return (
    <section className="relative min-h-screen flex items-center overflow-hidden bg-white dark:bg-gray-950">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-[500px] h-[500px] rounded-full bg-gradient-to-br from-indigo-400/20 to-purple-400/20 dark:from-indigo-500/10 dark:to-purple-500/10 blur-3xl animate-pulse-slow" />
        <div className="absolute -bottom-40 -left-40 w-[600px] h-[600px] rounded-full bg-gradient-to-tr from-cyan-400/20 to-indigo-400/20 dark:from-cyan-500/10 dark:to-indigo-500/10 blur-3xl animate-pulse-slow animation-delay-2000" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] rounded-full bg-gradient-to-r from-violet-400/10 to-fuchsia-400/10 dark:from-violet-500/5 dark:to-fuchsia-500/5 blur-3xl animate-spin-slow" />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-0">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          <div className="relative">
            <div className="relative p-6 sm:p-8 lg:p-10 rounded-2xl bg-white/70 dark:bg-gray-900/70 backdrop-blur-2xl border border-white/40 dark:border-gray-700/30 shadow-xl shadow-black/5">
              <div className="text-center lg:text-left">
                <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-indigo-50 dark:bg-indigo-900/30 border border-indigo-200/50 dark:border-indigo-700/50 text-indigo-700 dark:text-indigo-300 text-sm font-medium mb-8 animate-fade-in">
                  <span className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse" />
                  Built with React + Flask + DSA
                </div>

                <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-gray-900 dark:text-white leading-[1.1]">
                  Track Every{" "}
                  <span className="text-indigo-600 dark:text-indigo-400">Rupee</span>.
                  <br />
                  Analyze Every{" "}
                  <span className="text-indigo-600 dark:text-indigo-400">Expense</span>.
                  <br />
                  <span className="bg-gradient-to-r from-indigo-600 to-purple-600 dark:from-indigo-400 dark:to-purple-400 bg-clip-text text-transparent">
                    Powered by Smart DSA.
                  </span>
                </h1>

                <p className="mt-6 text-lg text-gray-600 dark:text-gray-400 max-w-xl mx-auto lg:mx-0 leading-relaxed">
                  A production-ready full-stack expense tracker with intelligent
                  searching, advanced analytics, secure authentication,
                  AI-powered transaction import and
                  algorithm-driven performance.
                </p>

                <div className="mt-8 flex flex-col sm:flex-row items-center gap-4 justify-center lg:justify-start">
                  <Link
                    to="/register"
                    className="w-full sm:w-auto px-8 py-3 bg-indigo-600 text-white font-semibold rounded-xl hover:bg-indigo-700 transition-all duration-200 shadow-lg shadow-indigo-600/25 hover:shadow-indigo-600/40 text-center"
                  >
                    Get Started
                  </Link>
                  <Link
                    to="/login"
                    className="w-full sm:w-auto px-8 py-3 text-gray-700 dark:text-gray-300 font-semibold rounded-xl border border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500 hover:bg-gray-50 dark:hover:bg-gray-800 transition-all duration-200 text-center"
                  >
                    Login
                  </Link>
                </div>

                <div className="mt-10 flex items-center gap-8 justify-center lg:justify-start text-sm text-gray-500 dark:text-gray-400">
                  <div className="flex items-center gap-2">
                    <div className="w-5 h-5 rounded-full bg-green-100 dark:bg-green-900/50 flex items-center justify-center">
                      <svg className="w-3 h-3 text-green-600 dark:text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    Free to use
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-5 h-5 rounded-full bg-green-100 dark:bg-green-900/50 flex items-center justify-center">
                      <svg className="w-3 h-3 text-green-600 dark:text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    No credit card
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-5 h-5 rounded-full bg-green-100 dark:bg-green-900/50 flex items-center justify-center">
                      <svg className="w-3 h-3 text-green-600 dark:text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    Open source
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="relative hidden lg:block">
            <div className="relative w-full aspect-[4/3]">
              <div className="absolute top-[8%] left-[5%] w-[72%] p-5 rounded-2xl bg-white/70 dark:bg-gray-900/70 backdrop-blur-xl border border-white/30 dark:border-gray-700/30 shadow-xl animate-float" style={{ animationDelay: "0s" }}>
                <div className="flex items-center justify-between mb-4">
                  <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Today's Spending</span>
                  <span className="text-xs text-red-500 font-medium flex items-center gap-1">
                    <FiTrendingDown className="w-3 h-3" />
                    +12.3%
                  </span>
                </div>
                <div className="flex items-baseline gap-1">
                  <span className="text-2xl font-bold text-gray-900 dark:text-white">₹</span>
                  <span className="text-3xl font-bold text-gray-900 dark:text-white">1,847</span>
                  <span className="text-sm text-gray-400 dark:text-gray-500 ml-1">today</span>
                </div>
                <div className="mt-4 flex gap-2">
                  {["Food", "Transport", "Shopping"].map((tag) => (
                    <span key={tag} className="px-2.5 py-1 text-xs font-medium rounded-full bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>

              <div className="absolute top-[5%] right-[5%] w-[32%] p-4 rounded-2xl bg-white/70 dark:bg-gray-900/70 backdrop-blur-xl border border-white/30 dark:border-gray-700/30 shadow-xl animate-float" style={{ animationDelay: "1s" }}>
                <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Balance</span>
                <div className="flex items-baseline gap-1 mt-2">
                  <span className="text-lg font-bold text-gray-900 dark:text-white">₹</span>
                  <span className="text-xl font-bold text-green-600 dark:text-green-400">12,430</span>
                </div>
                <div className="mt-3 w-full h-1.5 rounded-full bg-gray-200 dark:bg-gray-700 overflow-hidden">
                  <div className="w-3/5 h-full rounded-full bg-gradient-to-r from-indigo-500 to-purple-500" />
                </div>
                <span className="text-[10px] text-gray-400 dark:text-gray-500 mt-1 block">60% of monthly budget</span>
              </div>

              <div className="absolute bottom-[18%] left-[8%] w-[36%] p-4 rounded-2xl bg-white/70 dark:bg-gray-900/70 backdrop-blur-xl border border-white/30 dark:border-gray-700/30 shadow-xl animate-float" style={{ animationDelay: "2s" }}>
                <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Top Category</span>
                <div className="flex items-center gap-2 mt-2">
                  <div className="w-8 h-8 rounded-lg bg-orange-100 dark:bg-orange-900/40 flex items-center justify-center">
                    <svg className="w-4 h-4 text-orange-600 dark:text-orange-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-900 dark:text-white">Food & Dining</p>
                    <p className="text-xs text-gray-400 dark:text-gray-500">42% of expenses</p>
                  </div>
                </div>
                <div className="mt-3 w-full h-1.5 rounded-full bg-gray-200 dark:bg-gray-700 overflow-hidden">
                  <div className="w-[42%] h-full rounded-full bg-orange-500" />
                </div>
              </div>

              <div className="absolute bottom-[8%] right-[8%] w-[40%] p-4 rounded-2xl bg-indigo-600/90 backdrop-blur-xl border border-indigo-400/30 shadow-xl animate-float" style={{ animationDelay: "0.5s" }}>
                <div className="flex items-center gap-2">
                  <FiTrendingUp className="w-4 h-4 text-indigo-200" />
                  <span className="text-xs font-semibold text-indigo-200 uppercase tracking-wider">Savings Rate</span>
                </div>
                <p className="text-2xl font-bold text-white mt-1">24.5%</p>
                <p className="text-xs text-indigo-200 mt-0.5">of income saved this month</p>
              </div>

              <div className="absolute bottom-[32%] right-[12%] w-[20%] p-3 rounded-xl bg-white/70 dark:bg-gray-900/70 backdrop-blur-xl border border-white/30 dark:border-gray-700/30 shadow-xl animate-float flex items-center gap-2" style={{ animationDelay: "1.5s" }}>
                <div className="w-7 h-7 rounded-lg bg-green-100 dark:bg-green-900/40 flex items-center justify-center">
                  <FiDollarSign className="w-4 h-4 text-green-600 dark:text-green-400" />
                </div>
                <div>
                  <p className="text-xs text-gray-400 dark:text-gray-500">Income</p>
                  <p className="text-sm font-bold text-gray-900 dark:text-white">₹64K</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes hero-float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-8px); }
        }
        @keyframes hero-pulse-slow {
          0%, 100% { opacity: 0.6; transform: scale(1); }
          50% { opacity: 1; transform: scale(1.05); }
        }
        @keyframes hero-spin-slow {
          from { transform: translate(-50%, -50%) rotate(0deg); }
          to { transform: translate(-50%, -50%) rotate(360deg); }
        }
        .animate-float { animation: hero-float 4s ease-in-out infinite; }
        .animate-pulse-slow { animation: hero-pulse-slow 6s ease-in-out infinite; }
        .animate-spin-slow { animation: hero-spin-slow 20s linear infinite; }
        .animation-delay-2000 { animation-delay: 2s; }
      `}</style>
    </section>
  );
}
