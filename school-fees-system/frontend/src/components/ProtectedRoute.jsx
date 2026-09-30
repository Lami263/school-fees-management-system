import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute({ children, roles }) {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (roles && !roles.includes(user.role)) {
    return (
      <div className="card">
        <h2>Access restricted</h2>
        <p>Your role ({user.role}) does not have permission to view this page.</p>
      </div>
    );
  }

  return children;
}
