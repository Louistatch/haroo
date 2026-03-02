import React, { useState } from 'react';
import { Container, Grid, Card } from '../components/Layout';
import { Input, Select, TextArea, Button, Checkbox } from '../components/Form';
import { ResponsiveImage } from '../components/ResponsiveImage';
import { useBreakpoint, useIsMobile } from '../hooks/useMediaQuery';

/**
 * Demo page showcasing responsive components
 * This demonstrates all responsive features for the platform
 */
export default function ResponsiveDemo() {
  const [formData, setFormData] = useState({
    name: '',
    region: '',
    description: '',
    acceptTerms: false
  });
  const [loading, setLoading] = useState(false);
  
  const breakpoint = useBreakpoint();
  const isMobile = useIsMobile();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      alert('Formulaire soumis avec succès!');
      setLoading(false);
    }, 2000);
  };

  const regionOptions = [
    { value: 'maritime', label: 'Maritime' },
    { value: 'plateaux', label: 'Plateaux' },
    { value: 'centrale', label: 'Centrale' },
    { value: 'kara', label: 'Kara' },
    { value: 'savanes', label: 'Savanes' }
  ];

  return (
    <Container>
      <div style={{ padding: 'var(--spacing-lg) 0' }}>
        {/* Header Section */}
        <div className="text-center mb-lg">
          <h1>Démonstration du Design Responsive</h1>
          <p className="text-muted">
            Breakpoint actuel: <strong>{breakpoint}</strong> | 
            Mode: <strong>{isMobile ? 'Mobile' : 'Desktop'}</strong>
          </p>
        </div>

        {/* Grid Demo */}
        <section className="mb-lg">
          <h2>Grille Responsive</h2>
          <p className="text-muted mb-md">
            La grille s'adapte automatiquement: 1 colonne sur mobile, 2 sur tablette, 3 sur desktop
          </p>
          <Grid cols={{ xs: 1, sm: 2, md: 3 }} gap="md">
            <Card>
              <h3>Carte 1</h3>
              <p>Contenu de la première carte avec du texte d'exemple.</p>
            </Card>
            <Card>
              <h3>Carte 2</h3>
              <p>Contenu de la deuxième carte avec du texte d'exemple.</p>
            </Card>
            <Card>
              <h3>Carte 3</h3>
              <p>Contenu de la troisième carte avec du texte d'exemple.</p>
            </Card>
          </Grid>
        </section>

        {/* Form Demo */}
        <section className="mb-lg">
          <Card>
            <h2>Formulaire Tactile</h2>
            <p className="text-muted mb-md">
              Tous les champs ont des cibles tactiles de minimum 44px (48px sur mobile)
            </p>
            <form onSubmit={handleSubmit}>
              <Input
                label="Nom complet"
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Entrez votre nom"
                required
                helpText="Votre nom tel qu'il apparaîtra sur votre profil"
              />

              <Select
                label="Région"
                value={formData.region}
                onChange={(e) => setFormData({ ...formData, region: e.target.value })}
                options={regionOptions}
                placeholder="Sélectionnez votre région"
                required
                helpText="Choisissez la région où vous exercez"
              />

              <TextArea
                label="Description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Décrivez votre activité..."
                rows={4}
                helpText="Minimum 20 caractères"
              />

              <Checkbox
                label="J'accepte les conditions générales d'utilisation"
                checked={formData.acceptTerms}
                onChange={(e) => setFormData({ ...formData, acceptTerms: e.target.checked })}
              />

              <div style={{ display: 'flex', gap: 'var(--spacing-md)', flexWrap: 'wrap' }}>
                <Button 
                  type="submit" 
                  variant="primary"
                  loading={loading}
                  style={{ flex: isMobile ? '1 1 100%' : '1' }}
                >
                  Envoyer
                </Button>
                <Button 
                  type="button" 
                  variant="secondary"
                  onClick={() => setFormData({ name: '', region: '', description: '', acceptTerms: false })}
                  style={{ flex: isMobile ? '1 1 100%' : '1' }}
                >
                  Réinitialiser
                </Button>
              </div>
            </form>
          </Card>
        </section>

        {/* Button Variants Demo */}
        <section className="mb-lg">
          <Card>
            <h2>Variantes de Boutons</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
              <Button variant="primary">Bouton Principal</Button>
              <Button variant="secondary">Bouton Secondaire</Button>
              <Button variant="outline">Bouton Outline</Button>
              <Button variant="primary" size="sm">Petit Bouton</Button>
              <Button variant="primary" size="lg">Grand Bouton</Button>
              <Button variant="primary" disabled>Bouton Désactivé</Button>
              <Button variant="primary" loading>Chargement...</Button>
            </div>
          </Card>
        </section>

        {/* Responsive Image Demo */}
        <section className="mb-lg">
          <Card>
            <h2>Images Responsives</h2>
            <p className="text-muted mb-md">
              Les images s'adaptent automatiquement et utilisent le lazy loading
            </p>
            <div style={{ 
              background: 'var(--bg)', 
              padding: 'var(--spacing-lg)',
              borderRadius: '8px',
              textAlign: 'center'
            }}>
              <div style={{ 
                background: '#e5e7eb', 
                height: '200px', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                borderRadius: '8px'
              }}>
                <p className="text-muted">Placeholder pour image responsive</p>
              </div>
              <p className="text-sm text-muted mt-sm">
                Utilisez le composant ResponsiveImage pour les vraies images
              </p>
            </div>
          </Card>
        </section>

        {/* Responsive Utilities Demo */}
        <section className="mb-lg">
          <Card>
            <h2>Classes Utilitaires</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
              <div className="hide-mobile" style={{ padding: 'var(--spacing-md)', background: 'var(--bg)', borderRadius: '8px' }}>
                <strong>Visible uniquement sur desktop</strong>
                <p className="text-sm text-muted">Cette section est cachée sur mobile</p>
              </div>
              
              <div className="hide-desktop" style={{ padding: 'var(--spacing-md)', background: 'var(--bg)', borderRadius: '8px' }}>
                <strong>Visible uniquement sur mobile</strong>
                <p className="text-sm text-muted">Cette section est cachée sur desktop</p>
              </div>
            </div>
          </Card>
        </section>

        {/* Spacing Demo */}
        <section className="mb-lg">
          <Card>
            <h2>Système d'Espacement</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
              <div className="p-sm" style={{ background: 'var(--bg)' }}>Padding Small</div>
              <div className="p-md" style={{ background: 'var(--bg)' }}>Padding Medium</div>
              <div className="p-lg" style={{ background: 'var(--bg)' }}>Padding Large</div>
            </div>
          </Card>
        </section>

        {/* Typography Demo */}
        <section className="mb-lg">
          <Card>
            <h2>Typographie Responsive</h2>
            <h1>Titre H1 - S'adapte à l'écran</h1>
            <h2>Titre H2 - S'adapte à l'écran</h2>
            <h3>Titre H3 - S'adapte à l'écran</h3>
            <p>Paragraphe normal avec taille de police responsive</p>
            <p className="text-sm">Petit texte pour les détails</p>
            <p className="text-lg">Grand texte pour l'emphase</p>
            <p className="text-muted">Texte grisé pour les informations secondaires</p>
          </Card>
        </section>
      </div>
    </Container>
  );
}
