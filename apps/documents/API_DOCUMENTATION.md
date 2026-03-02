# API Documentation - Catalogue de Documents Techniques

## Vue d'ensemble

Cette API fournit des endpoints pour consulter le catalogue de documents techniques agricoles. Les documents peuvent être filtrés par localisation (région, préfecture, canton), culture, type et prix.

## Endpoints

### 1. Liste des documents

**Endpoint:** `GET /api/v1/documents/`

**Description:** Récupère la liste paginée des documents techniques actifs.

**Paramètres de requête:**

| Paramètre | Type | Description | Exemple |
|-----------|------|-------------|---------|
| `region` | integer | ID de la région | `?region=1` |
| `prefecture` | integer | ID de la préfecture | `?prefecture=5` |
| `canton` | integer | ID du canton | `?canton=12` |
| `culture` | string | Nom de la culture (recherche partielle) | `?culture=Maïs` |
| `type` | string | Type de document (`COMPTE_EXPLOITATION` ou `ITINERAIRE_TECHNIQUE`) | `?type=ITINERAIRE_TECHNIQUE` |
| `prix_min` | decimal | Prix minimum en FCFA | `?prix_min=5000` |
| `prix_max` | decimal | Prix maximum en FCFA | `?prix_max=10000` |
| `search` | string | Recherche dans titre, description, culture | `?search=riz` |
| `ordering` | string | Tri (`prix`, `-prix`, `created_at`, `-created_at`) | `?ordering=-prix` |
| `page` | integer | Numéro de page (50 éléments par page) | `?page=2` |

**Exemples de requêtes:**

```bash
# Tous les documents
GET /api/v1/documents/

# Documents de maïs dans la région Maritime
GET /api/v1/documents/?region=1&culture=Maïs

# Documents entre 5000 et 10000 FCFA, triés par prix décroissant
GET /api/v1/documents/?prix_min=5000&prix_max=10000&ordering=-prix

# Recherche de documents sur le riz
GET /api/v1/documents/?search=riz
```

**Réponse (200 OK):**

```json
{
  "count": 42,
  "next": "http://api.example.com/api/v1/documents/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "titre": "Itinéraire Technique Maïs - Lomé",
      "description": "Guide complet pour la culture du maïs à Lomé",
      "prix": "5000.00",
      "region": 1,
      "region_nom": "Maritime",
      "prefecture": 5,
      "prefecture_nom": "Golfe",
      "canton": 12,
      "canton_nom": "Lomé 1er",
      "culture": "Maïs",
      "type_document": "ITINERAIRE_TECHNIQUE",
      "format_fichier": "EXCEL",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

**Cache:** Les résultats sont mis en cache pendant 5 minutes (300 secondes).

---

### 2. Détails d'un document

**Endpoint:** `GET /api/v1/documents/{id}/`

**Description:** Récupère les détails complets d'un document technique.

**Paramètres:**

| Paramètre | Type | Description |
|-----------|------|-------------|
| `id` | integer | ID du document (dans l'URL) |

**Exemple de requête:**

```bash
GET /api/v1/documents/1/
```

**Réponse (200 OK):**

```json
{
  "id": 1,
  "titre": "Itinéraire Technique Maïs - Lomé",
  "description": "Guide complet pour la culture du maïs à Lomé avec calendrier cultural, doses d'engrais, traitements phytosanitaires et prévisions de rendement.",
  "prix": "5000.00",
  "region": 1,
  "region_nom": "Maritime",
  "prefecture": 5,
  "prefecture_nom": "Golfe",
  "canton": 12,
  "canton_nom": "Lomé 1er",
  "culture": "Maïs",
  "type_document": "ITINERAIRE_TECHNIQUE",
  "type_document_display": "Itinéraire Technique",
  "format_fichier": "EXCEL",
  "format_fichier_display": "Excel",
  "template_info": {
    "id": 3,
    "titre": "Template Maïs",
    "version": 1
  },
  "actif": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Réponse (404 Not Found):**

```json
{
  "detail": "Not found."
}
```

**Cache:** Les résultats sont mis en cache pendant 10 minutes (600 secondes).

---

## Pagination

L'API utilise une pagination par numéro de page avec 50 éléments par page.

**Structure de la réponse paginée:**

```json
{
  "count": 150,           // Nombre total d'éléments
  "next": "url",          // URL de la page suivante (null si dernière page)
  "previous": "url",      // URL de la page précédente (null si première page)
  "results": [...]        // Tableau des résultats
}
```

---

## Filtrage

### Filtres géographiques

Les filtres géographiques sont hiérarchiques:
- **Région** → **Préfecture** → **Canton**

Vous pouvez filtrer à n'importe quel niveau de la hiérarchie.

**Exemples:**

```bash
# Tous les documents de la région Maritime
GET /api/v1/documents/?region=1

# Documents de la préfecture de Golfe
GET /api/v1/documents/?prefecture=5

# Documents du canton Lomé 1er
GET /api/v1/documents/?canton=12
```

### Filtre par culture

Le filtre `culture` effectue une recherche partielle (insensible à la casse).

**Exemples:**

```bash
# Documents contenant "maïs" dans le nom de la culture
GET /api/v1/documents/?culture=maïs

# Documents contenant "riz"
GET /api/v1/documents/?culture=riz
```

### Filtre par type

Le filtre `type` accepte les valeurs exactes:
- `COMPTE_EXPLOITATION`: Compte d'Exploitation Prévisionnel
- `ITINERAIRE_TECHNIQUE`: Itinéraire Technique

**Exemple:**

```bash
GET /api/v1/documents/?type=ITINERAIRE_TECHNIQUE
```

### Filtre par prix

Utilisez `prix_min` et `prix_max` pour filtrer par plage de prix (en FCFA).

**Exemples:**

```bash
# Documents à moins de 10000 FCFA
GET /api/v1/documents/?prix_max=10000

# Documents entre 5000 et 15000 FCFA
GET /api/v1/documents/?prix_min=5000&prix_max=15000
```

### Combinaison de filtres

Vous pouvez combiner plusieurs filtres:

```bash
GET /api/v1/documents/?region=1&culture=Maïs&prix_max=10000&ordering=prix
```

---

## Recherche

Le paramètre `search` effectue une recherche textuelle dans:
- Titre du document
- Description du document
- Nom de la culture

**Exemple:**

```bash
# Recherche de "irrigation"
GET /api/v1/documents/?search=irrigation
```

---

## Tri

Utilisez le paramètre `ordering` pour trier les résultats:

| Valeur | Description |
|--------|-------------|
| `prix` | Prix croissant |
| `-prix` | Prix décroissant |
| `created_at` | Date de création croissante |
| `-created_at` | Date de création décroissante (défaut) |

**Exemples:**

```bash
# Tri par prix croissant
GET /api/v1/documents/?ordering=prix

# Tri par prix décroissant
GET /api/v1/documents/?ordering=-prix
```

---

## Cache

L'API utilise Redis pour mettre en cache les réponses et améliorer les performances:

- **Liste des documents:** Cache de 5 minutes (300 secondes)
- **Détails d'un document:** Cache de 10 minutes (600 secondes)

Chaque combinaison de filtres génère une entrée de cache distincte.

---

## Permissions

Les endpoints du catalogue sont **publics** et ne nécessitent pas d'authentification.

---

## Codes de statut HTTP

| Code | Description |
|------|-------------|
| 200 | Succès |
| 404 | Document non trouvé |
| 500 | Erreur serveur |

---

## Exemples d'utilisation

### JavaScript (Fetch API)

```javascript
// Liste des documents de maïs
fetch('http://api.example.com/api/v1/documents/?culture=Maïs')
  .then(response => response.json())
  .then(data => {
    console.log(`Trouvé ${data.count} documents`);
    data.results.forEach(doc => {
      console.log(`${doc.titre} - ${doc.prix} FCFA`);
    });
  });

// Détails d'un document
fetch('http://api.example.com/api/v1/documents/1/')
  .then(response => response.json())
  .then(doc => {
    console.log(`Titre: ${doc.titre}`);
    console.log(`Prix: ${doc.prix} FCFA`);
    console.log(`Localisation: ${doc.canton_nom}, ${doc.prefecture_nom}, ${doc.region_nom}`);
  });
```

### Python (requests)

```python
import requests

# Liste des documents
response = requests.get('http://api.example.com/api/v1/documents/', params={
    'region': 1,
    'culture': 'Maïs',
    'prix_max': 10000,
    'ordering': 'prix'
})
data = response.json()
print(f"Trouvé {data['count']} documents")

# Détails d'un document
response = requests.get('http://api.example.com/api/v1/documents/1/')
doc = response.json()
print(f"{doc['titre']} - {doc['prix']} FCFA")
```

### cURL

```bash
# Liste des documents
curl "http://api.example.com/api/v1/documents/?culture=Maïs&region=1"

# Détails d'un document
curl "http://api.example.com/api/v1/documents/1/"
```

---

## Notes techniques

### Performance

- Les requêtes utilisent `select_related()` pour optimiser les jointures SQL
- Le cache Redis réduit la charge sur la base de données
- La pagination limite le nombre de résultats par requête

### Optimisations futures

- Ajout d'un cache de second niveau pour les filtres fréquents
- Compression des réponses JSON
- Support de GraphQL pour des requêtes plus flexibles


## Flux d'Achat de Documents

### POST /api/v1/documents/{id}/purchase

Initier l'achat d'un document technique via Fedapay.

**Authentification:** Requise

**Paramètres URL:**
- `id` (integer): ID du document à acheter

**Corps de la requête:**
```json
{
  "callback_url": "https://example.com/callback"  // optionnel
}
```

**Réponse (201 Created):**
```json
{
  "success": true,
  "transaction_id": "uuid",
  "payment_url": "https://checkout.fedapay.com/...",
  "message": "Redirection vers Fedapay pour finaliser le paiement"
}
```

**Réponse si déjà acheté (200 OK):**
```json
{
  "success": true,
  "already_purchased": true,
  "message": "Vous avez déjà acheté ce document",
  "download_url": "https://api.example.com/api/v1/documents/123/download?token=...",
  "expiration": "2024-01-15T12:00:00Z"
}
```

**Exigences:** 3.4, 4.1, 5.1

---

### GET /api/v1/documents/{id}/download

Télécharger un document acheté avec un token valide.

**Authentification:** Requise

**Paramètres URL:**
- `id` (integer): ID du document

**Paramètres de requête:**
- `token` (string): Token de téléchargement sécurisé

**Réponse (200 OK):**
- Fichier du document (Excel ou Word)
- Header `Content-Disposition`: `attachment; filename="Document_Titre.xlsx"`

**Réponse d'erreur (403 Forbidden):**
```json
{
  "success": false,
  "error": "Le lien de téléchargement a expiré. Veuillez régénérer un nouveau lien depuis votre historique d'achats."
}
```

**Exigences:** 5.2, 5.5

---

### GET /api/v1/purchases/history

Récupérer l'historique des achats de documents de l'utilisateur.

**Authentification:** Requise

**Paramètres de requête:**

| Paramètre | Type | Description | Exemple |
|-----------|------|-------------|---------|
| `date_debut` | datetime | Date de début (ISO 8601) | `?date_debut=2024-01-01T00:00:00Z` |
| `date_fin` | datetime | Date de fin (ISO 8601) | `?date_fin=2024-12-31T23:59:59Z` |
| `type_document` | string | Type de document | `?type_document=COMPTE_EXPLOITATION` |
| `culture` | string | Nom de la culture (recherche partielle) | `?culture=Maïs` |
| `statut` | string | Statut de la transaction | `?statut=SUCCESS` |
| `lien_expire` | boolean | Filtrer par lien expiré | `?lien_expire=true` |
| `search` | string | Recherche dans titre et culture | `?search=riz` |
| `ordering` | string | Tri | `?ordering=-created_at` |
| `page` | integer | Numéro de page (50 éléments par page) | `?page=2` |

**Options de tri:**
- `created_at`: Date d'achat croissante
- `-created_at`: Date d'achat décroissante (défaut)
- `document__prix`: Prix croissant
- `-document__prix`: Prix décroissant
- `nombre_telechargements`: Nombre de téléchargements croissant
- `-nombre_telechargements`: Nombre de téléchargements décroissant

**Exemples de requêtes:**

```bash
# Tous les achats
GET /api/v1/purchases/history

# Achats du mois de janvier 2024
GET /api/v1/purchases/history?date_debut=2024-01-01T00:00:00Z&date_fin=2024-01-31T23:59:59Z

# Achats de documents de maïs
GET /api/v1/purchases/history?culture=Maïs

# Achats avec liens expirés
GET /api/v1/purchases/history?lien_expire=true

# Achats de type COMPTE_EXPLOITATION, triés par prix décroissant
GET /api/v1/purchases/history?type_document=COMPTE_EXPLOITATION&ordering=-document__prix
```

**Réponse (200 OK):**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "document": 123,
      "document_titre": "Compte d'Exploitation Maïs - Canton de Lomé",
      "document_culture": "Maïs",
      "document_prix": "5000.00",
      "format_fichier": "EXCEL",
      "transaction_id": "uuid",
      "transaction_statut": "SUCCESS",
      "lien_telechargement": "token",
      "expiration_lien": "2024-01-15T12:00:00Z",
      "lien_expire": false,
      "peut_regenerer": true,
      "nombre_telechargements": 3,
      "created_at": "2024-01-13T10:00:00Z"
    }
  ]
}
```

**Exigence:** 5.3

---

### POST /api/v1/purchases/history/{id}/regenerate-link

Régénérer un lien de téléchargement expiré.

**Authentification:** Requise

**Paramètres URL:**
- `id` (integer): ID de l'achat

**Réponse (200 OK):**
```json
{
  "success": true,
  "download_url": "https://api.example.com/api/v1/documents/123/download?token=...",
  "expiration": "2024-01-17T12:00:00Z",
  "message": "Nouveau lien de téléchargement généré avec succès"
}
```

**Exigence:** 5.4

---

## Sécurité

### Liens de Téléchargement Sécurisés

- **Durée de validité:** 48 heures
- **Token:** URL-safe, 32 caractères
- **Validation:** Token + utilisateur + statut de paiement
- **Régénération:** Possible à tout moment si le paiement est confirmé

### Audit des Téléchargements

Chaque téléchargement est enregistré avec:
- Horodatage
- Adresse IP
- Compteur de téléchargements

**Exigence:** 5.5

---

## Flux Complet

1. **Utilisateur initie l'achat:** `POST /api/v1/documents/{id}/purchase`
2. **Redirection vers Fedapay:** L'utilisateur finalise le paiement
3. **Webhook Fedapay:** Confirmation du paiement → Génération du document personnalisé
4. **Création de l'achat:** Lien de téléchargement généré (48h)
5. **Téléchargement:** `GET /api/v1/documents/{id}/download?token=...`
6. **Audit:** Enregistrement du téléchargement (IP + timestamp)
7. **Régénération (si expiré):** `POST /api/v1/purchases/history/{id}/regenerate-link`


---

## Filtrage de l'Historique des Achats

L'historique des achats supporte plusieurs filtres pour faciliter la recherche:

### Filtrage par Date

Utilisez `date_debut` et `date_fin` pour filtrer par plage de dates:

```bash
# Achats du mois de janvier 2024
GET /api/v1/purchases/history?date_debut=2024-01-01T00:00:00Z&date_fin=2024-01-31T23:59:59Z

# Achats depuis le 1er janvier 2024
GET /api/v1/purchases/history?date_debut=2024-01-01T00:00:00Z

# Achats jusqu'au 31 décembre 2023
GET /api/v1/purchases/history?date_fin=2023-12-31T23:59:59Z
```

### Filtrage par Type de Document

Filtrez par type de document technique:

```bash
# Comptes d'exploitation uniquement
GET /api/v1/purchases/history?type_document=COMPTE_EXPLOITATION

# Itinéraires techniques uniquement
GET /api/v1/purchases/history?type_document=ITINERAIRE_TECHNIQUE
```

### Filtrage par Culture

Recherchez des achats par culture (recherche partielle, insensible à la casse):

```bash
# Documents de maïs
GET /api/v1/purchases/history?culture=Maïs

# Documents de riz
GET /api/v1/purchases/history?culture=riz
```

### Filtrage par Statut de Transaction

Filtrez par statut de paiement:

```bash
# Achats réussis uniquement
GET /api/v1/purchases/history?statut=SUCCESS

# Achats en attente
GET /api/v1/purchases/history?statut=PENDING

# Achats échoués
GET /api/v1/purchases/history?statut=FAILED
```

### Filtrage par État du Lien

Filtrez selon l'état d'expiration du lien de téléchargement:

```bash
# Liens expirés (nécessitent régénération)
GET /api/v1/purchases/history?lien_expire=true

# Liens valides
GET /api/v1/purchases/history?lien_expire=false
```

### Recherche Textuelle

Utilisez le paramètre `search` pour rechercher dans le titre et la culture:

```bash
# Recherche de "irrigation"
GET /api/v1/purchases/history?search=irrigation
```

### Tri

Triez les résultats selon différents critères:

```bash
# Tri par date d'achat décroissante (défaut)
GET /api/v1/purchases/history?ordering=-created_at

# Tri par prix croissant
GET /api/v1/purchases/history?ordering=document__prix

# Tri par nombre de téléchargements décroissant
GET /api/v1/purchases/history?ordering=-nombre_telechargements
```

### Combinaison de Filtres

Vous pouvez combiner plusieurs filtres:

```bash
# Achats de maïs en janvier 2024 avec liens expirés
GET /api/v1/purchases/history?culture=Maïs&date_debut=2024-01-01T00:00:00Z&date_fin=2024-01-31T23:59:59Z&lien_expire=true

# Comptes d'exploitation réussis, triés par prix
GET /api/v1/purchases/history?type_document=COMPTE_EXPLOITATION&statut=SUCCESS&ordering=document__prix
```

### Pagination

L'historique est paginé avec 50 éléments par page:

```bash
# Première page
GET /api/v1/purchases/history

# Deuxième page
GET /api/v1/purchases/history?page=2

# Troisième page avec filtres
GET /api/v1/purchases/history?page=3&culture=Maïs&ordering=-created_at
```

---

## Exemples d'Utilisation - Historique des Achats

### JavaScript (Fetch API)

```javascript
// Récupérer l'historique complet
fetch('http://api.example.com/api/v1/purchases/history', {
  headers: {
    'Authorization': 'Bearer YOUR_JWT_TOKEN'
  }
})
  .then(response => response.json())
  .then(data => {
    console.log(`Total: ${data.count} achats`);
    data.results.forEach(achat => {
      console.log(`${achat.document_titre} - ${achat.document_prix} FCFA`);
      console.log(`Téléchargements: ${achat.nombre_telechargements}`);
      console.log(`Lien expiré: ${achat.lien_expire}`);
    });
  });

// Filtrer par culture et date
fetch('http://api.example.com/api/v1/purchases/history?culture=Maïs&date_debut=2024-01-01T00:00:00Z', {
  headers: {
    'Authorization': 'Bearer YOUR_JWT_TOKEN'
  }
})
  .then(response => response.json())
  .then(data => {
    console.log(`Achats de maïs depuis janvier: ${data.count}`);
  });

// Régénérer un lien expiré
fetch('http://api.example.com/api/v1/purchases/history/123/regenerate-link/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_JWT_TOKEN'
  }
})
  .then(response => response.json())
  .then(data => {
    console.log(`Nouveau lien: ${data.download_url}`);
    console.log(`Expire le: ${data.expiration}`);
  });
```

### Python (requests)

```python
import requests

# Configuration
API_URL = 'http://api.example.com/api/v1'
TOKEN = 'YOUR_JWT_TOKEN'
headers = {'Authorization': f'Bearer {TOKEN}'}

# Récupérer l'historique avec filtres
response = requests.get(
    f'{API_URL}/purchases/history',
    headers=headers,
    params={
        'culture': 'Maïs',
        'date_debut': '2024-01-01T00:00:00Z',
        'ordering': '-created_at'
    }
)
data = response.json()
print(f"Total: {data['count']} achats")

for achat in data['results']:
    print(f"{achat['document_titre']} - {achat['document_prix']} FCFA")
    print(f"Téléchargements: {achat['nombre_telechargements']}")
    if achat['lien_expire']:
        print("⚠️ Lien expiré - régénération nécessaire")

# Régénérer un lien expiré
achat_id = 123
response = requests.post(
    f'{API_URL}/purchases/history/{achat_id}/regenerate-link/',
    headers=headers
)
data = response.json()
print(f"Nouveau lien: {data['download_url']}")
print(f"Expire le: {data['expiration']}")
```

### cURL

```bash
# Récupérer l'historique
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "http://api.example.com/api/v1/purchases/history"

# Filtrer par culture et date
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "http://api.example.com/api/v1/purchases/history?culture=Maïs&date_debut=2024-01-01T00:00:00Z"

# Régénérer un lien
curl -X POST \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "http://api.example.com/api/v1/purchases/history/123/regenerate-link/"
```

