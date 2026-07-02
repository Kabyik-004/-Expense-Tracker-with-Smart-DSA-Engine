import api from "./api";
import { API_PATHS } from "../utils/constants";

export async function getExpenses(params = {}) {
  const query = new URLSearchParams();
  if (params.limit) query.set("limit", params.limit);
  if (params.offset) query.set("offset", params.offset);
  if (params.sort_by) query.set("sort_by", params.sort_by);
  if (params.sort_order) query.set("sort_order", params.sort_order);
  const qs = query.toString();
  const res = await api.get(`${API_PATHS.expenses.base}${qs ? `?${qs}` : ""}`);
  return res.data;
}

export async function getExpense(id) {
  const res = await api.get(`${API_PATHS.expenses.base}/${id}`);
  return res.data;
}

export async function createExpense(data) {
  const res = await api.post(API_PATHS.expenses.base, data);
  return res.data;
}

export async function updateExpense(id, data) {
  const res = await api.put(`${API_PATHS.expenses.base}/${id}`, data);
  return res.data;
}

export async function deleteExpense(id) {
  const res = await api.delete(`${API_PATHS.expenses.base}/${id}`);
  return res.data;
}

export async function searchExpensesByTitle(query) {
  const res = await api.get(`${API_PATHS.expenses.search.title}?q=${encodeURIComponent(query)}`);
  return res.data;
}

export async function searchExpensesByDescription(query) {
  const res = await api.get(`${API_PATHS.expenses.search.description}?q=${encodeURIComponent(query)}`);
  return res.data;
}

export async function searchExpensesByCategory(categoryId) {
  const res = await api.get(`${API_PATHS.expenses.search.category}?category_id=${categoryId}`);
  return res.data;
}

export async function searchExpensesByDate(date) {
  const res = await api.get(`${API_PATHS.expenses.search.date}?date=${date}`);
  return res.data;
}

export async function searchExpensesByDateRange(startDate, endDate) {
  const res = await api.get(`${API_PATHS.expenses.search.dateRange}?start_date=${startDate}&end_date=${endDate}`);
  return res.data;
}

export async function searchExpenseById(expenseId) {
  const res = await api.get(`${API_PATHS.expenses.search.id}?expense_id=${expenseId}`);
  return res.data;
}

export async function sortExpenses(field, ascending = true) {
  const res = await api.get(`${API_PATHS.expenses.sort.single}?sort_by=${field}&ascending=${ascending}`);
  return res.data;
}

export async function getCategoryTotals() {
  const res = await api.get(API_PATHS.expenses.summaries.categoryTotals);
  return res.data;
}

export async function getMonthlyTotals() {
  const res = await api.get(API_PATHS.expenses.summaries.monthlyTotals);
  return res.data;
}

export async function undoExpense() {
  const res = await api.post(API_PATHS.expenses.undo);
  return res.data;
}

export async function getUndoStatus() {
  const res = await api.get(API_PATHS.expenses.undoStatus);
  return res.data;
}

export async function clearUndo() {
  const res = await api.post(API_PATHS.expenses.undoClear);
  return res.data;
}

export async function getIncomes() {
  const res = await api.get(API_PATHS.incomes.base);
  return res.data;
}

export async function createIncome(data) {
  const res = await api.post(API_PATHS.incomes.base, data);
  return res.data;
}

export async function updateIncome(id, data) {
  const res = await api.put(`${API_PATHS.incomes.base}${id}/`, data);
  return res.data;
}

export async function deleteIncome(id) {
  const res = await api.delete(`${API_PATHS.incomes.base}${id}/`);
  return res.data;
}

export async function undoIncome() {
  const res = await api.post(API_PATHS.incomes.undo);
  return res.data;
}