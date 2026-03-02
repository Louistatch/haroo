import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { register } from "../api/auth";
import { Container } from "../components/Layout";
import { Input, Button, Select } from "../components/Form";

export default function Register() {
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [userType, setUserType] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await register({ phone, password, name, user_type: userType });
      alert("Inscription réussie. Connectez-vous.");
      navigate("/login");
    } catch (err: any) {
      const msg = err?.response?.data?.detail || "Erreur lors de l'inscription";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  const userTypeOptions = [
    { value: "EXPLOITANT", label: "Exploitant Agricole" },
    { value: "AGRONOME", label: "Agronome" },
    { value: "OUVRIER", label: "Ouvrier Agricole" },
    { value: "ACHETEUR", label: "Acheteur" },
  ];

  return (
    <Container>
      <div className="auth-card">
        <h2>Inscription</h2>
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
            label="Nom complet"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Votre nom complet"
            required
          />
          <Input
            label="Numéro de téléphone"
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="Ex: +228 90 12 34 56"
            required
            helpText="Format: +228 suivi de votre numéro"
          />
          <Select
            label="Type de profil"
            value={userType}
            onChange={(e) => setUserType(e.target.value)}
            options={userTypeOptions}
            placeholder="Sélectionnez votre profil"
            required
            helpText="Choisissez le profil qui correspond à votre activité"
          />
          <Input
            label="Mot de passe"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            helpText="Minimum 8 caractères"
          />
          <Button 
            type="submit" 
            loading={loading}
            fullWidth
          >
            S'inscrire
          </Button>
        </form>
        <div className="muted text-center">
          Déjà inscrit? <Link to="/login" style={{ color: 'var(--primary)' }}>Connexion</Link>
        </div>
      </div>
    </Container>
  );
}
