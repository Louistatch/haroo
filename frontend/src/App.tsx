import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Profile from "./pages/Profile";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import Documents from "./pages/Documents";
import Agronomists from "./pages/Agronomists";
import ProtectedRoute from "./components/ProtectedRoute";
import Header from "./components/Header";

function isAuthenticated() {
  return Boolean(localStorage.getItem("access_token"));
}

export default function App() {
  return (
    <div>
      <Header isAuthenticated={isAuthenticated()} />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/home" element={<ProtectedRoute><Home /></ProtectedRoute>} />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/documents" element={<Documents />} />
        <Route path="/agronomists" element={<Agronomists />} />
        <Route path="/me" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}
