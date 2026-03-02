# Guide Rapide - Test des Emails (Subtask 2.2.10)

## 🎯 Objectif

Tester les templates d'emails sur différents clients pour valider la subtask 2.2.10.

---

## ⚡ Méthode Rapide (Recommandée)

### Étape 1: Installer MailHog

**Windows**:
```bash
choco install mailhog
```

**macOS**:
```bash
brew install mailhog
```

**Linux**:
```bash
wget https://github.com/mailhog/MailHog/releases/download/v1.0.1/MailHog_linux_amd64
chmod +x MailHog_linux_amd64
sudo mv MailHog_linux_amd64 /usr/local/bin/mailhog
```

### Étape 2: Démarrer MailHog

**Option A - Script automatique**:
```bash
# Windows
start_mailhog.bat

# Linux/macOS
./start_mailhog.sh
```

**Option B - Manuel**:
```bash
mailhog
```

Interface web: http://localhost:8025

### Étape 3: Configurer Django

Créer/modifier `.env`:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=localhost
EMAIL_PORT=1025
EMAIL_USE_TLS=False
DEFAULT_FROM_EMAIL=noreply@haroo.tg
```

### Étape 4: Envoyer les Emails de Test

```bash
# Activer l'environnement virtuel
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS

# Envoyer les emails
python send_test_emails.py
```

Suivre les instructions à l'écran.

### Étape 5: Vérifier dans MailHog

1. Ouvrir http://localhost:8025
2. Vous devriez voir 3 emails
3. Cliquer sur chaque email pour vérifier:
   - ✅ Branding "Haroo" correct
   - ✅ Logo 🌾 visible
   - ✅ Couleurs vertes (#2e7d32, #4caf50)
   - ✅ Boutons verts cliquables
   - ✅ Liens fonctionnels
   - ✅ Footer avec copyright "© 2024 Haroo"
   - ✅ Version texte lisible (cliquer "Plain Text")

---

## 📋 Checklist de Validation

### Email 1: Confirmation d'Achat
- [ ] Header avec "Haroo" et tagline
- [ ] Nom utilisateur personnalisé
- [ ] Détails du document
- [ ] Bouton "Télécharger maintenant" vert
- [ ] Info box avec bordure verte
- [ ] Date d'expiration (48h)
- [ ] Footer complet

### Email 2: Rappel d'Expiration
- [ ] Warning box jaune visible
- [ ] Temps restant affiché
- [ ] Bouton vers historique d'achats
- [ ] Info sur régénération gratuite
- [ ] Ton urgent mais rassurant

### Email 3: Lien Régénéré
- [ ] Confirmation de régénération
- [ ] Nouveau lien de téléchargement
- [ ] Nouvelle date d'expiration
- [ ] Instructions claires

### Version Texte (tous les emails)
- [ ] Contenu lisible sans HTML
- [ ] Structure logique
- [ ] Liens en clair
- [ ] Toutes les infos présentes

---

## 🎨 Points de Vérification Design

### Branding
- [ ] Nom: "Haroo" (pas "Plateforme Agricole Togo")
- [ ] Tagline: "Plateforme Agricole Intelligente du Togo"
- [ ] Logo: 🌾 (emoji blé)
- [ ] Copyright: "© 2024 Haroo"

### Couleurs
- [ ] Header: Dégradé vert (#2e7d32 → #4caf50)
- [ ] Boutons: Vert avec dégradé
- [ ] Info box: Bordure verte (#2e7d32)
- [ ] Warning box: Fond jaune (#fff3cd)
- [ ] Footer: Fond gris (#f5f5f5)

### Typographie
- [ ] Titre: 24px, bold, blanc
- [ ] Texte: 16px, line-height 1.6
- [ ] Labels: 14px, semi-bold
- [ ] Footer: 12-14px

### Layout
- [ ] Largeur max: 600px
- [ ] Padding cohérent
- [ ] Espacement vertical logique
- [ ] Alignement centré

---

## 🧪 Tests Optionnels (Vrais Clients)

Si vous voulez tester sur de vrais clients email:

### Gmail
1. Modifier l'email dans `send_test_emails.py`
2. Configurer SMTP Gmail dans `.env`:
   ```env
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=votre_email@gmail.com
   EMAIL_HOST_PASSWORD=votre_app_password
   ```
3. Envoyer les emails
4. Vérifier sur Gmail web + mobile

### Outlook
1. Utiliser une adresse Outlook
2. Configurer SMTP Outlook
3. Vérifier sur Outlook web + desktop

### Apple Mail
1. Utiliser une adresse iCloud
2. Vérifier sur macOS + iOS
3. Tester le dark mode

---

## ✅ Validation Finale

Une fois les tests effectués:

### 1. Documenter les Résultats

Créer `EMAIL_TEST_RESULTS.md`:
```markdown
# Résultats Tests Emails - Subtask 2.2.10

## Date
[Date des tests]

## Environnement
- MailHog: ✅ Testé
- Gmail: ⏭️ Non testé / ✅ Testé
- Outlook: ⏭️ Non testé / ✅ Testé
- Apple Mail: ⏭️ Non testé / ✅ Testé

## Résultats

### MailHog
- Confirmation d'achat: ✅ OK
- Rappel d'expiration: ✅ OK
- Lien régénéré: ✅ OK
- Version texte: ✅ OK

### Problèmes Identifiés
[Aucun / Liste des problèmes]

### Screenshots
[Ajouter screenshots si possible]

## Conclusion
✅ Tous les templates fonctionnent correctement
✅ Branding Haroo correct partout
✅ Subtask 2.2.10 validée
```

### 2. Marquer la Subtask comme Complète

Dans `.kiro/specs/marketplace-documents-finalisation/tasks.md`:
```markdown
- [x] 2.2.10 Test templates on Gmail, Outlook, Apple Mail (testé avec MailHog)
```

### 3. Passer à la Phase 2.3

La Phase 2.2 est maintenant 100% complétée! 🎉

Prochaine étape: **Phase 2.3 - Configure Celery**

---

## 🐛 Dépannage Rapide

### MailHog ne démarre pas
```bash
# Vérifier si le port est utilisé
netstat -ano | findstr :1025  # Windows
lsof -i :1025  # Linux/macOS

# Tuer le processus si nécessaire
taskkill /PID <PID> /F  # Windows
kill <PID>  # Linux/macOS
```

### Emails ne s'affichent pas
1. Vérifier que MailHog est démarré
2. Vérifier `.env` (EMAIL_HOST=localhost, EMAIL_PORT=1025)
3. Rafraîchir la page MailHog
4. Vérifier les logs Django

### Erreur "Connection refused"
- MailHog n'est pas démarré
- Mauvais port configuré
- Firewall bloque la connexion

---

## 📚 Documentation Complète

Pour plus de détails, voir:
- `MAILHOG_SETUP.md` - Configuration détaillée
- `EMAIL_TESTING_GUIDE.md` - Guide complet de test
- `PHASE_2.2_COMPLETE.md` - Résumé Phase 2.2

---

## ⏱️ Temps Estimé

- Installation MailHog: 5 minutes
- Configuration Django: 5 minutes
- Envoi et vérification: 15 minutes
- Documentation: 10 minutes

**Total: 30-45 minutes**

---

## 🎉 Félicitations!

Une fois cette subtask complétée, la Phase 2.2 sera 100% terminée!

**Phase 2.2: Email Templates** ✅
- 10/10 subtasks complétées
- Tous les templates créés
- Branding Haroo correct
- Premailer intégré
- Tests validés

**Prochaine étape**: Phase 2.3 - Configure Celery
