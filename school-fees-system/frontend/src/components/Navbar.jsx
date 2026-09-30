import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const links = [
  { to: "/", label: "Dashboard", roles: ["admin", "bursar", "parent"] },
  { to: "/students", label: "Students", roles: ["admin", "bursar", "parent"] },
  { to: "/fee-structures", label: "Fee Structure", roles: ["admin", "bursar", "parent"] },
  { to: "/discounts", label: "Discounts", roles: ["admin", "bursar", "parent"] },
  { to: "/payments", label: "Payments", roles: ["admin", "bursar", "parent"] },
  { to: "/outstanding", label: "Outstanding Fees", roles: ["admin", "bursar", "parent"] },
  { to: "/search", label: "Search", roles: ["admin", "bursar", "parent"] },
  { to: "/reports", label: "Reports", roles: ["admin", "bursar", "parent"] },
  { to: "/audit-log", label: "Audit Log", roles: ["admin"] },
];

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav className="sidebar">
      <div className="brand">
        School Fees System
        <small>Payment &amp; QA Demo Project</small>
      </div>
      {links
        .filter((l) => !user || l.roles.includes(user.role))
        .map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            end={l.to === "/"}
            className={({ isActive }) => (isActive ? "active" : "")}
          >
            {l.label}
          </NavLink>
        ))}
      {user && (
        <div className="user-box">
          Signed in as <strong>{user.username}</strong> ({user.role})
          <div>
            <button onClick={logout}>Log out</button>
          </div>
        </div>
      )}
    </nav>
  );
}
