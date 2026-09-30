import { useEffect, useState } from "react";
import client from "../api/client";
import DataTable from "../components/DataTable";

export default function OutstandingFees() {
  const [terms, setTerms] = useState([]);
  const [termId, setTermId] = useState(null);
  const [rows, setRows] = useState([]);

  useEffect(() => {
    client.get("/terms").then((res) => {
      setTerms(res.data);
      if (res.data.length > 0) setTermId(res.data[0].id);
    });
  }, []);

  useEffect(() => {
    if (!termId) return;
    client.get(`/reports/outstanding?term_id=${termId}`).then((res) => setRows(res.data));
  }, [termId]);

  const total = rows.reduce((s, r) => s + r.balance, 0);

  return (
    <div>
      <div className="page-header">
        <h1>Outstanding Fees</h1>
        <p>Students with a balance greater than zero for the selected term.</p>
      </div>

      <div className="field" style={{ marginBottom: 20 }}>
        <label>Term</label>
        <select value={termId || ""} onChange={(e) => setTermId(Number(e.target.value))}>
          {terms.map((t) => <option key={t.id} value={t.id}>{t.name} ({t.academic_year})</option>)}
        </select>
      </div>

      <div className="stat-row">
        <div className="stat warn">
          <div className="label">Total Outstanding</div>
          <div className="value">${total.toFixed(2)}</div>
        </div>
        <div className="stat">
          <div className="label">Students Affected</div>
          <div className="value">{rows.length}</div>
        </div>
      </div>

      <div className="card">
        <DataTable
          rowKey="student_id"
          rows={rows}
          emptyMessage="No outstanding balances for this term."
          columns={[
            { key: "admission_no", header: "Admission No." },
            { key: "name", header: "Name" },
            { key: "class_name", header: "Class" },
            { key: "balance", header: "Balance", render: (r) => <span className="badge warn">${r.balance.toFixed(2)}</span> },
          ]}
        />
      </div>
    </div>
  );
}
