import { FiPackage } from "react-icons/fi";
import {
  SiReact,
  SiVite,
  SiTailwindcss,
  SiFlask,
  SiSqlalchemy,
  SiJsonwebtokens,
  SiPostgresql,
  SiGunicorn,
  SiDocker,
  SiRender,
  SiVercel,
  SiGithub,
} from "react-icons/si";

const techs = [
  {
    icon: SiReact,
    name: "React",
    description: "Component-based UI library for building interactive interfaces.",
    color: "text-sky-500",
    bg: "bg-sky-100 dark:bg-sky-900/30",
  },
  {
    icon: SiVite,
    name: "Vite",
    description: "Lightning-fast build tool for modern web development workflows.",
    color: "text-emerald-500",
    bg: "bg-emerald-100 dark:bg-emerald-900/30",
  },
  {
    icon: SiTailwindcss,
    name: "Tailwind CSS",
    description: "Utility-first CSS framework for rapid and consistent UI design.",
    color: "text-cyan-500",
    bg: "bg-cyan-100 dark:bg-cyan-900/30",
  },
  {
    icon: SiFlask,
    name: "Flask",
    description: "Lightweight Python web framework powering the REST API layer.",
    color: "text-gray-700 dark:text-gray-300",
    bg: "bg-gray-100 dark:bg-gray-700/50",
  },
  {
    icon: SiSqlalchemy,
    name: "SQLAlchemy",
    description: "SQL toolkit and ORM for expressive database interactions.",
    color: "text-red-500",
    bg: "bg-red-100 dark:bg-red-900/30",
  },
  {
    icon: FiPackage,
    name: "Marshmallow",
    description: "Object serialization and validation for consistent API payloads.",
    color: "text-amber-500",
    bg: "bg-amber-100 dark:bg-amber-900/30",
  },
  {
    icon: SiJsonwebtokens,
    name: "JWT",
    description: "Secure token-based authentication with access and refresh tokens.",
    color: "text-pink-500",
    bg: "bg-pink-100 dark:bg-pink-900/30",
  },
  {
    icon: SiPostgresql,
    name: "PostgreSQL",
    description: "Production-grade relational database with ACID compliance.",
    color: "text-blue-600",
    bg: "bg-blue-100 dark:bg-blue-900/30",
  },
  {
    icon: SiGunicorn,
    name: "Gunicorn",
    description: "WSGI server for running Python applications in production.",
    color: "text-emerald-600",
    bg: "bg-emerald-100 dark:bg-emerald-900/30",
  },
  {
    icon: SiDocker,
    name: "Docker",
    description: "Containerization platform ensuring consistent deployments.",
    color: "text-blue-500",
    bg: "bg-blue-100 dark:bg-blue-900/30",
  },
  {
    icon: SiRender,
    name: "Render",
    description: "Cloud platform hosting the backend API and PostgreSQL database.",
    color: "text-emerald-500",
    bg: "bg-emerald-100 dark:bg-emerald-900/30",
  },
  {
    icon: SiVercel,
    name: "Vercel",
    description: "Edge network platform for frontend deployment and hosting.",
    color: "text-gray-900 dark:text-white",
    bg: "bg-gray-100 dark:bg-gray-700/50",
  },
  {
    icon: SiGithub,
    name: "GitHub",
    description: "Version control and collaboration platform for the codebase.",
    color: "text-gray-900 dark:text-white",
    bg: "bg-gray-100 dark:bg-gray-700/50",
  },
];

export default function TechStack() {
  return (
    <section id="tech-stack" className="relative py-24 lg:py-32 bg-white dark:bg-gray-950">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <p className="text-emerald-600 dark:text-emerald-400 font-semibold text-sm tracking-wide uppercase mb-3">
            Tech Stack
          </p>
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white tracking-tight">
            Built with{" "}
            <span className="text-emerald-600 dark:text-emerald-400">Modern</span>{" "}
            Technologies
          </h2>
          <p className="mt-4 text-lg text-gray-600 dark:text-gray-400">
            A carefully chosen stack that balances performance, developer
            experience and production reliability.
          </p>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {techs.map((tech) => (
            <article
              key={tech.name}
              className="group relative bg-gray-50 dark:bg-gray-900/50 rounded-xl border border-gray-100 dark:border-gray-800 p-5 transition-all duration-300 hover:-translate-y-1 hover:shadow-lg"
            >
              <div
                className={`w-10 h-10 rounded-lg ${tech.bg} flex items-center justify-center mb-3 transition-all duration-300 group-hover:scale-110 group-hover:shadow-md`}
              >
                <tech.icon className={`w-5 h-5 ${tech.color}`} />
              </div>
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-1">
                {tech.name}
              </h3>
              <p className="text-xs text-gray-500 dark:text-gray-400 leading-relaxed">
                {tech.description}
              </p>

              <div className="absolute inset-x-4 bottom-0 h-0.5 bg-gradient-to-r from-emerald-500 to-emerald-500 scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left rounded-full" />
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
