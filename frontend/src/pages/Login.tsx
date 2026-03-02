import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { login } from "../api/auth";
import { Container } from "../components/Layout";
import { Input, Button } from "../components/Form";

export default function Login() {
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await login(phone, password);
      navigate("/home");
    } catch (err: any) {
      const msg = err?.response?.data?.detail || "Échec de la connexion";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Container>
      <div className="auth-card">
        <h2>Connexion</h2>
        {error && (
          <div style={{ 
            padding: 'var(--spacing-md)', 
            background: '#fee', 
            color: 'var(--error)', 
            borderRadius: '8px',
            marginBottom: 'var(--spacing-md)'
          }}>
            {error}
          </div>
        )}
        <form onSubmit={handleSubmit}>
          <Input
            label="Numéro de téléphone"
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="Ex: +228 90 12 34 56"
            required
            helpText="Format: +228 suivi de votre numéro"
          />
          <Input
            label="Mot de passe"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <Button 
            type="submit" 
            loading={loading}
            fullWidth
          >
            Se connecter
          </Button>
        </form>
        <div className="muted text-center">
          Pas de compte? <Link to="/register" style={{ color: 'var(--primary)' }}>Inscription</Link>
        </div>
      </div>
    </Container>
  );
}
