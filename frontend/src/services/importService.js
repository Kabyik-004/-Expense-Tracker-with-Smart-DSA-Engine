import api from "./api";
import { API_PATHS } from "../utils/constants";

export async function uploadStatement(file, onProgress) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await api.post(API_PATHS.imports.upload, formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: onProgress,
    timeout: 60000,
  });
  return res.data;
}

export async function previewImport(fileId, password) {
  const body = { file_id: fileId };
  if (password) body.password = password;
  const res = await api.post(API_PATHS.imports.preview, body);
  return res.data;
}

export async function confirmImport(payload) {
  const res = await api.post(API_PATHS.imports.confirm, payload);
  return res.data;
}

export async function getImportHistory() {
  const res = await api.get(API_PATHS.imports.history);
  return res.data;
}

export async function getImportDetail(statementId) {
  const res = await api.get(API_PATHS.imports.detail(statementId));
  return res.data;
}

export async function deleteImport(statementId) {
  const res = await api.delete(API_PATHS.imports.detail(statementId));
  return res.data;
}
