import { useEffect, useState } from "react";
import client, { apiErrorMessage } from "../api/client";
import DataTable from "../components/DataTable";

export default function Discounts() {
  const [discounts, setDiscounts] = useState([]);
  const [students, setStudents] = useState([]);
  const [terms, setTerms] = useState([]);
  const [form, setForm] = useState({ student_id: "", term_id: "", discount_type: "scholarship", amount: "", reason: "" });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  function load() {
    client.get("/discounts").then((res) => setDiscounts(res.data));
  }

  useEffect(() => {
    load();
    client.get("/students").then((res) => setStudents(res.data));
    client.get("/terms").then((res) => setTerms(res.data));
  }, []);

  function studentName(id) {
    const s = students.find((s) => s.id === id);
    return s ? `${s.first_name} ${s.last_name} (${s.admission_no})` : id;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError(""); setSuccess("");
    try {
      await client.post("/discounts", {
        ...form,
        student_id: Number(form.student_id),
        term_id: Number(form.term_id),
        amount: Number(form.amount),
      });
      setSuccess("Discount applied.");
      setForm({ student_id: "", term_id: "", discount_type: "scholarship", amount: "", reason: "" });
      load();
    } catch (err) {
      setError(apiErrorMessage(err, "Could not apply discount."));
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Discounts</h1>
        <p>Scholarships, sibling and staff discounts reduce a student's net fees before balance is calculated.</p>
      </div>

      <div className="card">
        <h2>Apply Discount</h2>
        {error && <div className="error-banner">{error}</div>}
        {success && <div className="success-banner">{success}</div>}
        <form className="inline-form" onSubmit={handleSubmit}>
          <div className="field">
            <label>Student</label>
            <select required value={form.student_id} onChange={(e) => setForm({ ...form, student_id: e.target.value })}>
              <option value="">Select student</option>
              {students.map((s) => <option key={s.id} value={s.id}>{s.first_name} {s.last_name} ({s.admission_no})</option>)}
            </select>
          </div>
          <div className="field">
            <label>Term</label>
            <select required value={form.term_id} onChange={(e) => setForm({ ...form, term_id: e.target.value })}>
              <option value="">Select term</option>
              {terms.map((t) => <option key={t.id} value={t.id}>{t.name} ({t.academic_year})</option>)}
            </select>
          </div>
          <div className="field">
            <label>Type</label>
            <select value={form.discount_type} onChange={(e) => setForm({ ...form, discount_type: e.target.value })}>
              <option value="scholarship">Scholarship</option>
              <option value="sibling">Sibling</option>
              <option value="staff">Staff</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div className="field">
            <label>Amount</label>
            <input required type="number" min="0" step="0.01" value={form.amount}
              onChange={(e) => setForm({ ...form, amount: e.target.value })} />
          </div>
          <div className="field">
            <label>Reason</label>
            <textarea value={form.reason} onChange={(e) => setForm({ ...form, reason: e.target.value })} />
          </div>
          <button className="btn" type="submit">Apply</button>
        </form>
      </div>

      <div className="card">
        <h2>Discounts Given</h2>
        <DataTable
          rowKey="id"
          rows={discounts}
          columns={[
            { key: "student", header: "Student", render: (r) => studentName(r.student_id) },
            { key: "discount_type", header: "Type" },
            { key: "amount", header: "Amount", render: (r) => `$${r.amount.toFixed(2)}` },
            { key: "reason", header: "Reason" },
          ]}
        />
      </div>
    </div>
  );
}
