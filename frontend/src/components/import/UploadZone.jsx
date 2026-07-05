import { useState, useRef, useCallback, useEffect } from "react";
import { FiUpload, FiFile, FiCheck, FiX, FiAlertCircle, FiLock } from "react-icons/fi";
import ProgressBar from "./ProgressBar";

const FORMATS = [
  { ext: "CSV", color: "text-green-600 dark:text-green-400", bg: "bg-green-100 dark:bg-green-900/40" },
  { ext: "PDF", color: "text-red-600 dark:text-red-400", bg: "bg-red-100 dark:bg-red-900/40" },
  { ext: "XLSX", color: "text-emerald-600 dark:text-emerald-400", bg: "bg-emerald-100 dark:bg-emerald-900/40" },
];

const ACCEPTED = ".csv,.pdf,.xlsx,.xls";

export default function UploadZone({ onUpload, loading, progress, uploadStatus, onRetry, pdfPassword, onPasswordChange }) {
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState(null);
  const [focused, setFocused] = useState(false);
  const inputRef = useRef(null);
  const zoneRef = useRef(null);

  useEffect(() => {
    if (uploadStatus === "idle" && !loading) {
      if (error && !selectedFile) {
      }
    }
  }, [uploadStatus, loading, error, selectedFile]);

  const validate = useCallback((file) => {
    if (!file) return "No file selected";
    const ext = "." + file.name.split(".").pop().toLowerCase();
    if (!ACCEPTED.includes(ext)) return "Unsupported format. Please upload CSV, PDF, or Excel files.";
    if (file.size > 15 * 1024 * 1024) return "File must be under 15 MB";
    if (file.size === 0) return "File is empty";
    return null;
  }, []);

  const handleFile = useCallback((file) => {
    setError(null);
    const err = validate(file);
    if (err) { setError(err); setSelectedFile(null); return; }
    setSelectedFile(file);
  }, [validate]);

  const handleDrop = useCallback((e) => {
    e.preventDefault(); setDragOver(false);
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  }, [handleFile]);

  const handleChange = useCallback((e) => {
    const f = e.target.files[0];
    if (f) handleFile(f);
  }, [handleFile]);

  const handleUploadClick = useCallback(() => {
    if (!selectedFile) return;
    onUpload(selectedFile);
  }, [selectedFile, onUpload]);

  const handleRemove = useCallback(() => {
    setSelectedFile(null); setError(null);
    if (inputRef.current) inputRef.current.value = "";
  }, []);

  const handleRetry = useCallback(() => {
    setError(null);
    onRetry?.();
  }, [onRetry]);

  const handleKeyDown = useCallback((e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      if (selectedFile && !loading) {
        handleUploadClick();
      } else if (!selectedFile) {
        inputRef.current?.click();
      }
    }
    if (e.key === "Escape" && selectedFile) {
      handleRemove();
    }
  }, [selectedFile, loading, handleUploadClick, handleRemove]);

  const showProgress = loading || uploadStatus === "processing" || uploadStatus === "success" || uploadStatus === "error";

  return (
    <div className="w-full space-y-4">
      <div
        ref={zoneRef}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => !selectedFile && !loading && inputRef.current?.click()}
        onKeyDown={handleKeyDown}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        tabIndex={0}
        role="button"
        aria-label={selectedFile ? `Selected file: ${selectedFile.name}. Press Enter to upload or Escape to remove.` : "Click or drag and drop to upload a bank statement"}
        aria-describedby="upload-formats upload-limit"
        className={`
          relative overflow-hidden rounded-3xl border-2 border-dashed cursor-pointer
          transition-all duration-500 p-10 md:p-14 text-center outline-none
          ${focused ? "ring-2 ring-indigo-400/50 ring-offset-2 ring-offset-transparent" : ""}
          ${dragOver
            ? "border-indigo-400/80 bg-indigo-50/80 dark:bg-indigo-950/40 drag-over"
            : selectedFile
              ? "border-emerald-300/70 bg-emerald-50/70 dark:border-emerald-600/50 dark:bg-emerald-950/30"
              : error
                ? "border-red-300/70 bg-red-50/70 dark:border-red-600/50 dark:bg-red-950/30"
                : "border-gray-200/60 dark:border-gray-700/50 bg-white/40 dark:bg-gray-900/30 hover:border-indigo-300/50 dark:hover:border-indigo-600/40"
          }
          backdrop-blur-xl shadow-lg
          ${loading ? "pointer-events-none opacity-80" : ""}
        `}
      >
        {dragOver && (
          <div className="absolute inset-0 bg-gradient-to-br from-indigo-400/10 via-transparent to-purple-400/10 dark:from-indigo-500/10 dark:to-purple-500/10 animate-gradient-shift pointer-events-none" />
        )}

        {dragOver && (
          <div className="absolute left-4 right-4 h-[2px] bg-gradient-to-r from-transparent via-indigo-500/60 to-transparent animate-scan-line pointer-events-none" />
        )}

        {!selectedFile && !dragOver && !loading && (
          <div className="absolute inset-0 pointer-events-none overflow-hidden opacity-30 dark:opacity-20">
            <div className="absolute w-2 h-2 rounded-full bg-indigo-400 top-1/4 left-[20%] animate-float-particle" style={{ animationDelay: "0s" }} />
            <div className="absolute w-1.5 h-1.5 rounded-full bg-purple-400 top-1/3 left-[70%] animate-float-particle" style={{ animationDelay: "0.8s" }} />
            <div className="absolute w-2.5 h-2.5 rounded-full bg-indigo-300 top-[60%] left-[40%] animate-float-particle" style={{ animationDelay: "1.6s" }} />
            <div className="absolute w-1 h-1 rounded-full bg-violet-400 top-[20%] left-[55%] animate-float-particle" style={{ animationDelay: "2.2s" }} />
          </div>
        )}

        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED}
          onChange={handleChange}
          className="hidden"
          tabIndex={-1}
          aria-hidden="true"
        />

        {loading || uploadStatus === "processing" ? (
          <div className="relative space-y-6 py-4">
            <div className="flex flex-col items-center gap-3">
              <div className="relative">
                <div className="w-20 h-20 rounded-[28px] bg-indigo-100 dark:bg-indigo-900/50 flex items-center justify-center shadow-inner">
                  <div className="w-10 h-10 border-2 border-indigo-300 border-t-indigo-600 rounded-full animate-spin" />
                </div>
              </div>
              <div>
                <p className="text-lg font-semibold text-gray-900 dark:text-white">Processing your statement</p>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Please wait while we analyze the file</p>
              </div>
            </div>
            <div className="max-w-md mx-auto">
              <ProgressBar
                percent={progress ?? 45}
                status="processing"
                label="Parsing transactions"
                description="Analyzing structure, detecting bank, mapping columns"
                size="sm"
              />
            </div>
          </div>
        ) : selectedFile ? (
          <div className="relative space-y-5">
            <div className="w-20 h-20 mx-auto bg-emerald-100 dark:bg-emerald-900/50 rounded-[28px] flex items-center justify-center shadow-inner">
              <div className="w-10 h-10 rounded-xl bg-emerald-200 dark:bg-emerald-800/60 flex items-center justify-center">
                <FiCheck className="w-6 h-6 text-emerald-700 dark:text-emerald-300" />
              </div>
            </div>
            <div>
              <p className="text-xl font-semibold text-gray-900 dark:text-white truncate max-w-xs mx-auto">
                {selectedFile.name}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                {(selectedFile.size / 1024).toFixed(1)} KB
              </p>
            </div>
            {selectedFile.name.toLowerCase().endsWith(".pdf") && (
              <div className="max-w-xs mx-auto w-full">
                <label className="flex items-center gap-2 text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">
                  <FiLock className="w-3.5 h-3.5" />
                  PDF Password (if protected)
                </label>
                <input
                  type="password"
                  value={pdfPassword}
                  onClick={(e) => e.stopPropagation()}
                  onChange={(e) => onPasswordChange?.(e.target.value)}
                  placeholder="Enter PDF password"
                  className="w-full px-3 py-2 text-sm rounded-xl border border-gray-200/60 dark:border-gray-700/50 bg-white/70 dark:bg-gray-800/50 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-400/50 transition-all input-focus"
                  aria-label="PDF password"
                />
              </div>
            )}
            <div className="flex justify-center gap-3">
              <button
                onClick={(e) => { e.stopPropagation(); handleUploadClick(); }}
                disabled={loading}
                className="px-8 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white rounded-2xl font-semibold text-sm transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/40 btn-hover"
                aria-label="Upload selected file"
              >
                <FiUpload className="w-4 h-4" />
                Upload Statement
              </button>
              <button
                onClick={(e) => { e.stopPropagation(); handleRemove(); }}
                className="px-5 py-3 text-gray-600 dark:text-gray-300 bg-white/70 dark:bg-gray-800/50 border border-gray-200/60 dark:border-gray-700/50 rounded-2xl hover:bg-white dark:hover:bg-gray-800 font-semibold text-sm transition-all flex items-center gap-2 backdrop-blur-sm"
                aria-label="Remove selected file"
              >
                <FiX className="w-4 h-4" />
                Remove
              </button>
            </div>
          </div>
        ) : (
          <div className="relative space-y-5">
            <div className="relative mx-auto w-fit">
              <div className={`w-24 h-24 mx-auto rounded-[32px] flex items-center justify-center shadow-inner transition-all duration-500 ${
                error
                  ? "bg-red-100 dark:bg-red-900/40"
                  : "bg-gradient-to-br from-indigo-100 to-purple-100 dark:from-indigo-900/40 dark:to-purple-900/40"
              }`}>
                {error ? (
                  <FiAlertCircle className="w-10 h-10 text-red-500 dark:text-red-400" />
                ) : (
                  <FiUpload className="w-10 h-10 text-indigo-600 dark:text-indigo-400" />
                )}
              </div>
              {dragOver && (
                <div className="absolute inset-0 rounded-[32px] animate-upload-pulse" />
              )}
            </div>

            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {dragOver ? "Drop your file here" : error ? "Upload failed" : "Upload bank statement"}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-2 max-w-md mx-auto leading-relaxed">
                {error ? (
                  <span className="text-red-600 dark:text-red-400 font-medium">{error}</span>
                ) : (
                  <>
                    Drag & drop your statement or{" "}
                    <span className="text-indigo-600 dark:text-indigo-400 font-semibold underline underline-offset-2 decoration-indigo-300/50">
                      browse files
                    </span>
                  </>
                )}
              </p>
            </div>

            {!error && (
              <>
                <div className="flex justify-center gap-2.5">
                  {FORMATS.map((f) => (
                    <span
                      key={f.ext}
                      className={`inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-semibold tracking-wide ${f.bg} ${f.color} border border-current/10 backdrop-blur-sm`}
                    >
                      <FiFile className="w-3.5 h-3.5" />
                      {f.ext}
                    </span>
                  ))}
                </div>

                <p id="upload-limit" className="text-xs text-gray-400 dark:text-gray-500">
                  Maximum file size: 15 MB
                </p>
              </>
            )}

            {error && (
              <div className="flex justify-center">
                <button
                  onClick={(e) => { e.stopPropagation(); setError(null); }}
                  className="inline-flex items-center gap-1.5 px-5 py-2.5 text-sm font-semibold text-gray-600 dark:text-gray-300 bg-white/70 dark:bg-gray-800/50 border border-gray-200/60 dark:border-gray-700/50 rounded-2xl hover:bg-white dark:hover:bg-gray-800 transition-all backdrop-blur-sm"
                >
                  <FiX className="w-4 h-4" />
                  Dismiss
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Progress bar for upload in progress / success / error */}
      {showProgress && (
        <div className="max-w-lg mx-auto w-full">
          <ProgressBar
            percent={uploadStatus === "success" ? 100 : progress ?? 0}
            status={uploadStatus === "processing" ? "processing" : uploadStatus === "success" ? "success" : uploadStatus === "error" ? "error" : "idle"}
            label={uploadStatus === "processing" ? "Uploading..." : uploadStatus === "success" ? "Upload complete" : uploadStatus === "error" ? "Upload failed" : ""}
            description={uploadStatus === "processing" ? "Encrypting and transferring your file" : uploadStatus === "error" ? "Check your connection and try again" : undefined}
            onRetry={uploadStatus === "error" ? handleRetry : undefined}
            size="sm"
          />
        </div>
      )}

      {error && !showProgress && (
        <div className="flex items-start gap-3 p-4 bg-red-50/80 dark:bg-red-950/40 border border-red-200/60 dark:border-red-800/50 rounded-2xl backdrop-blur-sm animate-fade-in" role="alert">
          <FiAlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
          <p className="text-sm text-red-700 dark:text-red-300 font-medium">{error}</p>
        </div>
      )}
    </div>
  );
}
