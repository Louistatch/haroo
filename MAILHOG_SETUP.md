# Configuration MailHog pour Tests d'Emails

## 🎯 Objectif

Configurer MailHog pour tester les emails localement sans envoyer de vrais emails.

---

## 📦 Installation MailHog

### Windows (avec Chocolatey)

```bash
# Installer Chocolatey si pas déjà installé
# Voir: https://chocolatey.org/install

# Installer MailHog
choco install mailhog
```

### Windows (sans Chocolatey)

1. Télécharger MailHog: https://github.com/mailhog/MailHog/releases
2. Télécharger `MailHog_windows_amd64.exe`
3. Renommer en `mailhog.exe`
4. Placer dans `C:\Program Files\MailHog\`
5. Ajouter au PATH système

### macOS (avec Homebrew)

```bash
brew install mailhog
```

### Linux

```bash
# Télécharger
wget https://github.com/mailhog/MailHog/releases/download/v1.0.1/MailHog_linux_amd64

# Rendre exécutable
chmod +x MailHog_linux_amd64

# Déplacer vers /usr/local/bin
sudo mv MailHog_linux_amd64 /usr/local/bin/mailhog
```

---

## 🚀 Démarrage MailHog

### Démarrer MailHog

```bash
mailhog
```

**Sortie attendue**:
```
[HTTP] Binding to address: 0.0.0.0:8025
[SMTP] Binding to address: 0.0.0.0:1025
Creating API v1 with WebPath: 
Creating API v2 with WebPath: 
```

### Accéder à l'interface web

Ouvrir dans le navigateur: **http://localhost:8025**

### Ports utilisés

- **Interface web**: http://localhost:8025
- **Serveur SMTP**: localhost:1025

---

## ⚙️ Configuration Django

### Option 1: Modifier haroo/settings/dev.py

Ajouter ou modifier:

```python
# Configuration Email pour MailHog (développement)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
DEFAULT_FROM_EMAIL = 'noreply@haroo.tg'
```

### Option 2: Utiliser .env

Ajouter dans `.env`:

```env
# Email Configuration (MailHog)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=localhost
EMAIL_PORT=1025
EMAIL_USE_TLS=False
EMAIL_USE_SSL=False
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@haroo.tg
```

Et dans `haroo/settings/base.py`:

```python
# Email Configuration
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='localhost')
EMAIL_PORT = env.int('EMAIL_PORT', default=1025)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=False)
EMAIL_USE_SSL = env.bool('EMAIL_USE_SSL', default=False)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@haroo.tg')
```

---

## 🧪 Test de Configuration

### 1. Vérifier que MailHog est démarré

```bash
# Vérifier le processus
# Windows
tasklist | findstr mailhog

# Linux/macOS
ps aux | grep mailhog
```

### 2. Tester l'envoi d'email

```bash
# Activer l'environnement virtuel
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS

# Envoyer les emails de test
python send_test_emails.py
```

### 3. Vérifier dans MailHog

1. Ouvrir http://localhost:8025
2. Vous devriez voir 3 emails:
   - Confirmation d'achat
   - Rappel d'expiration
   - Lien régénéré

---

## 📋 Checklist de Test (Subtask 2.2.10)

### Dans MailHog (localhost:8025)

- [ ] **Email 1: Confirmation d'achat**
  - [ ] Sujet correct
  - [ ] Header avec logo 🌾 et "Haroo"
  - [ ] Tagline "Plateforme Agricole Intelligente du Togo"
  - [ ] Nom utilisateur affiché (Jean Dupont)
  - [ ] Titre document affiché
  - [ ] Bouton "Télécharger" vert
  - [ ] Info box avec détails
  - [ ] Footer avec liens
  - [ ] Copyright "© 2024 Haroo"

- [ ] **Email 2: Rappel d'expiration**
  - [ ] Warning box jaune visible
  - [ ] Temps restant affiché (24h)
  - [ ] Bouton vers historique d'achats
  - [ ] Info sur régénération gratuite

- [ ] **Email 3: Lien régénéré**
  - [ ] Nouveau lien de téléchargement
  - [ ] Nouvelle date d'expiration
  - [ ] Bouton "Télécharger" fonctionnel

### Version Texte (Plain Text)

- [ ] Cliquer sur "Plain Text" dans MailHog
- [ ] Vérifier que le contenu est lisible
- [ ] Tous les liens sont en clair
- [ ] Structure logique préservée

### Tests Optionnels sur Vrais Clients

Si vous voulez tester sur de vrais clients email:

#### Gmail
1. Modifier `to_email` dans `send_test_emails.py`
2. Configurer SMTP Gmail dans settings
3. Envoyer les emails
4. Vérifier sur Gmail web + mobile

#### Outlook
1. Utiliser une adresse Outlook
2. Vérifier sur Outlook web + desktop
3. Tester les boutons et liens

#### Apple Mail
1. Utiliser une adresse iCloud
2. Vérifier sur macOS + iOS
3. Tester le dark mode

---

## 🐛 Dépannage

### MailHog ne démarre pas

**Erreur**: "bind: address already in use"

**Solution**: Un autre processus utilise le port 1025 ou 8025

```bash
# Windows - Trouver le processus
netstat -ano | findstr :1025
netstat -ano | findstr :8025

# Tuer le processus (remplacer PID)
taskkill /PID <PID> /F

# Linux/macOS
lsof -i :1025
lsof -i :8025
kill <PID>
```

### Emails ne s'affichent pas dans MailHog

**Vérifications**:
1. MailHog est bien démarré
2. Configuration Django correcte (EMAIL_HOST=localhost, EMAIL_PORT=1025)
3. Pas d'erreur dans les logs Django
4. Rafraîchir la page MailHog

### Erreur "Connection refused"

**Solution**: MailHog n'est pas démarré ou mauvais port

```bash
# Vérifier que MailHog écoute sur 1025
netstat -an | findstr :1025  # Windows
netstat -an | grep :1025     # Linux/macOS
```

---

## 🎯 Validation Finale

Une fois les tests effectués:

1. **Documenter les résultats**
   - Screenshots des emails dans MailHog
   - Notes sur le rendu
   - Problèmes identifiés (si présents)

2. **Marquer la subtask comme complète**
   ```markdown
   - [x] 2.2.10 Test templates on Gmail, Outlook, Apple Mail
   ```

3. **Passer à la Phase 2.3**
   - Configuration Celery
   - Tâches asynchrones

---

## 📚 Ressources

- **MailHog GitHub**: https://github.com/mailhog/MailHog
- **Documentation Django Email**: https://docs.djangoproject.com/en/4.2/topics/email/
- **Premailer**: https://github.com/peterbe/premailer

---

## ✅ Commandes Rapides

```bash
# Démarrer MailHog
mailhog

# Dans un autre terminal
# Activer venv
.venv\Scripts\activate

# Envoyer emails de test
python send_test_emails.py

# Ouvrir MailHog dans le navigateur
start http://localhost:8025  # Windows
open http://localhost:8025   # macOS
xdg-open http://localhost:8025  # Linux
```

---

**Temps estimé**: 30 minutes - 1 heure
**Difficulté**: Facile
**Prérequis**: MailHog installé, Django configuré
