const BASE_URL = process.env.REACT_APP_API_URL;

async function handleResponse(res) {
  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw new Error(error?.error || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function createInvoice(payload) {
  const res = await fetch(`${BASE_URL}/invoices/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}

export async function generatePDF(reportId) {
  const res = await fetch(`${BASE_URL}/generate-pdf/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ report_id: reportId }),
  });
  return handleResponse(res);
}

export async function checkStatus(taskId) {
  const res = await fetch(`${BASE_URL}/pdf-status/${taskId}/`);
  return handleResponse(res);
}

export async function getInvoice(id) {
  const res = await fetch(`${BASE_URL}/invoices/${id}/`);
  return handleResponse(res);
}

export async function listInvoices() {
  const res = await fetch(`${BASE_URL}/invoices/`);
  return handleResponse(res);
}

export function downloadPDF(reportId) {
  window.open(`${BASE_URL}/download-pdf/${reportId}/`, "_blank");
}
