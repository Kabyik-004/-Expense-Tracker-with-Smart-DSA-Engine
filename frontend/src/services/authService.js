import api from "./api";
import { API_PATHS } from "../utils/constants";

export async function registerUser(data) {
  const res = await api.post(API_PATHS.auth.register, data);
  return res.data;
}

export async function loginUser(data) {
  const res = await api.post(API_PATHS.auth.login, data);
  return res.data;
}

export async function refreshToken() {
  const res = await api.post(API_PATHS.auth.refresh);
  return res.data;
}

export async function logoutUser() {
  const res = await api.post(API_PATHS.auth.logout);
  return res.data;
}

export async function getProfile() {
  const res = await api.get(API_PATHS.auth.profile);
  return res.data;
}

export async function updateProfile(data) {
  const res = await api.put(API_PATHS.auth.profile, data);
  return res.data;
}

export async function changePassword(data) {
  const res = await api.put(API_PATHS.auth.changePassword, data);
  return res.data;
}

export async function uploadAvatar(data) {
  const res = await api.post(API_PATHS.auth.avatar, data);
  return res.data;
}

export async function getRecentActivity() {
  const res = await api.get(API_PATHS.auth.activity);
  return res.data;
}

export async function forgotPassword(data) {
  const res = await api.post(API_PATHS.auth.forgotPassword, data);
  return res.data;
}

export async function resetPassword(data) {
  const res = await api.post(API_PATHS.auth.resetPassword, data);
  return res.data;
}
