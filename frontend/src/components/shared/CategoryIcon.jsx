import {
  FiCoffee,
  FiShoppingBag,
  FiBriefcase,
  FiMapPin,
  FiFilm,
  FiFileText,
  FiHeart,
  FiBook,
  FiTruck,
  FiTag,
} from "react-icons/fi";

const categories = [
  {
    keys: ["food", "dining", "restaurant", "grocery", "eat", "lunch", "dinner", "breakfast", "cafe", "snack", "drink"],
    icon: FiCoffee,
    bg: "bg-orange-100 dark:bg-orange-900/40",
    color: "text-orange-600 dark:text-orange-400",
  },
  {
    keys: ["shop", "retail", "cloth", "apparel", "accessory", "gadget", "electronics", "amazon", "flipkart"],
    icon: FiShoppingBag,
    bg: "bg-pink-100 dark:bg-pink-900/40",
    color: "text-pink-600 dark:text-pink-400",
  },
  {
    keys: ["salary", "wage", "income", "paycheck", "earning", "bonus", "stipend", "freelance"],
    icon: FiBriefcase,
    bg: "bg-green-100 dark:bg-green-900/40",
    color: "text-green-600 dark:text-green-400",
  },
  {
    keys: ["travel", "hotel", "flight", "vacation", "trip", "holiday", "tour", "journey", "lodging"],
    icon: FiMapPin,
    bg: "bg-sky-100 dark:bg-sky-900/40",
    color: "text-sky-600 dark:text-sky-400",
  },
  {
    keys: ["entertain", "movie", "game", "fun", "cinema", "netflix", "spotify", "music", "concert", "subscription"],
    icon: FiFilm,
    bg: "bg-emerald-100 dark:bg-emerald-900/40",
    color: "text-emerald-600 dark:text-emerald-400",
  },
  {
    keys: ["bill", "util", "electricity", "water", "gas", "internet", "phone", "rent", "maintenance", "insurance"],
    icon: FiFileText,
    bg: "bg-red-100 dark:bg-red-900/40",
    color: "text-red-600 dark:text-red-400",
  },
  {
    keys: ["health", "medical", "doctor", "gym", "fitness", "hospital", "pharmacy", "medicine", "dental", "wellness"],
    icon: FiHeart,
    bg: "bg-rose-100 dark:bg-rose-900/40",
    color: "text-rose-600 dark:text-rose-400",
  },
  {
    keys: ["edu", "course", "school", "learn", "training", "class", "book", "university", "college", "tution"],
    icon: FiBook,
    bg: "bg-blue-100 dark:bg-blue-900/40",
    color: "text-blue-600 dark:text-blue-400",
  },
  {
    keys: ["transport", "fuel", "gas", "car", "uber", "lyft", "bus", "train", "metro", "auto", "parking", "petrol", "diesel"],
    icon: FiTruck,
    bg: "bg-amber-100 dark:bg-amber-900/40",
    color: "text-amber-600 dark:text-amber-400",
  },
];

const defaultConfig = { icon: FiTag, bg: "bg-gray-100 dark:bg-gray-700", color: "text-gray-500 dark:text-gray-400" };

function findConfig(name) {
  if (!name) return defaultConfig;
  const lower = name.toLowerCase().trim();
  for (const cat of categories) {
    if (cat.keys.some((k) => lower.includes(k))) return cat;
  }
  return defaultConfig;
}

export default function CategoryIcon({ name, size = "md", className = "" }) {
  const config = findConfig(name);
  const Icon = config.icon;

  const sizeMap = {
    sm: { container: "w-7 h-7", icon: "w-3.5 h-3.5" },
    md: { container: "w-9 h-9", icon: "w-4 h-4" },
    lg: { container: "w-12 h-12", icon: "w-6 h-6" },
  };

  const s = sizeMap[size] || sizeMap.md;

  return (
    <div
      className={`rounded-full flex items-center justify-center shrink-0 transition-all duration-300 hover:scale-110 hover:shadow-md active:scale-95 ${config.bg} ${s.container} ${className}`}
    >
      <Icon className={`transition-transform duration-300 hover:rotate-[8deg] ${config.color} ${s.icon}`} />
    </div>
  );
}
