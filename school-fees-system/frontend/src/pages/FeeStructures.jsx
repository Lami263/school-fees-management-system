import { useEffect, useState } from "react";
import client, { apiErrorMessage } from "../api/client";
import DataTable from "../components/DataTable";
import { useAuth } from "../context/AuthContext";

export default function FeeStructures() {
  const [fees, setFees] = useState([]);
  const [classes, setClasses] = useState([]);
  const [terms, setTerms] = useState([]);
  const [form, setForm] = useState({ class_id: "", term_id: "", fee_type: "", amount: "" });
  const [error, setError] = useState("");
  const { user } = useAuth();
  const canEdit = user && user.role === "admin";

  function load() {
    client.get("/fee-structures").then((res) => setFees(res.data));
  }

  useEffect(() => {
    load();
    client.get("/classes").then((res) => setClasses(res.data));
    client.get("/terms").then((res) => setTerms(res.data));
  }, []);

  function classNameOf(id) {
    return classes.find((c) => c.id === id)?.name || id;
  }
  function termNameOf(id) {
    const t = terms.find((t) => t.id === id);
    return t ? `${t.name} (${t.academic_year})` : id;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      await client.post("/fee-structures", {
        ...form,
        class_id: Number(form.class_id),
        term_id: Number(form.term_id),
        amount: Number(form.amount),
      });
      setForm({ class_id: "", term_id: "", fee_type: "", amount: "" });
      load();
    } catch (err) {
      setError(apiErrorMessage(err, "Could not save fee structure."));
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Fee Structure</h1>
        <p>Define what each class owes per term. This feeds the balance calculation for every student.</p>
      </div>

      {canEdit && (
        <div className="card">
          <h2>Add Fee Line</h2>
          {error && <div className="error-banner">{error}</div>}
          <form className="inline-form" onSubmit={handleSubmit}>
            <div className="field">
              <label>Class</label>
              <select required value={form.class_id} onChange={(e) => setForm({ ...form, class_id: e.target.value })}>
                <option value="">Select class</option>
                {classes.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
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
              <label>Fee Type</label>
              <input required placeholder="e.g. Tuition" value={form.fee_type}
                onChange={(e) => setForm({ ...form, fee_type: e.target.value })} />
            </div>
            <div className="field">
              <label>Amount</label>
              <input required type="number" min="0" step="0.01" value={form.amount}
                onChange={(e) => setForm({ ...form, amount: e.target.value })} />
            </div>
            <button className="btn" type="submit">Add</button>
          </form>
        </div>
      )}

      <div className="card">
        <h2>Fee Structures</h2>
        <DataTable
          rowKey="id"
          rows={fees}
          columns={[
            { key: "class", header: "Class", render: (r) => classNameOf(r.class_id) },
            { key: "term", header: "Term", render: (r) => termNameOf(r.term_id) },
            { key: "fee_type", header: "Fee Type" },
            { key: "amount", header: "Amount", render: (r) => `$${r.amount.toFixed(2)}` },
          ]}
        />
      </div>
    </div>
  );
}
