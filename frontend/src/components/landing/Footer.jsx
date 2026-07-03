import { FiMail, FiHeart } from "react-icons/fi";
import { FaLinkedin } from "react-icons/fa";
import { SiGithub } from "react-icons/si";

const links = [
  {
    href: "https://github.com/kabyikpaul",
    icon: SiGithub,
    label: "GitHub",
  },
  {
    href: "https://linkedin.com/in/kabyikpaul",
    icon: FaLinkedin,
    label: "LinkedIn",
  },
  {
    href: "mailto:kabyik@email.com",
    icon: FiMail,
    label: "Email",
  },
];

export default function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer id="about" className="bg-white dark:bg-gray-950 border-t border-gray-100 dark:border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-16">
        <div className="flex flex-col md:flex-row items-center justify-between gap-8">
          <div className="text-center md:text-left">
            <div className="flex items-center justify-center md:justify-start gap-2 mb-2">
              <div className="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center">
                <span className="text-white font-bold text-[10px]">ET</span>
              </div>
              <span className="text-base font-semibold text-gray-900 dark:text-white">
                Expense Tracker
              </span>
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400 max-w-xs">
              A full-stack expense tracking application powered by Data
              Structures & Algorithms.
            </p>
          </div>

          <div className="flex items-center gap-6">
            {links.map((link) => (
              <a
                key={link.label}
                href={link.href}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors duration-200 group"
                aria-label={link.label}
              >
                <link.icon className="w-4 h-4 transition-transform duration-200 group-hover:scale-110" />
                <span className="hidden sm:inline">{link.label}</span>
              </a>
            ))}
          </div>
        </div>

        <div className="mt-10 pt-6 border-t border-gray-100 dark:border-gray-800 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-gray-400 dark:text-gray-500">
            &copy; {year} Expense Tracker. All rights reserved.
          </p>
          <p className="text-xs text-gray-400 dark:text-gray-500 flex items-center gap-1">
            Made with{" "}
            <FiHeart className="w-3 h-3 text-red-500 fill-red-500" /> by{" "}
            <a
              href="https://github.com/kabyikpaul"
              target="_blank"
              rel="noopener noreferrer"
              className="font-medium text-gray-600 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
            >
              Kabyik Paul
            </a>
          </p>
        </div>
      </div>
    </footer>
  );
}
