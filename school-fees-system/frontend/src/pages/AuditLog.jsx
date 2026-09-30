import { useEffect, useState } from "react";
import client from "../api/client";
import DataTable from "../components/DataTable";

export default function AuditLog() {
  const [entries, setEntries] = useState([]);

  useEffect(() => {
    client.get("/audit").then((res) => setEntries(res.data));
  }, []);

  return (
    <div>
      <div className="page-header">
        <h1>Audit Log</h1>
        <p>Every edit or reversal of a confirmed payment is recorded here, admin-only.</p>
      </div>
      <div className="card">
        <DataTable
          rowKey="id"
          rows={entries}
          emptyMessage="No audit entries yet."
          columns={[
            { key: "timestamp", header: "Timestamp" },
            { key: "action", header: "Action" },
            { key: "table_affected", header: "Table" },
            { key: "record_id", header: "Record ID" },
            { key: "details", header: "Details" },
          ]}
        />
      </div>
    </div>
  );
}
