import React, { useEffect, useState, useCallback, useMemo } from "react";
import { checkStatus, downloadPDF } from "../api/api";

function ReportStatus({ taskId, reportId }) {
  const [status, setStatus] = useState("PENDING");

  useEffect(() => {
    if (!taskId) return;

    const interval = setInterval(async () => {
      try {
        const result = await checkStatus(taskId);
        setStatus(result.status);
        if (["SUCCESS", "FAILURE"].includes(result.status)) {
          clearInterval(interval);
        }
      } catch (error) {
        clearInterval(interval);
        setStatus("FAILURE");
        console.error("Status check error:", error);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [taskId]);

  const handleDownload = useCallback(() => {
    downloadPDF(reportId);
  }, [reportId]);

  const statusMessage = useMemo(() => {
    switch (status) {
      case "SUCCESS":
        return (
          <span className="text-green-600 font-medium flex items-center gap-1">
            ✅ PDF successfully generated
          </span>
        );
      case "FAILURE":
        return (
          <span className="text-red-600 font-medium flex items-center gap-1">
            ❌ PDF generation failed
          </span>
        );
      default:
        return (
          <span className="text-gray-500 animate-pulse flex items-center gap-1">
            ⏳ Generating PDF...
          </span>
        );
    }
  }, [status]);

  if (!taskId) return null;

  return (
    <div className="max-w-3xl mx-auto mt-6 bg-white p-4 rounded-xl shadow-md flex flex-col md:flex-row items-center justify-between gap-3">
      <div className="text-sm">{statusMessage}</div>

      {status === "SUCCESS" && (
        <button
          onClick={handleDownload}
          className="btn-outline transition hover:scale-105 active:scale-95"
        >
          📄 Download PDF
        </button>
      )}
    </div>
  );
}

export default React.memo(ReportStatus);
