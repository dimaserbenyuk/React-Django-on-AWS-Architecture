import React, { useState, Suspense, lazy } from "react";
import InvoiceForm from "./components/InvoiceForm";
import { Toaster } from "react-hot-toast";

const ReportStatus = lazy(() => import("./components/ReportStatus"));

function App() {
  const [taskId, setTaskId] = useState(null);
  const [reportId, setReportId] = useState(null);

  return (
    <>
      {/* 🔔 Toaster для уведомлений */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: "#fff",
            color: "#1f2937",
            border: "1px solid #e5e7eb",
            fontSize: "0.875rem",
          },
        }}
      />

      <main className="min-h-screen bg-gray-50 px-4 py-8">
        <div className="max-w-4xl mx-auto space-y-6">
          <InvoiceForm
            onPDFGenerated={(task, report) => {
              setTaskId(task);
              setReportId(report);
            }}
          />

          {/* 🎯 Suspense wrapper для ленивой загрузки */}
          {taskId && (
            <Suspense fallback={<div className="text-sm text-gray-400 animate-pulse">Loading status...</div>}>
              <ReportStatus taskId={taskId} reportId={reportId} />
            </Suspense>
          )}
        </div>
      </main>
    </>
  );
}

export default App;
