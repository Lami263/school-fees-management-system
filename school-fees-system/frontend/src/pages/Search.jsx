import { useState } from "react";
import client from "../api/client";
import DataTable from "../components/DataTable";

export default function Search() {
  const [q, setQ] = useState("");
  const [results, setResults] = useState([]);
  const [searched, setSearched] = useState(false);

  async function handleSearch(e) {
    e.preventDefault();
    const res = await client.get(`/search/students?q=${encodeURIComponent(q)}`);
    setResults(res.data);
    setSearched(true);
  }

  return (
    <div>
      <div className="page-header">
        <h1>Search</h1>
        <p>Find a student by name or admission number.</p>
      </div>

      <div className="card">
        <form className="inline-form" onSubmit={handleSearch}>
          <div className="field">
            <label>Search term</label>
            <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="e.g. Moyo or ADM001" />
          </div>
          <button className="btn" type="submit">Search</button>
        </form>
      </div>

      {searched && (
        <div className="card">
          <h2>Results ({results.length})</h2>
          <DataTable
            rowKey="id"
            rows={results}
            emptyMessage="No students matched that search."
            columns={[
              { key: "admission_no", header: "Admission No." },
              { key: "name", header: "Name", render: (r) => `${r.first_name} ${r.last_name}` },
              { key: "class_name", header: "Class" },
              { key: "status", header: "Status" },
            ]}
          />
        </div>
      )}
    </div>
  );
}
