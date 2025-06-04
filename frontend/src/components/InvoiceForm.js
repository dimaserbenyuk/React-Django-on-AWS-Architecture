import React, { useState } from "react";
import { createInvoice, generatePDF } from "../api/api";
import toast from "react-hot-toast";

function InvoiceForm({ onPDFGenerated }) {
  const [form, setForm] = useState({
    company_name: "",
    address: "",
    customer_name: "",
    customer_email: "",
    customer_phone: "",
    customer_address: "",
    items: [{ name: "", quantity: 1, unit_price: 0 }],
  });

  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleItemChange = (index, field, value) => {
    const updated = [...form.items];
    updated[index][field] = value;
    setForm((prev) => ({ ...prev, items: updated }));
  };

  const addItem = () => {
    setForm((prev) => ({
      ...prev,
      items: [...prev.items, { name: "", quantity: 1, unit_price: 0 }],
    }));
  };

  const resetForm = () => {
    setForm({
      company_name: "",
      address: "",
      customer_name: "",
      customer_email: "",
      customer_phone: "",
      customer_address: "",
      items: [{ name: "", quantity: 1, unit_price: 0 }],
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const payload = {
        company_name: form.company_name,
        address: form.address,
        customer: {
          name: form.customer_name,
          email: form.customer_email,
          phone: form.customer_phone,
          address: form.customer_address,
        },
        items: form.items,
      };

      const invoice = await createInvoice(payload);
      const task = await generatePDF(invoice.id);

      toast.success("🧾 Invoice created, PDF generation started");
      onPDFGenerated?.(task.task_id, invoice.id);
      resetForm();
    } catch (err) {
      console.error(err);
      toast.error("❌ Failed to generate invoice");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <header className="mt-12 mb-8 text-center">
        <h1 className="text-4xl font-bold tracking-tight text-gray-800">
          🧾 Invoice PDF Generator
        </h1>
        <p className="text-gray-500 mt-2">Create invoice and download PDF</p>
      </header>

      <form
        onSubmit={handleSubmit}
        className="max-w-3xl mx-auto p-6 bg-white rounded-2xl shadow-lg space-y-6"
      >
        {/* Company Info */}
        <section className="space-y-2">
          <h2 className="text-xl font-semibold">🏢 Company Info</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <input name="company_name" value={form.company_name} onChange={handleChange} placeholder="Company Name" required className="input" />
            <input name="address" value={form.address} onChange={handleChange} placeholder="Company Address" required className="input" />
          </div>
        </section>

        {/* Customer Info */}
        <section className="space-y-2">
          <h2 className="text-xl font-semibold">👤 Customer Info</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <input name="customer_name" value={form.customer_name} onChange={handleChange} placeholder="Name" required className="input" />
            <input name="customer_email" value={form.customer_email} onChange={handleChange} placeholder="Email" className="input" />
            <input name="customer_phone" value={form.customer_phone} onChange={handleChange} placeholder="Phone" className="input" />
            <input name="customer_address" value={form.customer_address} onChange={handleChange} placeholder="Address" className="input" />
          </div>
        </section>

        {/* Items */}
        <section className="space-y-2">
          <h2 className="text-xl font-semibold">📦 Items</h2>
          {form.items.map((item, idx) => (
            <div key={idx} className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <input value={item.name} onChange={(e) => handleItemChange(idx, "name", e.target.value)} placeholder="Item name" required className="input" />
              <input type="number" value={item.quantity} onChange={(e) => handleItemChange(idx, "quantity", e.target.value)} min="1" required className="input" />
              <input type="number" value={item.unit_price} onChange={(e) => handleItemChange(idx, "unit_price", e.target.value)} min="0" required className="input" />
            </div>
          ))}
          <button type="button" onClick={addItem} className="text-sm text-blue-600 hover:underline">
            ➕ Add Item
          </button>
        </section>

        {/* Actions */}
        <div className="flex items-center gap-4">
          <button
            type="submit"
            disabled={loading}
            className={`btn-primary transition-transform duration-200 ${
              loading ? "opacity-50 cursor-not-allowed" : "hover:scale-105 active:scale-95"
            }`}
          >
            {loading ? "Generating..." : "Generate PDF"}
          </button>
        </div>
      </form>
    </>
  );
}

export default InvoiceForm;
