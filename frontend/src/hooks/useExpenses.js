import { useContext } from "react";
import { ExpenseContext } from "../context/ExpenseContext";

export function useExpenses() {
  const ctx = useContext(ExpenseContext);
  if (!ctx) throw new Error("useExpenses must be used within ExpenseProvider");
  return ctx;
}
