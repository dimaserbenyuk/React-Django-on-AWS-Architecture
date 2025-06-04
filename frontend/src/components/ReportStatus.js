import React, { useEffect, useState } from "react";
import { checkStatus, downloadPDF } from "../api/api";

function ReportStatus({ taskId, reportId }) {
  const [status, setStatus] = useState("PENDING");

  useEffect(() => {
    const interval = setInterval(async () => {
      const result = await checkStatus(taskId);
      setStatus(result.status);
      if (["SUCCESS", "FAILURE"].includes(result.status)) {
        clearInterval(interval);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [taskId]);

  if (!taskId) return null;

  return (
    <div className="max-w-3xl mx-auto mt-4 bg-white p-4 rounded-xl shadow-md flex items-center justify-between">
      <div className="text-sm">
        {status === "SUCCESS" && (
          <span className="text-green-600 font-semibold">✅ PDF successfully generated</span>
        )}
        {status === "FAILURE" && (
          <span className="text-red-600 font-semibold">❌ PDF generation failed</span>
        )}
        {status === "PENDING" || status === "STARTED" || status === "RUNNING" ? (
          <span className="text-gray-500 animate-pulse">⏳ Generating PDF...</span>
        ) : null}
      </div>

      {status === "SUCCESS" && (
        <button
          onClick={() => downloadPDF(reportId)}
          className="btn-outline ml-4"
        >
          📄 Download PDF
        </button>
      )}
    </div>
  );
}

export default ReportStatus;
