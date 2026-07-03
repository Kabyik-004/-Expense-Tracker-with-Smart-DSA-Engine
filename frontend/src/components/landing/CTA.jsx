import { Link } from "react-router-dom";
import { FiArrowRight } from "react-icons/fi";

export default function CTA() {
  return (
    <section className="relative py-24 lg:py-32 bg-white dark:bg-gray-950 overflow-hidden">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-indigo-600 via-indigo-700 to-purple-800 dark:from-indigo-500 dark:via-indigo-600 dark:to-purple-700">
          <div className="absolute inset-0 pointer-events-none">
            <div className="absolute -top-20 -right-20 w-64 h-64 rounded-full bg-white/10 blur-3xl animate-pulse-slow" />
            <div className="absolute -bottom-20 -left-20 w-80 h-80 rounded-full bg-purple-300/20 blur-3xl animate-pulse-slow" style={{ animationDelay: "2s" }} />
            <div className="absolute top-1/2 left-1/3 w-40 h-40 rounded-full bg-white/5 blur-2xl animate-float" />
            <div className="absolute top-1/4 right-1/4 w-20 h-20 rounded-full bg-white/10 blur-xl animate-float" style={{ animationDelay: "1s" }} />
            <div className="absolute bottom-1/3 left-1/4 w-16 h-16 rounded-lg bg-white/5 blur-lg animate-float" style={{ animationDelay: "1.5s" }} />
          </div>

          <div className="relative z-10 px-8 py-16 sm:px-16 sm:py-24 lg:px-24 text-center">
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white tracking-tight leading-[1.15]">
              Ready to Take Control of
              <br />
              <span className="text-indigo-200">Your Finances?</span>
            </h2>

            <p className="mt-5 text-lg text-indigo-200/90 max-w-xl mx-auto leading-relaxed">
              Join thousands of users who trust the Smart DSA Engine to track,
              analyze and optimize their expenses.
            </p>

            <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                to="/register"
                className="inline-flex items-center gap-2 px-8 py-3.5 bg-white text-indigo-700 font-semibold rounded-xl hover:bg-indigo-50 transition-all duration-200 shadow-lg shadow-black/10 hover:shadow-xl hover:-translate-y-0.5"
              >
                Create Account
                <FiArrowRight className="w-4 h-4" />
              </Link>
              <Link
                to="/login"
                className="inline-flex items-center gap-2 px-8 py-3.5 border-2 border-white/30 text-white font-semibold rounded-xl hover:bg-white/10 transition-all duration-200 hover:border-white/50"
              >
                Login
              </Link>
            </div>

            <p className="mt-6 text-sm text-indigo-200/70">
              Free to use. No credit card required.
            </p>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes cta-float {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-12px) rotate(3deg); }
        }
        @keyframes cta-pulse-slow {
          0%, 100% { opacity: 0.4; transform: scale(1); }
          50% { opacity: 0.8; transform: scale(1.1); }
        }
        .animate-float { animation: cta-float 5s ease-in-out infinite; }
        .animate-pulse-slow { animation: cta-pulse-slow 6s ease-in-out infinite; }
      `}</style>
    </section>
  );
}
