import React, { useState } from "react";
import InvoiceForm from "./components/InvoiceForm";
import ReportStatus from "./components/ReportStatus";
import { Toaster } from "react-hot-toast";

function App() {
  const [taskId, setTaskId] = useState(null);
  const [reportId, setReportId] = useState(null);

  return (
    <main className="min-h-screen bg-gray-50 px-4 py-8">
      {/* Toaster для уведомлений */}
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

      <div className="max-w-4xl mx-auto space-y-6">
        <InvoiceForm
          onPDFGenerated={(task, report) => {
            setTaskId(task);
            setReportId(report);
          }}
        />
        {taskId && <ReportStatus taskId={taskId} reportId={reportId} />}
      </div>
    </main>
  );
}

export default App;
