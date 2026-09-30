import { useEffect, useState } from "react";
import client, { apiErrorMessage } from "../api/client";
import DataTable from "../components/DataTable";
import { useAuth } from "../context/AuthContext";

const emptyForm = {
  admission_no: "", first_name: "", last_name: "", dob: "", gender: "M",
  class_id: "", guardian_name: "", guardian_phone: "",
};

export default function Students() {
  const [students, setStudents] = useState([]);
  const [classes, setClasses] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const { user } = useAuth();

  function loadStudents() {
    client.get("/students").then((res) => setStudents(res.data));
  }

  useEffect(() => {
    loadStudents();
    client.get("/classes").then((res) => setClasses(res.data));
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSuccess("");
    try {
      await client.post("/students", form);
      setSuccess(`Student ${form.first_name} ${form.last_name} registered.`);
      setForm(emptyForm);
      loadStudents();
    } catch (err) {
      setError(apiErrorMessage(err, "Could not register student."));
    }
  }

  const canEdit = user && ["admin", "bursar"].includes(user.role);

  return (
    <div>
      <div className="page-header">
        <h1>Students</h1>
        <p>Register new students and browse existing records.</p>
      </div>

      {canEdit && (
        <div className="card">
          <h2>Register Student</h2>
          {error && <div className="error-banner">{error}</div>}
          {success && <div className="success-banner">{success}</div>}
          <form className="inline-form" onSubmit={handleSubmit}>
            <div className="field">
              <label>Admission No.</label>
              <input required value={form.admission_no}
                onChange={(e) => setForm({ ...form, admission_no: e.target.value })} />
            </div>
            <div className="field">
              <label>First Name</label>
              <input required value={form.first_name}
                onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
            </div>
            <div className="field">
              <label>Last Name</label>
              <input required value={form.last_name}
                onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
            </div>
            <div className="field">
              <label>Date of Birth</label>
              <input type="date" value={form.dob}
                onChange={(e) => setForm({ ...form, dob: e.target.value })} />
            </div>
            <div className="field">
              <label>Gender</label>
              <select value={form.gender} onChange={(e) => setForm({ ...form, gender: e.target.value })}>
                <option value="M">Male</option>
                <option value="F">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>
            <div className="field">
              <label>Class</label>
              <select value={form.class_id} onChange={(e) => setForm({ ...form, class_id: e.target.value })}>
                <option value="">Select class</option>
                {classes.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </div>
            <div className="field">
              <label>Guardian Name</label>
              <input value={form.guardian_name}
                onChange={(e) => setForm({ ...form, guardian_name: e.target.value })} />
            </div>
            <div className="field">
              <label>Guardian Phone</label>
              <input value={form.guardian_phone}
                onChange={(e) => setForm({ ...form, guardian_phone: e.target.value })} />
            </div>
            <button className="btn" type="submit">Register</button>
          </form>
        </div>
      )}

      <div className="card">
        <h2>All Students ({students.length})</h2>
        <DataTable
          rowKey="id"
          rows={students}
          emptyMessage="No students registered yet."
          columns={[
            { key: "admission_no", header: "Admission No." },
            { key: "name", header: "Name", render: (r) => `${r.first_name} ${r.last_name}` },
            { key: "class_name", header: "Class" },
            { key: "guardian_name", header: "Guardian" },
            { key: "status", header: "Status", render: (r) => <span className="badge good">{r.status}</span> },
          ]}
        />
      </div>
    </div>
  );
}
