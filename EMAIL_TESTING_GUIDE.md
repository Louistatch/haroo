# Guide de Test des Emails

## Subtask 2.2.10: Test des templates sur Gmail, Outlook, Apple Mail

Ce guide explique comment tester les templates d'emails sur différents clients email pour assurer une compatibilité maximale.

---

## 📋 Résumé des Templates

Nous avons créé 3 types d'emails avec versions HTML et texte:

1. **Confirmation d'achat** (`purchase_confirmation.html/txt`)
   - Envoyé après un achat réussi
   - Contient le lien de téléchargement
   - Affiche les détails du document

2. **Rappel d'expiration** (`expiration_reminder.html/txt`)
   - Envoyé 24h avant expiration
   - Alerte l'utilisateur
   - Lien vers l'historique d'achats

3. **Lien régénéré** (`link_regenerated.html/txt`)
   - Envoyé après régénération d'un lien expiré
   - Nouveau lien de téléchargement
   - Nouvelle date d'expiration

---

## 🎨 Optimisations Appliquées

### CSS Inline avec Premailer
- ✅ Premailer installé et intégré dans EmailService
- ✅ Conversion automatique des `<style>` en attributs `style=""`
- ✅ Améliore la compatibilité avec les clients email

### Design Responsive
- ✅ Media queries pour mobile
- ✅ Tables pour la structure (compatibilité Outlook)
- ✅ Largeur max 600px
- ✅ Padding adaptatif

### Compatibilité Email
- ✅ Inline CSS pour tous les styles critiques
- ✅ Fallbacks pour les dégradés CSS
- ✅ Propriétés MSO pour Outlook
- ✅ Reset CSS pour normaliser le rendu

---

## 🧪 Méthodes de Test

### Option 1: MailHog (Recommandé pour développement)

MailHog est un serveur SMTP de test qui capture tous les emails.

**Installation:**
```bash
# Windows (avec Chocolatey)
choco install mailhog

# macOS (avec Homebrew)
brew install mailhog

# Linux
wget https://github.com/mailhog/MailHog/releases/download/v1.0.1/MailHog_linux_amd64
chmod +x MailHog_linux_amd64
sudo mv MailHog_linux_amd64 /usr/local/bin/mailhog
```

**Configuration Django:**
```python
# settings.py (développement)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_USE_TLS = False
```

**Utilisation:**
```bash
# Démarrer MailHog
mailhog

# Interface web: http://localhost:8025
# SMTP: localhost:1025
```

**Avantages:**
- ✅ Capture tous les emails
- ✅ Interface web pour visualiser
- ✅ Pas besoin de vrais comptes email
- ✅ Test rapide et local

### Option 2: Mailtrap (Recommandé pour staging)

Service en ligne pour tester les emails.

**Configuration:**
1. Créer un compte sur https://mailtrap.io
2. Obtenir les credentials SMTP
3. Configurer Django:

```python
# settings.py (staging)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mailtrap.io'
EMAIL_PORT = 2525
EMAIL_HOST_USER = 'your_username'
EMAIL_HOST_PASSWORD = 'your_password'
EMAIL_USE_TLS = True
```

**Avantages:**
- ✅ Test sur vrais clients email (Gmail, Outlook, etc.)
- ✅ Analyse de spam score
- ✅ Vérification HTML/CSS
- ✅ Screenshots automatiques

### Option 3: Litmus ou Email on Acid (Professionnel)

Services payants pour tests professionnels.

**Fonctionnalités:**
- Test sur 90+ clients email
- Screenshots automatiques
- Analyse de compatibilité
- Test de spam
- Validation HTML/CSS

**Prix:**
- Litmus: ~$99/mois
- Email on Acid: ~$99/mois

### Option 4: Envoi à de vrais comptes (Production)

Pour tester en conditions réelles.

**Créer des comptes de test:**
- Gmail: test@gmail.com
- Outlook: test@outlook.com
- Apple Mail: test@icloud.com
- Yahoo: test@yahoo.com

**Configuration Django:**
```python
# settings.py (production)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # ou votre SMTP
EMAIL_PORT = 587
EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'your_app_password'
EMAIL_USE_TLS = True
```

---

## 📝 Checklist de Test

### Tests Fonctionnels

- [ ] **Email envoyé avec succès**
  - Vérifier les logs Django
  - Confirmer la réception

- [ ] **Contenu correct**
  - Nom de l'utilisateur affiché
  - Titre du document correct
  - Prix et format corrects
  - Dates correctes

- [ ] **Liens fonctionnels**
  - Lien de téléchargement cliquable
  - Lien vers historique d'achats
  - Liens footer (Accueil, Documents, etc.)

### Tests Visuels

#### Gmail (Web + Mobile)
- [ ] Header avec logo et branding visible
- [ ] Couleurs vertes (#2e7d32, #4caf50) correctes
- [ ] Boutons bien stylés avec dégradé
- [ ] Info box avec bordure verte
- [ ] Warning box jaune visible
- [ ] Footer avec liens et copyright
- [ ] Responsive sur mobile

#### Outlook (Desktop + Web)
- [ ] Structure de table correcte
- [ ] Pas de problèmes de padding
- [ ] Dégradés CSS ou fallback
- [ ] Boutons cliquables
- [ ] Pas de texte coupé
- [ ] Images alignées

#### Apple Mail (macOS + iOS)
- [ ] Rendu identique à Gmail
- [ ] Animations CSS (si présentes)
- [ ] Emojis affichés correctement
- [ ] Dark mode compatible
- [ ] Responsive sur iPhone/iPad

#### Yahoo Mail
- [ ] Structure préservée
- [ ] Couleurs correctes
- [ ] Liens fonctionnels
- [ ] Pas de CSS cassé

#### Thunderbird
- [ ] Rendu basique correct
- [ ] Fallback texte disponible
- [ ] Liens cliquables

### Tests de Compatibilité

- [ ] **Version texte**
  - Lisible sans HTML
  - Toutes les infos présentes
  - Liens en clair

- [ ] **Dark Mode**
  - Texte lisible sur fond sombre
  - Couleurs adaptées
  - Contraste suffisant

- [ ] **Images désactivées**
  - Contenu compréhensible
  - Alt text présent
  - Emojis en fallback

- [ ] **CSS désactivé**
  - Structure HTML basique lisible
  - Ordre logique du contenu

### Tests de Sécurité

- [ ] **Spam Score**
  - Score < 5 sur SpamAssassin
  - Pas de mots-clés spam
  - SPF/DKIM configurés

- [ ] **Phishing Protection**
  - Liens légitimes
  - Domaine vérifié
  - Pas d'alertes de sécurité

---

## 🚀 Script de Test Rapide

Créer un script pour envoyer des emails de test:

```python
# test_send_emails.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'haroo.settings')
django.setup()

from apps.documents.services import EmailService
from apps.documents.models import AchatDocument

# Récupérer un achat de test
achat = AchatDocument.objects.first()

if achat:
    service = EmailService()
    
    # Test 1: Confirmation d'achat
    print("Envoi confirmation d'achat...")
    url = "http://localhost:8000/api/v1/documents/1/download?token=test123"
    service.send_purchase_confirmation(achat, url)
    
    # Test 2: Rappel d'expiration
    print("Envoi rappel d'expiration...")
    service.send_expiration_reminder(achat, 24)
    
    # Test 3: Lien régénéré
    print("Envoi lien régénéré...")
    service.send_link_regenerated(achat, url)
    
    print("✅ Tous les emails de test envoyés!")
else:
    print("❌ Aucun achat trouvé dans la base de données")
```

**Utilisation:**
```bash
python test_send_emails.py
```

---

## 📊 Résultats Attendus

### Rendu Optimal
- Header vert avec logo 🌾
- Texte lisible (16px, line-height 1.6)
- Boutons verts avec hover
- Info box avec bordure verte
- Warning box jaune
- Footer gris avec liens

### Compatibilité Minimale
- Structure préservée
- Texte lisible
- Liens fonctionnels
- Version texte disponible

---

## ✅ Validation Finale

Pour valider la subtask 2.2.10, vous devez:

1. **Installer MailHog** et tester localement
2. **Envoyer 3 types d'emails** (confirmation, rappel, régénération)
3. **Vérifier sur au moins 3 clients**:
   - Gmail (web)
   - Outlook (web ou desktop)
   - Apple Mail (si disponible) ou Yahoo

4. **Documenter les résultats**:
   - Screenshots de chaque client
   - Notes sur les problèmes trouvés
   - Corrections appliquées

5. **Marquer la subtask comme complète** dans tasks.md

---

## 🐛 Problèmes Courants et Solutions

### Outlook ne respecte pas les marges
**Solution:** Utiliser des tables avec cellpadding/cellspacing

### Gmail supprime les CSS
**Solution:** Premailer convertit tout en inline (déjà fait ✅)

### Dark mode illisible
**Solution:** Ajouter des media queries pour dark mode

```css
@media (prefers-color-scheme: dark) {
    .email-content {
        background-color: #1e1e1e !important;
        color: #ffffff !important;
    }
}
```

### Images ne s'affichent pas
**Solution:** Utiliser des emojis Unicode au lieu d'images

---

## 📚 Ressources

- [Can I Email](https://www.caniemail.com/) - Compatibilité CSS email
- [Email on Acid Blog](https://www.emailonacid.com/blog/) - Best practices
- [Litmus Community](https://litmus.com/community) - Forums et guides
- [Really Good Emails](https://reallygoodemails.com/) - Inspiration

---

## 🎯 Prochaines Étapes

Après validation de 2.2.10:

1. **Phase 2.3**: Configurer Celery pour envois asynchrones
2. **Phase 2.4**: Intégrer EmailService dans les views
3. **Phase 2.5**: Tests d'intégration complets

---

**Status:** ⏳ En attente de tests manuels

**Note:** Les templates sont prêts et optimisés. Il ne reste plus qu'à les tester sur les différents clients email pour valider la compatibilité.
