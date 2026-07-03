import { createContext, useState, useCallback } from "react";
import * as expenseService from "../services/expenseService";

export const ExpenseContext = createContext(null);

const ITEMS_PER_PAGE = 10;

export function ExpenseProvider({ children }) {
  const [expenses, setExpenses] = useState([]);
  const [filteredExpenses, setFilteredExpenses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [categories, setCategories] = useState([]);

  const [searchMode, setSearchMode] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchField, setSearchField] = useState("title");

  const [sortField, setSortField] = useState("date");
  const [sortAscending, setSortAscending] = useState(false);

  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [undoStackSize, setUndoStackSize] = useState(0);

  const fetchExpenses = useCallback(async () => {
    setLoading(true);
    setSearchMode(false);
    setSearchQuery("");
    try {
      const res = await expenseService.getExpenses();
      if (res.success) {
        const sorted = sortExpensesList(res.data.expenses, sortField, sortAscending);
        setExpenses(sorted);
        setFilteredExpenses(sorted);
        setTotalPages(Math.ceil(sorted.length / ITEMS_PER_PAGE) || 1);
        setPage(1);
        setCategories(res.data.categories || []);
      }
    } catch {
    } finally {
      setLoading(false);
    }
  }, [sortField, sortAscending]);

  const fetchUndoStatus = useCallback(async () => {
    try {
      const res = await expenseService.getUndoStatus();
      if (res.success) setUndoStackSize(res.data.stack_size || 0);
    } catch {}
  }, []);

  const fetchCategories = useCallback(async () => {
    try {
      const res = await expenseService.getExpenses({ limit: 1 });
      if (res.success && res.data.categories) {
        setCategories(res.data.categories);
      }
    } catch {}
  }, []);

  const addExpense = useCallback(async (data) => {
    const res = await expenseService.createExpense(data);
    if (res.success) {
      const updated = [res.data.expense, ...expenses];
      const sorted = sortExpensesList(updated, sortField, sortAscending);
      setExpenses(sorted);
      setFilteredExpenses(sorted);
      setTotalPages(Math.ceil(sorted.length / ITEMS_PER_PAGE) || 1);
      await fetchUndoStatus();
    }
    return res;
  }, [expenses, sortField, sortAscending, fetchUndoStatus]);

  const editExpense = useCallback(async (id, data) => {
    const res = await expenseService.updateExpense(id, data);
    if (res.success) {
      const updated = expenses.map((e) => (e.id === id ? res.data.expense : e));
      const sorted = sortExpensesList(updated, sortField, sortAscending);
      setExpenses(sorted);
      setFilteredExpenses(sorted);
      await fetchUndoStatus();
    }
    return res;
  }, [expenses, sortField, sortAscending, fetchUndoStatus]);

  const removeExpense = useCallback(async (id) => {
    const res = await expenseService.deleteExpense(id);
    if (res.success) {
      const updated = expenses.filter((e) => e.id !== id);
      setExpenses(updated);
      setFilteredExpenses(updated);
      setTotalPages(Math.ceil(updated.length / ITEMS_PER_PAGE) || 1);
      await fetchUndoStatus();
    }
    return res;
  }, [expenses, fetchUndoStatus]);

  const undoLastExpense = useCallback(async () => {
    const res = await expenseService.undoExpense();
    if (res.success) {
      await fetchExpenses();
      await fetchUndoStatus();
    }
    return res;
  }, [fetchExpenses, fetchUndoStatus]);

  const handleSearch = useCallback(async (query, field) => {
    if (!query.trim()) {
      setSearchMode(false);
      setFilteredExpenses(expenses);
      setTotalPages(Math.ceil(expenses.length / ITEMS_PER_PAGE) || 1);
      setPage(1);
      return;
    }
    setLoading(true);
    setSearchQuery(query);
    setSearchField(field);
    try {
      let res;
      switch (field) {
        case "title":
          res = await expenseService.searchExpensesByTitle(query);
          break;
        case "description":
          res = await expenseService.searchExpensesByDescription(query);
          break;
        case "date":
          res = await expenseService.searchExpensesByDate(query);
          break;
        case "category":
          res = await expenseService.searchExpensesByCategory(parseInt(query));
          break;
        case "id":
          res = await expenseService.searchExpenseById(parseInt(query));
          break;
        default:
          res = await expenseService.searchExpensesByTitle(query);
      }
      if (res.success) {
        const results = res.data?.expenses || res.data?.results || [];
        setFilteredExpenses(results);
        setTotalPages(Math.ceil(results.length / ITEMS_PER_PAGE) || 1);
        setPage(1);
        setSearchMode(true);
      }
    } catch {
    } finally {
      setLoading(false);
    }
  }, [expenses]);

  const handleSort = useCallback((field) => {
    const ascending = sortField === field ? !sortAscending : field === "amount" || field === "id";
    setSortField(field);
    setSortAscending(ascending);
    const sorted = sortExpensesList([...expenses], field, ascending);
    setExpenses(sorted);
    setFilteredExpenses(sorted);
  }, [expenses, sortField, sortAscending]);

  const paginatedExpenses = filteredExpenses.slice(
    (page - 1) * ITEMS_PER_PAGE,
    page * ITEMS_PER_PAGE
  );

  return (
    <ExpenseContext.Provider
      value={{
        expenses: paginatedExpenses,
        allExpenses: expenses,
        filteredExpenses,
        loading,
        page,
        totalPages,
        setPage,
        sortField,
        sortAscending,
        searchMode,
        searchQuery,
        searchField,
        undoStackSize,
        categories,
        fetchExpenses,
        fetchCategories,
        addExpense,
        editExpense,
        removeExpense,
        undoLastExpense,
        fetchUndoStatus,
        handleSearch,
        handleSort,
        ITEMS_PER_PAGE,
      }}
    >
      {children}
    </ExpenseContext.Provider>
  );
}

function sortExpensesList(list, field, ascending) {
  const sorted = [...list].sort((a, b) => {
    let valA = a[field];
    let valB = b[field];
    if (field === "amount") {
      valA = parseFloat(valA) || 0;
      valB = parseFloat(valB) || 0;
    } else if (field === "date") {
      valA = valA || "";
      valB = valB || "";
    } else {
      valA = (valA || "").toString().toLowerCase();
      valB = (valB || "").toString().toLowerCase();
    }
    if (valA < valB) return ascending ? -1 : 1;
    if (valA > valB) return ascending ? 1 : -1;
    return 0;
  });
  return sorted;
}