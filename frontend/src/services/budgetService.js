import api from "./api";
import { API_PATHS } from "../utils/constants";

export async function getBudgets() {
  const res = await api.get(API_PATHS.budgets.base);
  return res.data;
}

export async function getBudgetStatus(month, year) {
  const params = {};
  if (month) params.month = month;
  if (year) params.year = year;
  const res = await api.get(API_PATHS.budgets.status, { params });
  return res.data;
}

export async function setBudget(data) {
  const res = await api.post(API_PATHS.budgets.base, data);
  return res.data;
}

export async function deleteBudget(id) {
  const res = await api.delete(`${API_PATHS.budgets.base}${id}`);
  return res.data;
}
