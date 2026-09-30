import { useEffect, useState } from "react";
import client from "../api/client";

export default function Reports() {
  const [students, setStudents] = useState([]);
  const [terms, setTerms] = useState([]);
  const [studentId, setStudentId] = useState("");
  const [termId, setTermId] = useState("");
  const [statement, setStatement] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    client.get("/students").then((res) => setStudents(res.data));
    client.get("/terms").then((res) => setTerms(res.data));
  }, []);

  async function handleLoad(e) {
    e.preventDefault();
    setError("");
    setStatement(null);
    try {
      const res = await client.get(`/reports/student/${studentId}/statement?term_id=${termId}`);
      setStatement(res.data);
    } catch (err) {
      setError("Could not load statement.");
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Reports</h1>
        <p>Per-student fee statement: fees, discounts, payments and running balance.</p>
      </div>

      <div className="card">
        <h2>Student Statement</h2>
        {error && <div className="error-banner">{error}</div>}
        <form className="inline-form" onSubmit={handleLoad}>
          <div className="field">
            <label>Student</label>
            <select required value={studentId} onChange={(e) => setStudentId(e.target.value)}>
              <option value="">Select student</option>
              {students.map((s) => <option key={s.id} value={s.id}>{s.first_name} {s.last_name} ({s.admission_no})</option>)}
            </select>
          </div>
          <div className="field">
            <label>Term</label>
            <select required value={termId} onChange={(e) => setTermId(e.target.value)}>
              <option value="">Select term</option>
              {terms.map((t) => <option key={t.id} value={t.id}>{t.name} ({t.academic_year})</option>)}
            </select>
          </div>
          <button className="btn" type="submit">Generate</button>
        </form>
      </div>

      {statement && (
        <div className="card">
          <h2>Statement Summary</h2>
          <div className="stat-row">
            <div className="stat"><div className="label">Total Fees</div><div className="value">${statement.total_fees.toFixed(2)}</div></div>
            <div className="stat"><div className="label">Discounts</div><div className="value">${statement.total_discount.toFixed(2)}</div></div>
            <div className="stat"><div className="label">Net Fees</div><div className="value">${statement.net_fees.toFixed(2)}</div></div>
            <div className="stat good"><div className="label">Total Paid</div><div className="value">${statement.total_payments.toFixed(2)}</div></div>
            <div className={`stat ${statement.balance > 0 ? "warn" : "good"}`}>
              <div className="label">Balance</div><div className="value">${statement.balance.toFixed(2)}</div>
            </div>
          </div>

          <h2>Payment History</h2>
          <table>
            <thead><tr><th>Date</th><th>Amount</th><th>Method</th><th>Reference</th><th>Status</th></tr></thead>
            <tbody>
              {statement.payments.map((p) => (
                <tr key={p.id}>
                  <td>{p.payment_date}</td>
                  <td>${p.amount.toFixed(2)}</td>
                  <td>{p.payment_method}</td>
                  <td>{p.reference_no}</td>
                  <td><span className={`badge ${p.status === "confirmed" ? "good" : "bad"}`}>{p.status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
