import { useEffect, useState } from "react";
import client from "../api/client";

export default function Dashboard() {
  const [terms, setTerms] = useState([]);
  const [termId, setTermId] = useState(null);
  const [collections, setCollections] = useState(null);
  const [outstanding, setOutstanding] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    client.get("/terms").then((res) => {
      setTerms(res.data);
      if (res.data.length > 0) setTermId(res.data[0].id);
    });
  }, []);

  useEffect(() => {
    if (!termId) return;
    Promise.all([
      client.get(`/reports/collections?term_id=${termId}`),
      client.get(`/reports/outstanding?term_id=${termId}`),
    ])
      .then(([c, o]) => {
        setCollections(c.data);
        setOutstanding(o.data);
      })
      .catch(() => setError("Could not load dashboard data. Is the backend running?"));
  }, [termId]);

  const totalOutstanding = outstanding.reduce((sum, s) => sum + s.balance, 0);

  return (
    <div>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Overview of collections and outstanding balances for the selected term.</p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="field" style={{ marginBottom: 20 }}>
        <label>Term</label>
        <select value={termId || ""} onChange={(e) => setTermId(Number(e.target.value))}>
          {terms.map((t) => (
            <option key={t.id} value={t.id}>{t.name} ({t.academic_year})</option>
          ))}
        </select>
      </div>

      <div className="stat-row">
        <div className="stat good">
          <div className="label">Total Collected</div>
          <div className="value">${collections ? collections.total_collected.toFixed(2) : "0.00"}</div>
        </div>
        <div className="stat">
          <div className="label">Transactions</div>
          <div className="value">{collections ? collections.transaction_count : 0}</div>
        </div>
        <div className="stat warn">
          <div className="label">Total Outstanding</div>
          <div className="value">${totalOutstanding.toFixed(2)}</div>
        </div>
        <div className="stat warn">
          <div className="label">Students with Balance</div>
          <div className="value">{outstanding.length}</div>
        </div>
      </div>

      {collections && (
        <div className="card">
          <h2>Collections by Payment Method</h2>
          <table>
            <thead><tr><th>Method</th><th>Amount</th></tr></thead>
            <tbody>
              {Object.entries(collections.by_payment_method).map(([method, amount]) => (
                <tr key={method}>
                  <td style={{ textTransform: "capitalize" }}>{method.replace("_", " ")}</td>
                  <td>${amount.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="card">
        <h2>Top Outstanding Balances</h2>
        <table>
          <thead><tr><th>Admission No.</th><th>Name</th><th>Class</th><th>Balance</th></tr></thead>
          <tbody>
            {outstanding.slice(0, 8).map((s) => (
              <tr key={s.student_id}>
                <td>{s.admission_no}</td>
                <td>{s.name}</td>
                <td>{s.class_name}</td>
                <td><span className="badge warn">${s.balance.toFixed(2)}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
