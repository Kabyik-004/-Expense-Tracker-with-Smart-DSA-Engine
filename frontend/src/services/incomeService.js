import api from "./api";
import { API_PATHS } from "../utils/constants";

export async function getIncomes(params = {}) {
  const res = await api.get(API_PATHS.incomes.base, { params });
  return res.data;
}

export async function getIncome(id) {
  const res = await api.get(`${API_PATHS.incomes.base}${id}`);
  return res.data;
}

export async function createIncome(data) {
  const res = await api.post(API_PATHS.incomes.base, data);
  return res.data;
}

export async function updateIncome(id, data) {
  const res = await api.put(`${API_PATHS.incomes.base}${id}`, data);
  return res.data;
}

export async function deleteIncome(id) {
  const res = await api.delete(`${API_PATHS.incomes.base}${id}`);
  return res.data;
}

export async function undoIncome() {
  const res = await api.post(API_PATHS.incomes.undo);
  return res.data;
}
