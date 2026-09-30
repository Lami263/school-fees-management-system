import { Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Students from "./pages/Students";
import FeeStructures from "./pages/FeeStructures";
import Discounts from "./pages/Discounts";
import Payments from "./pages/Payments";
import OutstandingFees from "./pages/OutstandingFees";
import Search from "./pages/Search";
import Reports from "./pages/Reports";
import AuditLog from "./pages/AuditLog";

function Shell({ children }) {
  return (
    <div className="app-shell">
      <Navbar />
      <main className="main">{children}</main>
    </div>
  );
}

function AppRoutes() {
  const { user } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/" replace /> : <Login />} />
      <Route path="/" element={
        <ProtectedRoute><Shell><Dashboard /></Shell></ProtectedRoute>
      } />
      <Route path="/students" element={
        <ProtectedRoute><Shell><Students /></Shell></ProtectedRoute>
      } />
      <Route path="/fee-structures" element={
        <ProtectedRoute><Shell><FeeStructures /></Shell></ProtectedRoute>
      } />
      <Route path="/discounts" element={
        <ProtectedRoute><Shell><Discounts /></Shell></ProtectedRoute>
      } />
      <Route path="/payments" element={
        <ProtectedRoute><Shell><Payments /></Shell></ProtectedRoute>
      } />
      <Route path="/outstanding" element={
        <ProtectedRoute><Shell><OutstandingFees /></Shell></ProtectedRoute>
      } />
      <Route path="/search" element={
        <ProtectedRoute><Shell><Search /></Shell></ProtectedRoute>
      } />
      <Route path="/reports" element={
        <ProtectedRoute><Shell><Reports /></Shell></ProtectedRoute>
      } />
      <Route path="/audit-log" element={
        <ProtectedRoute roles={["admin"]}><Shell><AuditLog /></Shell></ProtectedRoute>
      } />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}
