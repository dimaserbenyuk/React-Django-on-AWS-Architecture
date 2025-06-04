const BASE_URL = import.meta.env.VITE_API_URL;

async function handleResponse(res) {
  const contentType = res.headers.get("content-type");
  const isJSON = contentType && contentType.includes("application/json");
  const data = isJSON ? await res.json().catch(() => null) : null;

  if (!res.ok) {
    const message = data?.error || `HTTP ${res.status}`;
    throw new Error(message);
  }

  return data;
}

async function request(url, options = {}) {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  return handleResponse(res);
}

// API Methods
export const createInvoice = (payload) =>
  request(`${BASE_URL}/invoices/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const generatePDF = (reportId) =>
  request(`${BASE_URL}/generate-pdf/`, {
    method: "POST",
    body: JSON.stringify({ report_id: reportId }),
  });

export const checkStatus = (taskId) =>
  request(`${BASE_URL}/pdf-status/${taskId}/`);

export const getInvoice = (id) =>
  request(`${BASE_URL}/invoices/${id}/`);

export const listInvoices = () =>
  request(`${BASE_URL}/invoices/`);

export const downloadPDF = (reportId) => {
  window.open(`${BASE_URL}/download-pdf/${reportId}/`, "_blank", "noopener,noreferrer");
};
