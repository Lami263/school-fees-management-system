import { useEffect, useState } from "react";
import client, { apiErrorMessage } from "../api/client";
import DataTable from "../components/DataTable";
import { useAuth } from "../context/AuthContext";

const emptyForm = {
  student_id: "", term_id: "", amount: "", payment_method: "cash",
  reference_no: "", allow_overpayment: false,
};

export default function Payments() {
  const [payments, setPayments] = useState([]);
  const [students, setStudents] = useState([]);
  const [terms, setTerms] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [balance, setBalance] = useState(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const { user } = useAuth();
  const canRecord = user && ["admin", "bursar"].includes(user.role);
  const canEditOrDelete = user && user.role === "admin";

  function load() {
    client.get("/payments").then((res) => setPayments(res.data));
  }

  useEffect(() => {
    load();
    client.get("/students").then((res) => setStudents(res.data));
    client.get("/terms").then((res) => setTerms(res.data));
  }, []);

  useEffect(() => {
    if (form.student_id && form.term_id) {
      client.get(`/reports/student/${form.student_id}/statement?term_id=${form.term_id}`)
        .then((res) => setBalance(res.data.balance))
        .catch(() => setBalance(null));
    } else {
      setBalance(null);
    }
  }, [form.student_id, form.term_id]);

  function studentName(id) {
    const s = students.find((s) => s.id === id);
    return s ? `${s.first_name} ${s.last_name} (${s.admission_no})` : id;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError(""); setSuccess("");
    try {
      const res = await client.post("/payments", {
        ...form,
        student_id: Number(form.student_id),
        term_id: Number(form.term_id),
        amount: Number(form.amount),
      });
      setSuccess(`Payment of $${res.data.amount} recorded. Receipt generated.`);
      setForm(emptyForm);
      load();
    } catch (err) {
      setError(apiErrorMessage(err, "Payment could not be recorded."));
    }
  }

  async function handleReverse(paymentId) {
    if (!window.confirm("Reverse this payment? This action is logged.")) return;
    try {
      await client.delete(`/payments/${paymentId}?reason=Reversed via UI`);
      load();
    } catch (err) {
      setError(apiErrorMessage(err, "Could not reverse payment."));
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Payments</h1>
        <p>Record payments against a student's balance. Validation covers zero, negative, duplicate and overpayment cases.</p>
      </div>

      {canRecord && (
        <div className="card">
          <h2>Record Payment</h2>
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
              <label>Amount {balance !== null && <span>(balance: ${balance.toFixed(2)})</span>}</label>
              <input required type="number" step="0.01" value={form.amount}
                onChange={(e) => setForm({ ...form, amount: e.target.value })} />
            </div>
            <div className="field">
              <label>Method</label>
              <select value={form.payment_method} onChange={(e) => setForm({ ...form, payment_method: e.target.value })}>
                <option value="cash">Cash</option>
                <option value="bank_transfer">Bank Transfer</option>
                <option value="mobile_money">Mobile Money</option>
                <option value="cheque">Cheque</option>
              </select>
            </div>
            <div className="field">
              <label>Reference No.</label>
              <input required value={form.reference_no}
                onChange={(e) => setForm({ ...form, reference_no: e.target.value })} />
            </div>
            <div className="field">
              <label>
                <input type="checkbox" checked={form.allow_overpayment}
                  onChange={(e) => setForm({ ...form, allow_overpayment: e.target.checked })} />
                {" "}Allow overpayment
              </label>
            </div>
            <button className="btn" type="submit">Record Payment</button>
          </form>
        </div>
      )}

      <div className="card">
        <h2>Payment History</h2>
        <DataTable
          rowKey="id"
          rows={payments}
          columns={[
            { key: "student", header: "Student", render: (r) => studentName(r.student_id) },
            { key: "amount", header: "Amount", render: (r) => `$${r.amount.toFixed(2)}` },
            { key: "payment_method", header: "Method" },
            { key: "reference_no", header: "Reference" },
            { key: "payment_date", header: "Date" },
            {
              key: "status", header: "Status",
              render: (r) => (
                <span className={`badge ${r.status === "confirmed" ? "good" : r.status === "reversed" ? "bad" : "warn"}`}>
                  {r.status}
                </span>
              ),
            },
            ...(canEditOrDelete ? [{
              key: "actions", header: "Actions",
              render: (r) => r.status === "confirmed" ? (
                <div className="actions-cell">
                  <button className="btn danger" onClick={() => handleReverse(r.id)}>Reverse</button>
                </div>
              ) : null,
            }] : []),
          ]}
        />
      </div>
    </div>
  );
}
