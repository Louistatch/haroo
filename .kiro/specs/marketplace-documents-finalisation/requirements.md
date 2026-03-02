# Requirements Document: Finalisation Marketplace Documents Techniques

## Overview

Ce document spécifie les exigences fonctionnelles et non-fonctionnelles pour finaliser la marketplace de vente de documents techniques agricoles. Le système permet aux agriculteurs togolais d'acheter des documents techniques (comptes d'exploitation, itinéraires techniques) via paiement Fedapay, avec téléchargement sécurisé et gestion d'historique.

## Functional Requirements

### FR1: Purchase History Page

**FR1.1**: Le système DOIT afficher une page d'historique des achats accessible à `/purchases/history`

**FR1.2**: La page d'historique DOIT afficher pour chaque achat:
- Titre du document
- Culture associée
- Prix payé
- Format du fichier (Excel/Word)
- Statut de la transaction (Payé/En attente/Échoué)
- Date d'achat
- Nombre de téléchargements effectués
- Date d'expiration du lien
- Statut du lien (Valide/Expiré)

**FR1.3**: Le système DOIT permettre de filtrer les achats par:
- Plage de dates (date_debut, date_fin)
- Culture (recherche partielle)
- Statut de transaction (SUCCESS, PENDING, FAILED)
- Statut du lien (expiré/valide)

**FR1.4**: Le système DOIT afficher un bouton "Télécharger" pour les achats avec lien valide

**FR1.5**: Le système DOIT afficher un bouton "Régénérer lien" pour les achats avec lien expiré et paiement réussi

**FR1.6**: Le système DOIT afficher un badge visuel indiquant le statut:
- Badge vert "Payé" pour SUCCESS
- Badge orange "En attente" pour PENDING
- Badge rouge "Échoué" pour FAILED
- Badge rouge "Expiré" pour lien expiré

**FR1.7**: Le système DOIT paginer les résultats (20 achats par page)


### FR2: Payment Success Page

**FR2.1**: Le système DOIT afficher une page de confirmation après paiement réussi accessible à `/payment-success`

**FR2.2**: La page DOIT récupérer le transaction_id depuis les paramètres URL

**FR2.3**: Le système DOIT vérifier le statut de la transaction via l'API backend

**FR2.4**: La page DOIT afficher:
- Animation/icône de succès
- Titre du document acheté
- Culture et prix
- Format du fichier
- Date d'expiration du lien (48h)

**FR2.5**: La page DOIT fournir un bouton de téléchargement immédiat

**FR2.6**: La page DOIT fournir un lien vers l'historique des achats

**FR2.7**: Si le paiement a échoué, le système DOIT:
- Afficher un message d'erreur clair
- Rediriger vers la page des documents après 5 secondes
- Permettre de réessayer l'achat

**FR2.8**: Si le transaction_id est manquant ou invalide, le système DOIT rediriger vers `/documents`

### FR3: Link Regeneration

**FR3.1**: Le système DOIT permettre la régénération d'un lien expiré via POST `/api/v1/purchases/history/{id}/regenerate-link`

**FR3.2**: La régénération DOIT créer un nouveau token unique de 32+ caractères

**FR3.3**: Le nouveau lien DOIT être valide pour 48 heures à partir de la régénération

**FR3.4**: Le système DOIT invalider l'ancien token lors de la régénération

**FR3.5**: La régénération DOIT être autorisée uniquement si:
- L'utilisateur est le propriétaire de l'achat
- Le statut de la transaction est SUCCESS
- L'utilisateur est authentifié

**FR3.6**: Le système DOIT retourner le nouveau lien et la date d'expiration

**FR3.7**: Le système DOIT envoyer un email avec le nouveau lien

### FR4: Email Notifications

**FR4.1**: Le système DOIT envoyer un email de confirmation immédiatement après un achat réussi

**FR4.2**: L'email de confirmation DOIT contenir:
- Nom de l'utilisateur
- Titre et détails du document
- Prix payé
- Lien de téléchargement sécurisé
- Date d'expiration du lien
- ID de transaction
- Lien vers l'historique des achats

**FR4.3**: Le système DOIT envoyer un email de rappel 24 heures avant l'expiration du lien

**FR4.4**: L'email de rappel DOIT être envoyé uniquement si:
- Le lien n'a pas encore été utilisé (nombre_telechargements = 0)
- Le statut de la transaction est SUCCESS
- Le lien expire dans 24h ± 1h

**FR4.5**: Le système DOIT envoyer un email après régénération de lien contenant:
- Nouveau lien de téléchargement
- Nouvelle date d'expiration
- Rappel des détails du document

**FR4.6**: Tous les emails DOIVENT utiliser des templates HTML professionnels

**FR4.7**: Les emails DOIVENT être envoyés de manière asynchrone (non-bloquante)

**FR4.8**: Les échecs d'envoi d'email NE DOIVENT PAS bloquer le processus d'achat

**FR4.9**: Le système DOIT logger tous les envois d'emails (succès et échecs)


### FR5: Admin Interface Improvements

**FR5.1**: L'interface admin DOIT afficher les statistiques suivantes sur la page des achats:
- Nombre total de ventes (statut SUCCESS)
- Revenus totaux
- Nombre total de téléchargements

**FR5.2**: L'admin DOIT permettre de filtrer les achats par:
- Statut de transaction
- Statut du lien (expiré/valide)
- Plage de dates
- Culture du document
- Région du document

**FR5.3**: L'admin DOIT permettre la recherche par:
- Email de l'acheteur
- Nom de l'acheteur
- Titre du document
- ID de transaction

**FR5.4**: L'admin DOIT afficher pour chaque achat:
- Lien vers le profil de l'acheteur
- Lien vers le document
- Montant formaté en FCFA
- Badge de statut coloré (vert/orange/rouge)
- Statut du lien (valide/expiré) avec icône

**FR5.5**: L'admin DOIT fournir une action en masse "Régénérer les liens" pour:
- Sélectionner plusieurs achats
- Régénérer les liens expirés
- Afficher le nombre de liens régénérés

**FR5.6**: L'admin DOIT fournir une action "Exporter en CSV" incluant:
- Toutes les colonnes visibles
- Filtres appliqués
- Format compatible Excel

**FR5.7**: L'admin des DocumentTechnique DOIT afficher:
- Nombre d'achats par document
- Lien vers les achats associés
- Actions en masse: activer/désactiver documents

**FR5.8**: L'admin des DocumentTemplate DOIT fournir:
- Action "Dupliquer template" avec incrémentation de version
- Affichage des variables requises en lecture seule

### FR6: Documents Page Improvements

**FR6.1**: La page Documents DOIT afficher un indicateur si l'utilisateur a déjà acheté un document

**FR6.2**: Le système DOIT afficher une modal de confirmation avant l'achat contenant:
- Détails complets du document
- Prix
- Informations du template
- Bouton "Confirmer l'achat"
- Bouton "Annuler"

**FR6.3**: Le système DOIT afficher des notifications toast pour:
- Succès de l'initialisation d'achat
- Erreurs de paiement
- Erreurs réseau
- Document déjà acheté

**FR6.4**: Le système DOIT afficher des skeleton loaders pendant le chargement

**FR6.5**: Si l'utilisateur a déjà acheté le document, le bouton DOIT afficher "Télécharger" au lieu de "Acheter"


## Non-Functional Requirements

### NFR1: Performance

**NFR1.1**: La page d'historique des achats DOIT se charger en moins de 2 secondes pour 100 achats

**NFR1.2**: Les filtres DOIVENT être débounced avec un délai de 300ms

**NFR1.3**: Les requêtes API DOIVENT utiliser select_related() pour éviter les requêtes N+1

**NFR1.4**: Les listes DOIVENT être paginées (20 éléments par page)

**NFR1.5**: Les emails DOIVENT être envoyés de manière asynchrone (temps de réponse API < 500ms)

**NFR1.6**: Le téléchargement de fichiers DOIT utiliser X-Accel-Redirect (Nginx) pour optimiser les performances

### NFR2: Security

**NFR2.1**: Les tokens de téléchargement DOIVENT avoir au moins 256 bits d'entropie (32 caractères URL-safe)

**NFR2.2**: Les tokens DOIVENT être générés avec secrets.token_urlsafe() (cryptographiquement sécurisé)

**NFR2.3**: Le système DOIT vérifier que l'utilisateur est le propriétaire avant tout téléchargement

**NFR2.4**: Le système DOIT vérifier que le paiement est confirmé (statut SUCCESS) avant tout téléchargement

**NFR2.5**: Le système DOIT vérifier l'expiration du lien avant tout téléchargement

**NFR2.6**: Le système DOIT logger toutes les tentatives de téléchargement non autorisées avec IP

**NFR2.7**: Le système DOIT implémenter un rate limiting de 10 téléchargements par heure par utilisateur

**NFR2.8**: Les webhooks Fedapay DOIVENT vérifier les signatures

**NFR2.9**: Les adresses email DOIVENT être validées avant l'envoi

**NFR2.10**: Les tokens DOIVENT être masqués dans l'interface admin

### NFR3: Reliability

**NFR3.1**: Les échecs d'envoi d'email NE DOIVENT PAS empêcher la finalisation de l'achat

**NFR3.2**: Les emails échoués DOIVENT être réessayés 3 fois avec backoff exponentiel

**NFR3.3**: Le système DOIT logger tous les échecs avec contexte complet

**NFR3.4**: Les transactions de base de données DOIVENT être atomiques

**NFR3.5**: Le système DOIT gérer gracieusement les pannes de Fedapay

### NFR4: Usability

**NFR4.1**: Les messages d'erreur DOIVENT être clairs et en français

**NFR4.2**: Les dates DOIVENT être formatées au format français (DD/MM/YYYY HH:MM)

**NFR4.3**: Les montants DOIVENT être formatés avec séparateurs de milliers (ex: 5 000 FCFA)

**NFR4.4**: Les badges de statut DOIVENT utiliser des couleurs intuitives:
- Vert pour succès/valide
- Orange pour en attente
- Rouge pour échec/expiré

**NFR4.5**: Les boutons DOIVENT avoir des états de chargement visuels

**NFR4.6**: Les formulaires DOIVENT valider les entrées côté client avant soumission

**NFR4.7**: Le système DOIT afficher des confirmations pour les actions destructives


### NFR5: Maintainability

**NFR5.1**: Le code frontend DOIT utiliser TypeScript avec types stricts

**NFR5.2**: Le code backend DOIT inclure des docstrings pour toutes les fonctions publiques

**NFR5.3**: Les composants React DOIVENT être fonctionnels avec hooks

**NFR5.4**: Le code DOIT suivre les conventions PEP 8 (Python) et ESLint (TypeScript)

**NFR5.5**: Les services DOIVENT être testables unitairement (injection de dépendances)

**NFR5.6**: Les templates d'email DOIVENT être séparés du code (fichiers .html et .txt)

### NFR6: Scalability

**NFR6.1**: Le système DOIT supporter 1000 achats simultanés

**NFR6.2**: Le système DOIT supporter 10 000 utilisateurs actifs

**NFR6.3**: La base de données DOIT avoir des index appropriés pour les requêtes fréquentes

**NFR6.4**: Le système DOIT utiliser Redis pour le cache

**NFR6.5**: Les tâches asynchrones DOIVENT utiliser Celery avec Redis comme broker

### NFR7: Compatibility

**NFR7.1**: Le frontend DOIT être compatible avec:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**NFR7.2**: Le frontend DOIT être responsive (mobile, tablette, desktop)

**NFR7.3**: Les emails DOIVENT être compatibles avec:
- Gmail
- Outlook
- Apple Mail
- Clients mobiles

**NFR7.4**: Le backend DOIT être compatible avec:
- Python 3.10+
- Django 4.2+
- PostgreSQL 12+

### NFR8: Monitoring and Logging

**NFR8.1**: Le système DOIT logger tous les achats avec:
- ID utilisateur
- ID document
- ID transaction
- Timestamp
- Montant

**NFR8.2**: Le système DOIT logger tous les téléchargements avec:
- ID achat
- Adresse IP
- Timestamp
- User agent

**NFR8.3**: Le système DOIT logger tous les envois d'email avec:
- ID achat
- Destinataire
- Type d'email
- Statut (succès/échec)
- Timestamp

**NFR8.4**: Les erreurs DOIVENT être loggées avec stack trace complète

**NFR8.5**: Les logs DOIVENT être structurés (JSON) pour faciliter l'analyse


## Acceptance Criteria

### AC1: Purchase History Page

**Given** un utilisateur authentifié avec des achats
**When** l'utilisateur accède à `/purchases/history`
**Then** le système affiche la liste de tous ses achats avec:
- Titre, culture, prix, format
- Statut de transaction avec badge coloré
- Statut du lien (valide/expiré)
- Nombre de téléchargements
- Date d'achat et d'expiration

**Given** un utilisateur avec un lien expiré
**When** l'utilisateur clique sur "Régénérer lien"
**Then** le système:
- Génère un nouveau token unique
- Met à jour l'expiration à +48h
- Affiche le nouveau lien
- Envoie un email de confirmation
- Affiche une notification de succès

**Given** un utilisateur avec un lien valide
**When** l'utilisateur clique sur "Télécharger"
**Then** le système:
- Ouvre le téléchargement dans un nouvel onglet
- Incrémente le compteur de téléchargements
- Enregistre un DownloadLog avec IP et timestamp

**Given** un utilisateur appliquant des filtres
**When** l'utilisateur sélectionne culture="Maïs" et lien_expire=true
**Then** le système affiche uniquement les achats de maïs avec lien expiré

### AC2: Payment Success Page

**Given** un paiement Fedapay réussi
**When** Fedapay redirige vers `/payment-success?transaction_id=xxx`
**Then** le système:
- Vérifie le statut de la transaction
- Affiche une animation de succès
- Affiche les détails du document
- Fournit un bouton de téléchargement immédiat
- Affiche la date d'expiration (48h)
- Fournit un lien vers l'historique

**Given** un paiement Fedapay échoué
**When** Fedapay redirige avec statut FAILED
**Then** le système:
- Affiche un message d'erreur clair
- Redirige vers `/documents` après 5 secondes
- Permet de réessayer l'achat

**Given** un transaction_id invalide ou manquant
**When** l'utilisateur accède à `/payment-success`
**Then** le système redirige immédiatement vers `/documents`

### AC3: Email Notifications

**Given** un achat réussi
**When** le statut de la transaction passe à SUCCESS
**Then** le système:
- Envoie un email de confirmation dans les 5 minutes
- L'email contient le lien de téléchargement
- L'email contient la date d'expiration
- L'email est en HTML avec fallback texte
- L'envoi est loggé

**Given** un lien expirant dans 24h
**When** la tâche Celery s'exécute
**Then** le système:
- Identifie les achats avec expiration dans 24h ± 1h
- Filtre ceux non encore téléchargés
- Envoie un email de rappel
- Marque l'email comme envoyé pour éviter les doublons

**Given** une régénération de lien
**When** l'utilisateur régénère un lien expiré
**Then** le système:
- Envoie un email avec le nouveau lien
- L'email contient la nouvelle date d'expiration
- L'envoi est loggé


### AC4: Admin Interface

**Given** un administrateur connecté
**When** l'admin accède à la page des achats
**Then** le système affiche:
- Statistiques: total ventes, revenus, téléchargements
- Liste des achats avec badges colorés
- Filtres par statut, date, culture, région
- Recherche par acheteur, document, transaction

**Given** un admin sélectionnant plusieurs achats
**When** l'admin choisit l'action "Régénérer les liens"
**Then** le système:
- Régénère les liens pour tous les achats SUCCESS
- Affiche le nombre de liens régénérés
- Envoie des emails aux utilisateurs concernés

**Given** un admin avec des filtres appliqués
**When** l'admin clique sur "Exporter en CSV"
**Then** le système:
- Génère un fichier CSV avec les achats filtrés
- Inclut toutes les colonnes visibles
- Format compatible Excel
- Télécharge automatiquement

### AC5: Documents Page Improvements

**Given** un utilisateur ayant déjà acheté un document
**When** l'utilisateur consulte la page des documents
**Then** le système:
- Affiche un badge "Déjà acheté" sur le document
- Change le bouton en "Télécharger"
- Clique sur "Télécharger" ouvre le téléchargement direct

**Given** un utilisateur cliquant sur "Acheter"
**When** le document n'est pas encore acheté
**Then** le système:
- Affiche une modal de confirmation
- La modal contient les détails complets
- Boutons "Confirmer" et "Annuler"
- "Confirmer" initie le paiement Fedapay

**Given** une erreur lors de l'achat
**When** l'API retourne une erreur
**Then** le système:
- Affiche une notification toast d'erreur
- Le message est clair et en français
- L'utilisateur peut réessayer

## Data Requirements

### DR1: Database Schema

**DR1.1**: Le modèle AchatDocument DOIT avoir les champs:
- acheteur (ForeignKey vers User)
- document (ForeignKey vers DocumentTechnique)
- transaction (OneToOneField vers Transaction)
- lien_telechargement (CharField, max 500)
- expiration_lien (DateTimeField, nullable)
- nombre_telechargements (IntegerField, default 0)
- created_at, updated_at (auto)

**DR1.2**: Le modèle DownloadLog DOIT avoir les champs:
- achat (ForeignKey vers AchatDocument)
- ip_address (GenericIPAddressField)
- timestamp (DateTimeField, auto_now_add)

**DR1.3**: Les index suivants DOIVENT exister:
- AchatDocument: (acheteur, created_at)
- AchatDocument: (transaction, created_at)
- AchatDocument: (expiration_lien)
- DownloadLog: (achat, timestamp)
- DocumentTechnique: (culture, canton)
- DocumentTechnique: (actif)

### DR2: Data Validation

**DR2.1**: lien_telechargement DOIT être unique globalement

**DR2.2**: expiration_lien DOIT être dans le futur lors de la création

**DR2.3**: nombre_telechargements DOIT être >= 0

**DR2.4**: ip_address DOIT être une adresse IPv4 ou IPv6 valide

**DR2.5**: DocumentTechnique.prix DOIT être > 0

### DR3: Data Retention

**DR3.1**: Les achats DOIVENT être conservés indéfiniment (audit)

**DR3.2**: Les DownloadLog DOIVENT être anonymisés après 90 jours (GDPR)

**DR3.3**: Les tokens expirés PEUVENT être supprimés après 1 an


## API Requirements

### API1: Purchase History Endpoint

**Endpoint**: GET `/api/v1/purchases/history`

**Authentication**: Required (Bearer token)

**Query Parameters**:
- date_debut (ISO 8601 date, optional)
- date_fin (ISO 8601 date, optional)
- culture (string, optional)
- statut (SUCCESS|PENDING|FAILED, optional)
- lien_expire (boolean, optional)
- page (integer, default 1)
- page_size (integer, default 20)

**Response 200**:
```json
{
  "count": 42,
  "next": "http://api.example.com/purchases/history?page=2",
  "previous": null,
  "results": [
    {
      "id": 123,
      "document": 456,
      "document_titre": "Compte d'Exploitation Maïs",
      "document_culture": "Maïs",
      "document_prix": "5000.00",
      "format_fichier": "EXCEL",
      "transaction_id": "uuid",
      "transaction_statut": "SUCCESS",
      "lien_telechargement": "token",
      "expiration_lien": "2024-01-15T12:00:00Z",
      "lien_expire": false,
      "peut_regenerer": true,
      "nombre_telechargements": 2,
      "created_at": "2024-01-13T12:00:00Z"
    }
  ]
}
```

**Response 401**: Unauthorized (token manquant ou invalide)

### API2: Regenerate Link Endpoint

**Endpoint**: POST `/api/v1/purchases/history/{id}/regenerate-link`

**Authentication**: Required (Bearer token)

**Request Body**: Empty

**Response 200**:
```json
{
  "success": true,
  "download_url": "http://api.example.com/documents/456/download?token=new_token",
  "expiration": "2024-01-17T12:00:00Z",
  "message": "Nouveau lien de téléchargement généré avec succès"
}
```

**Response 400**: Bad Request (transaction non SUCCESS)
```json
{
  "success": false,
  "error": "Le paiement n'est pas confirmé"
}
```

**Response 403**: Forbidden (pas le propriétaire)

**Response 404**: Not Found (achat inexistant)

### API3: Payment Verification Endpoint

**Endpoint**: GET `/api/v1/purchases/verify/{transaction_id}`

**Authentication**: Required (Bearer token)

**Response 200** (Success):
```json
{
  "success": true,
  "transaction_id": "uuid",
  "document": {
    "id": 456,
    "titre": "Compte d'Exploitation Maïs",
    "culture": "Maïs",
    "prix": "5000.00",
    "format_fichier": "EXCEL"
  },
  "download_url": "http://api.example.com/documents/456/download?token=xxx",
  "expiration": "2024-01-15T12:00:00Z",
  "message": "Paiement confirmé"
}
```

**Response 200** (Failed):
```json
{
  "success": false,
  "transaction_id": "uuid",
  "message": "Le paiement a échoué",
  "error": "Payment declined"
}
```

**Response 404**: Transaction not found


## UI/UX Requirements

### UI1: Purchase History Page Layout

**UI1.1**: La page DOIT avoir un header avec:
- Titre "📚 Mes Achats de Documents"
- Compteur total d'achats
- Bouton "Retour aux documents"

**UI1.2**: La sidebar de filtres DOIT contenir:
- Champ de recherche par titre
- Sélecteur de plage de dates (date picker)
- Sélecteur de culture (dropdown)
- Sélecteur de statut (dropdown)
- Checkbox "Liens expirés uniquement"
- Bouton "Réinitialiser les filtres"

**UI1.3**: Chaque carte d'achat DOIT afficher:
- Icône de document (📄)
- Titre du document
- Culture avec icône (🌾)
- Prix avec icône (💰)
- Format (Excel/Word) avec icône
- Badge de statut coloré
- Date d'achat formatée
- Nombre de téléchargements
- Date d'expiration (si applicable)
- Bouton d'action (Télécharger ou Régénérer)

**UI1.4**: Les cartes DOIVENT avoir:
- Bordure verte si lien valide
- Bordure rouge si lien expiré
- Bordure orange si paiement en attente
- Bordure grise si paiement échoué

**UI1.5**: La pagination DOIT afficher:
- Numéro de page actuelle
- Nombre total de pages
- Boutons Précédent/Suivant
- Sélecteur de taille de page (10/20/50)

### UI2: Payment Success Page Layout

**UI2.1**: La page DOIT avoir:
- Grande icône de succès animée (✅)
- Titre "Paiement Réussi!" en grand
- Sous-titre "Votre document est maintenant disponible"

**UI2.2**: La carte de document DOIT afficher:
- Titre du document
- Culture et prix
- Format du fichier
- Icône de document

**UI2.3**: Le bouton de téléchargement DOIT:
- Être large et proéminent
- Avoir une icône de téléchargement (📥)
- Texte "Télécharger Maintenant"
- Couleur verte
- Animation au survol

**UI2.4**: L'avertissement d'expiration DOIT:
- Être visible mais non intrusif
- Texte "Lien valide jusqu'au [date]"
- Icône d'horloge (⏰)

**UI2.5**: Le lien vers l'historique DOIT:
- Être un bouton secondaire
- Texte "Voir mon historique d'achats"
- Positionné en bas de page

### UI3: Toast Notifications

**UI3.1**: Les toasts de succès DOIVENT:
- Fond vert
- Icône ✓
- Durée 3 secondes
- Position top-right

**UI3.2**: Les toasts d'erreur DOIVENT:
- Fond rouge
- Icône ✗
- Durée 5 secondes
- Position top-right
- Bouton de fermeture

**UI3.3**: Les toasts d'information DOIVENT:
- Fond bleu
- Icône ℹ
- Durée 4 secondes
- Position top-right

### UI4: Loading States

**UI4.1**: Les skeleton loaders DOIVENT:
- Avoir une animation de pulsation
- Respecter la structure de la carte finale
- Couleur gris clair

**UI4.2**: Les boutons en chargement DOIVENT:
- Afficher un spinner
- Être désactivés
- Texte "Chargement..."
- Conserver leur taille

**UI4.3**: La page en chargement DOIT:
- Afficher 3-5 skeleton cards
- Afficher un spinner global si liste vide

### UI5: Responsive Design

**UI5.1**: Sur mobile (< 768px):
- Sidebar de filtres en modal
- Cartes en colonne unique
- Boutons pleine largeur
- Texte réduit mais lisible

**UI5.2**: Sur tablette (768px - 1024px):
- Sidebar collapsible
- Cartes en 2 colonnes
- Espacement réduit

**UI5.3**: Sur desktop (> 1024px):
- Sidebar fixe à gauche
- Cartes en 3 colonnes
- Espacement optimal


## Email Requirements

### EM1: Purchase Confirmation Email

**Subject**: "Confirmation d'achat - [Titre du document]"

**From**: "Haroo Platform <noreply@haroo.tg>"

**Content MUST include**:
- Salutation personnalisée avec nom de l'utilisateur
- Titre du document acheté
- Culture et prix
- Bouton CTA "Télécharger le document" (lien sécurisé)
- Date d'expiration du lien (48h)
- ID de transaction pour référence
- Date et heure de l'achat
- Lien vers l'historique des achats
- Footer avec coordonnées de support

**Design**:
- Logo Haroo en header
- Couleurs de la marque (vert #2e7d32)
- Responsive (mobile-friendly)
- Bouton CTA proéminent
- Texte clair et concis

### EM2: Expiration Reminder Email

**Subject**: "⏰ Votre lien de téléchargement expire bientôt"

**From**: "Haroo Platform <noreply@haroo.tg>"

**Content MUST include**:
- Rappel du document concerné
- Message d'urgence "Expire dans 24 heures"
- Bouton CTA "Télécharger maintenant"
- Information sur la régénération possible
- Lien vers l'historique

**Trigger**: 24 heures avant expiration, uniquement si non téléchargé

### EM3: Link Regenerated Email

**Subject**: "✅ Nouveau lien de téléchargement disponible"

**From**: "Haroo Platform <noreply@haroo.tg>"

**Content MUST include**:
- Confirmation de régénération
- Titre du document
- Nouveau bouton CTA "Télécharger"
- Nouvelle date d'expiration (48h)
- Rappel de télécharger rapidement

### EM4: Email Template Requirements

**EM4.1**: Tous les emails DOIVENT avoir:
- Version HTML et version texte
- CSS inline pour compatibilité
- Images hébergées (pas d'attachements)
- Liens absolus (pas de liens relatifs)

**EM4.2**: Les emails DOIVENT être testés sur:
- Gmail (web et mobile)
- Outlook (web et desktop)
- Apple Mail (macOS et iOS)
- Clients Android

**EM4.3**: Les emails DOIVENT respecter:
- Largeur max 600px
- Taille totale < 100KB
- Pas de JavaScript
- Polices web-safe

## Integration Requirements

### INT1: Fedapay Integration

**INT1.1**: Le système DOIT utiliser l'API Fedapay v1

**INT1.2**: Le système DOIT utiliser le mode sandbox pour les tests

**INT1.3**: Le système DOIT vérifier les signatures des webhooks

**INT1.4**: Le système DOIT gérer les callbacks:
- Success: Mettre à jour transaction à SUCCESS, générer lien, envoyer email
- Failed: Mettre à jour transaction à FAILED, logger l'erreur
- Pending: Mettre à jour transaction à PENDING, attendre confirmation

**INT1.5**: Le système DOIT inclure dans la requête Fedapay:
- Montant en FCFA
- Description du document
- Callback URL
- Metadata (user_id, document_id)

### INT2: Celery Integration

**INT2.1**: Le système DOIT configurer Celery avec Redis comme broker

**INT2.2**: Le système DOIT définir les tâches:
- send_purchase_confirmation_async (immédiate)
- send_expiration_reminders (scheduled, daily)
- anonymize_old_download_logs (scheduled, weekly)

**INT2.3**: Les tâches DOIVENT avoir:
- Retry logic (max 3 tentatives)
- Exponential backoff (5min, 15min, 45min)
- Logging complet

**INT2.4**: Le système DOIT utiliser Celery Beat pour les tâches planifiées

### INT3: Redis Integration

**INT3.1**: Le système DOIT utiliser Redis pour:
- Cache des listes de documents (5 minutes)
- Cache des détails de documents (10 minutes)
- Celery message broker
- Rate limiting

**INT3.2**: Les clés de cache DOIVENT suivre le pattern:
- `documents_list:{params_hash}`
- `document_detail:{document_id}`
- `user_purchases:{user_id}`

**INT3.3**: Le système DOIT invalider le cache lors de:
- Création/modification de document
- Nouvel achat
- Régénération de lien


## Testing Requirements

### TEST1: Unit Testing

**TEST1.1**: Le code backend DOIT avoir une couverture de tests ≥ 80%

**TEST1.2**: Les tests DOIVENT couvrir:
- SecureDownloadService: génération token, validation, régénération
- EmailService: envoi emails, templates, gestion erreurs
- ViewSets: purchase, download, regenerate, history
- Serializers: validation, transformation données
- Filters: application correcte des filtres

**TEST1.3**: Le code frontend DOIT avoir une couverture de tests ≥ 70%

**TEST1.4**: Les tests frontend DOIVENT couvrir:
- PurchaseHistory: affichage, filtres, actions
- PaymentSuccess: vérification, affichage, navigation
- Documents: modal, indicateurs, actions

**TEST1.5**: Les tests DOIVENT utiliser:
- pytest pour Python
- Jest + React Testing Library pour TypeScript
- Factory Boy pour fixtures Python
- MSW pour mocking API en TypeScript

### TEST2: Property-Based Testing

**TEST2.1**: Le système DOIT avoir des property tests pour:
- Unicité des tokens générés
- Cohérence des dates d'expiration (toujours +48h)
- Invariant d'autorisation (owner only)
- Validité des URLs générées

**TEST2.2**: Les property tests DOIVENT utiliser:
- Hypothesis pour Python
- fast-check pour TypeScript

**TEST2.3**: Les property tests DOIVENT générer:
- Minimum 100 cas de test par propriété
- Cas limites (edge cases)
- Cas invalides

### TEST3: Integration Testing

**TEST3.1**: Le système DOIT avoir des tests d'intégration pour:
- Flux complet achat → paiement → téléchargement
- Flux régénération de lien
- Flux filtrage historique
- Envoi d'emails

**TEST3.2**: Les tests d'intégration DOIVENT:
- Utiliser une base de données de test
- Utiliser Fedapay sandbox
- Utiliser MailHog pour emails
- Nettoyer les données après chaque test

### TEST4: E2E Testing (Optional)

**TEST4.1**: Le système DEVRAIT avoir des tests E2E pour:
- Parcours utilisateur complet
- Cas d'erreur principaux
- Responsive design

**TEST4.2**: Les tests E2E DEVRAIENT utiliser:
- Playwright
- Environnement de staging
- Données de test dédiées

### TEST5: Performance Testing

**TEST5.1**: Le système DOIT être testé pour:
- Temps de chargement de la page historique (< 2s)
- Temps de réponse API (< 500ms)
- Temps de génération de token (< 100ms)
- Temps d'envoi email async (< 5s)

**TEST5.2**: Les tests de performance DOIVENT simuler:
- 100 utilisateurs simultanés
- 1000 achats en base
- Requêtes avec filtres complexes


## Deployment Requirements

### DEP1: Environment Configuration

**DEP1.1**: Le système DOIT avoir 3 environnements:
- Development (local)
- Staging (pré-production)
- Production

**DEP1.2**: Les variables d'environnement DOIVENT inclure:
```
# Django
SECRET_KEY=xxx
DEBUG=False
ALLOWED_HOSTS=haroo.tg,www.haroo.tg

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=xxx
EMAIL_HOST_PASSWORD=xxx
DEFAULT_FROM_EMAIL=noreply@haroo.tg

# Fedapay
FEDAPAY_API_KEY=xxx
FEDAPAY_ENVIRONMENT=sandbox|live

# Frontend
FRONTEND_URL=https://haroo.tg
```

**DEP1.3**: Les secrets DOIVENT être:
- Stockés dans un gestionnaire de secrets (AWS Secrets Manager, Vault)
- Jamais commités dans Git
- Différents par environnement

### DEP2: Database Migration

**DEP2.1**: Les migrations DOIVENT être:
- Testées en staging avant production
- Réversibles (avec migration down)
- Documentées

**DEP2.2**: Le déploiement DOIT suivre:
1. Backup de la base de données
2. Application des migrations
3. Vérification de l'intégrité
4. Rollback si erreur

### DEP3: Static Files

**DEP3.1**: Les fichiers statiques frontend DOIVENT être:
- Buildés avec Vite
- Minifiés et optimisés
- Servis via CDN (CloudFront, Cloudflare)

**DEP3.2**: Les fichiers media (documents) DOIVENT être:
- Stockés sur S3 ou équivalent
- Servis via CDN avec signature
- Backupés quotidiennement

### DEP4: Monitoring

**DEP4.1**: Le système DOIT monitorer:
- Taux d'erreur API (< 1%)
- Temps de réponse (p95 < 1s)
- Taux de succès des emails (> 95%)
- Utilisation CPU/RAM
- Espace disque

**DEP4.2**: Le système DOIT alerter sur:
- Erreurs 5xx (immédiat)
- Temps de réponse élevé (> 3s)
- Échecs d'envoi email (> 10%)
- Espace disque < 20%

**DEP4.3**: Le système DEVRAIT utiliser:
- Sentry pour tracking d'erreurs
- Prometheus + Grafana pour métriques
- CloudWatch ou équivalent

### DEP5: Backup and Recovery

**DEP5.1**: Les backups DOIVENT inclure:
- Base de données (quotidien, rétention 30 jours)
- Fichiers media (quotidien, rétention 90 jours)
- Configuration (à chaque changement)

**DEP5.2**: Le système DOIT avoir un plan de recovery:
- RTO (Recovery Time Objective): 4 heures
- RPO (Recovery Point Objective): 24 heures
- Procédure documentée et testée

### DEP6: Scaling

**DEP6.1**: Le système DOIT supporter le scaling horizontal:
- Plusieurs instances Django derrière load balancer
- Celery workers scalables
- Redis cluster pour haute disponibilité

**DEP6.2**: Le système DOIT avoir:
- Health check endpoint: `/health`
- Readiness check endpoint: `/ready`
- Graceful shutdown (30s timeout)

## Documentation Requirements

### DOC1: Code Documentation

**DOC1.1**: Toutes les fonctions publiques DOIVENT avoir des docstrings incluant:
- Description
- Paramètres avec types
- Valeur de retour
- Exceptions possibles
- Exemples d'utilisation

**DOC1.2**: Les composants React DOIVENT avoir:
- JSDoc avec description
- Props documentés avec types
- Exemples d'utilisation

### DOC2: API Documentation

**DOC2.1**: L'API DOIT avoir une documentation OpenAPI/Swagger

**DOC2.2**: La documentation DOIT inclure:
- Tous les endpoints
- Paramètres et body
- Exemples de requêtes/réponses
- Codes d'erreur possibles
- Authentication requirements

### DOC3: User Documentation

**DOC3.1**: Le système DOIT avoir un guide utilisateur incluant:
- Comment acheter un document
- Comment télécharger un document
- Comment régénérer un lien expiré
- FAQ

**DOC3.2**: Le guide DOIT être:
- En français
- Avec captures d'écran
- Accessible depuis l'application

### DOC4: Admin Documentation

**DOC4.1**: Le système DOIT avoir un guide admin incluant:
- Gestion des documents
- Gestion des achats
- Régénération de liens
- Export de données
- Résolution de problèmes courants

## Traceability Matrix

| Requirement ID | Design Section | Test Coverage |
|---------------|----------------|---------------|
| FR1.1-FR1.7 | PurchaseHistory Component | TEST1.4 |
| FR2.1-FR2.8 | PaymentSuccess Component | TEST1.4 |
| FR3.1-FR3.7 | SecureDownloadService.regenerate_link | TEST1.2 |
| FR4.1-FR4.9 | EmailService | TEST1.2, TEST3.1 |
| FR5.1-FR5.8 | Admin Improvements | Manual Testing |
| FR6.1-FR6.5 | Documents Improvements | TEST1.4 |
| NFR1.1-NFR1.6 | Performance Considerations | TEST5.1 |
| NFR2.1-NFR2.10 | Security Considerations | TEST1.2 |
| NFR3.1-NFR3.5 | Error Handling | TEST1.2, TEST3.1 |

