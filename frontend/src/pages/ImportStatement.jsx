import { useState, useCallback, useEffect, useRef } from "react";
import { FiUploadCloud, FiArrowRight, FiDatabase, FiAlertCircle, FiCheck, FiDollarSign, FiPlay, FiArrowLeft, FiLock } from "react-icons/fi";
import UploadZone from "../components/import/UploadZone";
import PreviewTable from "../components/import/PreviewTable";
import ImportSummary from "../components/import/ImportSummary";
import SupportedBanks from "../components/import/SupportedBanks";
import { useToast } from "../components/shared/Toast";
import * as importService from "../services/importService";
import { PreviewSkeleton, ImportProgressSkeleton } from "../components/import/SkeletonLoaders";
import ErrorBlock from "../components/import/ErrorBlock";
import ProgressBar from "../components/import/ProgressBar";

const STEPS = ["upload", "preview"];
const STEP_LABELS = { upload: "Upload", preview: "Review & Import" };

export default function ImportStatement() {
  const { addToast } = useToast();
  const [step, setStep] = useState("upload");
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState("idle");
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewError, setPreviewError] = useState(null);
  const [fileMeta, setFileMeta] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [previewMeta, setPreviewMeta] = useState(null);
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState(null);
  const [dupActions, setDupActions] = useState({});
  const [pdfPassword, setPdfPassword] = useState("");
  const headerRef = useRef(null);
  const confirmBtnRef = useRef(null);

  useEffect(() => {
    headerRef.current?.focus();
  }, [step]);

  const handleRetryUpload = useCallback(() => {
    setUploadStatus("idle");
    setUploadProgress(0);
    setUploading(false);
  }, []);

  const loadPreview = useCallback(async (fileId, password) => {
    setPreviewLoading(true);
    setPreviewError(null);
    try {
      const resp = await importService.previewImport(fileId, password);
      if (resp?.success) {
        setTransactions(resp.data.transactions || []);
        setPreviewMeta(resp.data.metadata || null);
        addToast("Statement parsed successfully", "success", {
          description: `${(resp.data.transactions || []).length} transactions found`,
          duration: 3000,
        });
      } else {
        setPreviewError(resp?.message || "Preview failed");
        addToast(resp?.message || "Preview failed", "error");
      }
    } catch (err) {
      const msg = err?.response?.data?.message || "Failed to parse statement";
      setPreviewError(msg);
      addToast("Preview failed", "error", { description: msg });
    } finally {
      setPreviewLoading(false);
    }
  }, [addToast]);

  const handleUpload = useCallback(async (file) => {
    setUploading(true);
    setUploadStatus("processing");
    setUploadProgress(10);
    try {
      const progressInterval = setInterval(() => {
        setUploadProgress((p) => Math.min(85, p + Math.random() * 8));
      }, 400);

      const resp = await importService.uploadStatement(file, (progressEvent) => {
        if (progressEvent?.total) {
          const pct = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(Math.min(85, pct));
        }
      });

      clearInterval(progressInterval);
      setUploadProgress(100);
      setUploadStatus("success");

      if (resp?.success) {
        setUploading(false);
        setFileMeta(resp.data);
        addToast("File uploaded successfully", "success", {
          description: `${file.name} — ${(file.size / 1024).toFixed(1)} KB`,
        });
        setTimeout(() => {
          setStep("preview");
          loadPreview(resp.data.id, pdfPassword);
        }, 600);
      } else {
        setUploadStatus("error");
        addToast(resp?.message || "Upload failed", "error");
        setUploading(false);
      }
    } catch (err) {
      setUploadStatus("error");
      const msg = err?.response?.data?.message || "Connection lost. Please check your internet and try again.";
      addToast("Upload failed", "error", { description: msg });
      setUploading(false);
    }
  }, [addToast, loadPreview, pdfPassword]);

  const handleUpdate = useCallback((rowIndex, field, value) => {
    setTransactions((prev) =>
      prev.map((tx) =>
        tx.row_index === rowIndex ? { ...tx, [field]: value } : tx
      )
    );
  }, []);

  const handleDelete = useCallback((rowIndex) => {
    setTransactions((prev) => prev.filter((tx) => tx.row_index !== rowIndex));
  }, []);

  const handleCategoryChange = useCallback((rowIndex, category) => {
    setTransactions((prev) =>
      prev.map((tx) =>
        tx.row_index === rowIndex
          ? { ...tx, suggested_category: category, category_confidence: 1.0, category_method: "manual" }
          : tx
      )
    );
  }, []);

  const handleSelectionChange = useCallback(() => {
  }, []);

  const handleDuplicateAction = useCallback((rowIndex, action) => {
    setDupActions((prev) => ({ ...prev, [rowIndex]: action }));
  }, []);

  const handleConfirmImport = useCallback(async () => {
    setImporting(true);
    setImportResult(null);
    try {
      const txPayload = transactions.map((tx) => ({
        row_index: tx.row_index,
        valid: tx.valid,
        action: dupActions[tx.row_index] || tx.duplicate_action || "import",
        debit: tx.debit,
        credit: tx.credit,
        amount: tx.amount,
        date: tx.date,
        description: tx.description,
        suggested_category: tx.suggested_category,
        reference_number: tx.reference_number,
        duplicate_matches: tx.duplicate_matches,
      }));

      const resp = await importService.confirmImport({
        file_id: fileMeta?.id,
        transactions: txPayload,
        filename: fileMeta?.filename,
        file_type: fileMeta?.file_type,
      });

      if (resp?.success) {
        setImportResult({ success: true, data: resp.data });
        addToast("Import completed successfully!", "success", {
          description: `${resp.data.results?.imported || 0} transactions imported`,
        });
      } else {
        setImportResult({ success: false, error: resp?.message || "Import failed" });
        addToast(resp?.message || "Import failed", "error");
      }
    } catch (err) {
      const msg = err?.response?.data?.message || "Import failed. Please try again.";
      setImportResult({ success: false, error: msg });
      addToast("Import failed", "error", { description: msg });
    } finally {
      setImporting(false);
    }
  }, [transactions, dupActions, fileMeta, addToast]);

  const handleBack = useCallback(() => {
    setStep("upload");
    setTransactions([]);
    setPreviewMeta(null);
    setFileMeta(null);
    setImportResult(null);
    setPreviewError(null);
    setUploadStatus("idle");
    setUploadProgress(0);
    setUploading(false);
  }, []);

  const handleRetryPreview = useCallback(() => {
    if (fileMeta?.id) loadPreview(fileMeta.id, pdfPassword);
  }, [fileMeta, loadPreview, pdfPassword]);

  const handleKeyDown = useCallback((e) => {
    if (e.key === "Escape" && step === "preview" && !importResult?.success) {
      handleBack();
    }
  }, [step, importResult, handleBack]);

  const validCount = transactions.filter((t) => t.valid).length;
  const invalidCount = transactions.filter((t) => !t.valid).length;
  const totalAmount = transactions
    .filter((t) => t.valid)
    .reduce((sum, t) => sum + (t.amount || 0), 0);

  const showImportProgress = importing;

  return (
    <div
      className="max-w-6xl mx-auto space-y-8 animate-page-enter"
      onKeyDown={handleKeyDown}
      role="main"
      aria-label="Import bank statement"
    >
      {/* Page header */}
      <div
        ref={headerRef}
        tabIndex={-1}
        className="relative overflow-hidden rounded-3xl border border-gray-200/40 dark:border-gray-800/30 bg-white/30 dark:bg-gray-900/20 backdrop-blur-2xl p-8 md:p-10 shadow-lg outline-none"
      >
        <div className="absolute top-0 right-0 w-72 h-72 bg-gradient-to-bl from-emerald-200/30 via-emerald-200/20 to-transparent dark:from-emerald-500/10 dark:via-emerald-500/8 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-56 h-56 bg-gradient-to-tr from-emerald-200/20 to-transparent dark:from-emerald-500/8 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2 pointer-events-none" />

        <div className="relative flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-4">
            {step === "preview" && !importResult?.success && (
              <button
                onClick={handleBack}
                className="w-10 h-10 rounded-xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-gray-500 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
                aria-label="Back to upload"
              >
                <FiArrowLeft className="w-5 h-5" />
              </button>
            )}
            <div className="w-14 h-14 rounded-[18px] bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center shadow-xl shadow-emerald-500/20">
              <FiUploadCloud className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white tracking-tight">
                Smart Import
              </h1>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1.5 max-w-lg leading-relaxed">
                {importResult?.success
                  ? "Import completed. Review the summary below."
                  : step === "upload"
                    ? "Upload your bank statement and let the engine do the rest."
                    : "Review and edit your transactions before importing."}
              </p>
            </div>
          </div>

          {/* Step indicator */}
          <nav className="hidden sm:flex items-center gap-2" aria-label="Import steps">
            {STEPS.map((s, i) => (
              <div key={s} className="flex items-center gap-2">
                <div
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-semibold transition-colors ${
                    step === s || (s === "upload" && importResult?.success)
                      ? "bg-emerald-100 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-300"
                      : "text-gray-400 dark:text-gray-500"
                  }`}
                  aria-current={step === s ? "step" : undefined}
                >
                  <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                    step === s || (s === "upload" && importResult?.success)
                      ? "bg-emerald-600 text-white"
                      : "bg-gray-200 dark:bg-gray-700 text-gray-500"
                  }`}>
                    {s === "upload" && importResult?.success ? (
                      <FiCheck className="w-3 h-3" />
                    ) : (
                      i + 1
                    )}
                  </div>
                  {STEP_LABELS[s]}
                </div>
                {i < STEPS.length - 1 && <FiArrowRight className="w-3 h-3 text-gray-300 dark:text-gray-600" aria-hidden="true" />}
              </div>
            ))}
          </nav>
        </div>
      </div>

      {step === "upload" && (
        <section aria-label="Upload section">
          <UploadZone
            onUpload={handleUpload}
            loading={uploading}
            progress={uploadProgress}
            uploadStatus={uploadStatus}
            onRetry={handleRetryUpload}
            pdfPassword={pdfPassword}
            onPasswordChange={setPdfPassword}
          />

          {uploadStatus !== "processing" && (
            <>
              <div className="flex items-center gap-3 py-2">
                <div className="flex-1 h-px bg-gradient-to-r from-transparent via-gray-200 dark:via-gray-700 to-transparent" />
                <span className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-widest">Supported</span>
                <div className="flex-1 h-px bg-gradient-to-r from-transparent via-gray-200 dark:via-gray-700 to-transparent" />
              </div>

              <SupportedBanks />

              <div className="flex items-center justify-center gap-2 text-xs text-gray-400 dark:text-gray-500" aria-label="Import process steps">
                <span>Secured upload</span>
                <FiArrowRight className="w-3 h-3" aria-hidden="true" />
                <span>Auto-detect bank</span>
                <FiArrowRight className="w-3 h-3" aria-hidden="true" />
                <span>Map columns</span>
                <FiArrowRight className="w-3 h-3" aria-hidden="true" />
                <span>Import expenses</span>
              </div>
            </>
          )}
        </section>
      )}

      {step === "preview" && (
        <section aria-label="Preview and import section" className="space-y-6">
          {/* Import progress */}
          {showImportProgress && (
            <div className="rounded-2xl border border-emerald-200/40 dark:border-emerald-800/30 bg-emerald-50/30 dark:bg-emerald-950/20 backdrop-blur-sm p-6">
              <ImportProgressSkeleton />
              <div className="max-w-md mx-auto mt-4">
                <ProgressBar
                  percent={importResult?.success ? 100 : 60}
                  status={importResult?.success ? "success" : "processing"}
                  label={importResult?.success ? "Import complete" : "Importing transactions..."}
                  description={importResult?.success ? "All transactions have been saved" : "Saving to database"}
                  size="sm"
                />
              </div>
            </div>
          )}

          {/* Summary bar */}
          {!importResult?.success && !importing && !previewLoading && !previewError && transactions.length > 0 && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4" role="list" aria-label="Transaction summary">
              <div className="relative overflow-hidden rounded-2xl border border-gray-200/40 dark:border-gray-800/30 bg-white/30 dark:bg-gray-900/20 backdrop-blur-xl p-5">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-emerald-100 dark:bg-emerald-900/40 flex items-center justify-center">
                    <FiDatabase className="w-5 h-5 text-emerald-600 dark:text-emerald-400" aria-hidden="true" />
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">Total</p>
                    <p className="text-lg font-bold text-gray-900 dark:text-white">{transactions.length}</p>
                  </div>
                </div>
              </div>

              <div className="relative overflow-hidden rounded-2xl border border-gray-200/40 dark:border-gray-800/30 bg-white/30 dark:bg-gray-900/20 backdrop-blur-xl p-5">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-emerald-100 dark:bg-emerald-900/40 flex items-center justify-center">
                    <FiCheck className="w-5 h-5 text-emerald-600 dark:text-emerald-400" aria-hidden="true" />
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">Valid</p>
                    <p className="text-lg font-bold text-gray-900 dark:text-white">{validCount}</p>
                  </div>
                </div>
              </div>

              <div className="relative overflow-hidden rounded-2xl border border-gray-200/40 dark:border-gray-800/30 bg-white/30 dark:bg-gray-900/20 backdrop-blur-xl p-5">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-red-100 dark:bg-red-900/40 flex items-center justify-center">
                    <FiAlertCircle className="w-5 h-5 text-red-600 dark:text-red-400" aria-hidden="true" />
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">Invalid</p>
                    <p className="text-lg font-bold text-gray-900 dark:text-white">{invalidCount}</p>
                  </div>
                </div>
              </div>

              <div className="relative overflow-hidden rounded-2xl border border-gray-200/40 dark:border-gray-800/30 bg-white/30 dark:bg-gray-900/20 backdrop-blur-xl p-5">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-amber-100 dark:bg-amber-900/40 flex items-center justify-center">
                    <FiDollarSign className="w-5 h-5 text-amber-600 dark:text-amber-400" aria-hidden="true" />
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">Total Amount</p>
                    <p className="text-lg font-bold text-gray-900 dark:text-white">
                      {new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", minimumFractionDigits: 0 }).format(totalAmount)}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Preview content */}
          {previewLoading ? (
            <PreviewSkeleton />
          ) : previewError ? (
            <div className="space-y-4">
              <ErrorBlock
                title="Failed to load preview"
                message={previewError}
                onRetry={handleRetryPreview}
                retryLabel="Retry Preview"
              />
              {previewError.toLowerCase().includes("password") && (
                <div className="max-w-xs mx-auto w-full">
                  <label className="flex items-center gap-2 text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">
                    <FiLock className="w-3.5 h-3.5" />
                    PDF Password
                  </label>
                  <input
                    type="password"
                    value={pdfPassword}
                    onChange={(e) => setPdfPassword(e.target.value)}
                    placeholder="Enter PDF password"
                    className="w-full px-3 py-2 text-sm rounded-xl border border-gray-200/60 dark:border-gray-700/50 bg-white/70 dark:bg-gray-800/50 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-400/50 transition-all input-focus"
                  />
                </div>
              )}
            </div>
          ) : (
            <>
              {transactions.length > 0 && !importResult?.success && !importing && (
                <PreviewTable
                  transactions={transactions}
                  onUpdate={handleUpdate}
                  onDelete={handleDelete}
                  onCategoryChange={handleCategoryChange}
                  onSelectionChange={handleSelectionChange}
                  onDuplicateAction={handleDuplicateAction}
                />
              )}

              {/* Import summary */}
              {importResult?.success && (
                <div className="pt-2">
                  <ImportSummary
                    importData={importResult.data}
                    transactions={transactions}
                    fileMeta={fileMeta}
                    previewMeta={previewMeta}
                  />
                </div>
              )}

              {importResult && !importResult.success && (
                <ErrorBlock
                  title="Import failed"
                  message={importResult.error}
                  onRetry={handleConfirmImport}
                  retryLabel="Retry Import"
                />
              )}
            </>
          )}

          {/* Bank metadata */}
          {previewMeta && !importResult?.success && (
            <div className="flex items-center gap-4 flex-wrap text-xs text-gray-400 dark:text-gray-500" aria-label="File metadata">
              <span>Parser: <span className="font-medium text-gray-600 dark:text-gray-300">{previewMeta.parser}</span></span>
              {previewMeta.detected_bank && (
                <span>Bank: <span className="font-medium text-gray-600 dark:text-gray-300">{previewMeta.detected_bank}</span></span>
              )}
              {fileMeta && (
                <span>File: <span className="font-medium text-gray-600 dark:text-gray-300">{fileMeta.filename}</span></span>
              )}
            </div>
          )}

          {/* Action buttons */}
          <div className="flex items-center justify-center gap-3 flex-wrap" role="group" aria-label="Import actions">
            {!importResult?.success && !previewLoading && transactions.length > 0 && (
              <button
                ref={confirmBtnRef}
                onClick={handleConfirmImport}
                disabled={importing || validCount === 0}
                className="px-8 py-3 bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-500 hover:to-emerald-600 text-white rounded-2xl font-semibold text-sm transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-lg shadow-emerald-500/20 hover:shadow-emerald-500/40 btn-hover"
                aria-label={`Confirm import of ${validCount} transactions`}
              >
                {importing ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Importing...
                  </>
                ) : (
                  <>
                    <FiPlay className="w-4 h-4" aria-hidden="true" />
                    Confirm Import ({validCount} transaction{validCount !== 1 ? "s" : ""})
                  </>
                )}
              </button>
            )}
            <button
              onClick={handleBack}
              className="px-6 py-2.5 text-sm font-semibold text-gray-600 dark:text-gray-300 bg-white/50 dark:bg-gray-900/30 border border-gray-200/50 dark:border-gray-700/40 rounded-xl hover:bg-white dark:hover:bg-gray-800 transition-all backdrop-blur-sm"
            >
              {importResult?.success ? "Import another file" : previewError ? "Upload a different file" : "Upload a different file"}
            </button>
          </div>
        </section>
      )}
    </div>
  );
}
