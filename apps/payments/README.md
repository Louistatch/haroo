# Module Payments - Intégration Fedapay

Ce module gère l'intégration avec Fedapay pour les paiements mobiles au Togo.

## Fonctionnalités

### 1. Initialisation de paiement
- Endpoint: `POST /api/v1/payments/initiate`
- Crée une transaction et redirige vers Fedapay
- Calcul automatique des commissions selon le type de transaction

### 2. Webhooks Fedapay
- Endpoint: `POST /api/v1/payments/webhooks/fedapay`
- Reçoit les notifications de Fedapay
- Vérifie la signature HMAC SHA256 pour sécurité
- Met à jour automatiquement le statut des transactions
- Déclenche les actions post-paiement selon le type de transaction:
  - **ACHAT_DOCUMENT**: Génère un lien de téléchargement sécurisé (48h)
  - **RECRUTEMENT_AGRONOME**: Bloque le paiement en escrow
  - **PREVENTE**: Bloque l'acompte (20%) en escrow
  - **TRANSPORT**: Bloque le paiement en escrow
  - **ABONNEMENT**: Active l'abonnement premium
- Idempotent: traiter plusieurs fois le même webhook ne cause pas de problèmes
- Vérification de signature pour la sécurité

### 3. Historique des transactions
- Endpoint: `GET /api/v1/transactions/history`
- Liste les transactions de l'utilisateur connecté
- Filtres disponibles: type, statut

### 4. Détails d'une transaction
- Endpoint: `GET /api/v1/transactions/{id}`
- Récupère les détails d'une transaction spécifique

### 5. Callback après paiement
- Endpoint: `GET /api/v1/payments/callback`
- Page de retour après paiement Fedapay

## Modèles

### Transaction
- `id`: UUID unique
- `utilisateur`: Référence vers l'utilisateur
- `type_transaction`: Type (ACHAT_DOCUMENT, RECRUTEMENT_AGRONOME, PREVENTE, TRANSPORT, ABONNEMENT)
- `montant`: Montant en FCFA
- `commission_plateforme`: Commission calculée automatiquement
- `statut`: PENDING, SUCCESS, FAILED, REFUNDED
- `fedapay_transaction_id`: ID de la transaction Fedapay
- `reference_externe`: Référence optionnelle (ID document, mission, etc.)

## Services

### FedapayService
Gère l'intégration avec l'API Fedapay:
- `initiate_payment()`: Initialise un paiement
- `get_transaction_status()`: Récupère le statut d'une transaction
- `verify_webhook_signature()`: Vérifie la signature des webhooks

### PostPaymentActionHandler
- `handle_successful_payment()`: Dispatcher principal pour les actions post-paiement
- `_handle_document_purchase()`: Déblocage de documents avec lien sécurisé
- `_handle_agronomist_recruitment()`: Gestion escrow pour missions d'agronomes
- `_handle_presale()`: Gestion escrow pour préventes agricoles
- `_handle_transport()`: Gestion escrow pour transport
- `_handle_subscription()`: Activation d'abonnements premium

### TransactionService
Gère les transactions:
- `create_transaction()`: Crée une nouvelle transaction avec calcul de commission
- `update_transaction_status()`: Met à jour le statut d'une transaction

### CommissionCalculator
Calcule les commissions:
- `get_commission_rate()`: Obtient le taux de commission
- `calculate_net_amount()`: Calcule le montant net après commission

## Taux de Commission

- **Achat de documents**: 0%
- **Recrutement d'agronomes**: 10%
- **Préventes agricoles**: 5%
- **Transport**: 8%
- **Abonnements**: 0%

## Configuration

Variables d'environnement requises dans `.env`:

```env
FEDAPAY_API_KEY=your-api-key
FEDAPAY_SECRET_KEY=your-secret-key
FEDAPAY_ENVIRONMENT=sandbox  # ou 'live' en production
FEDAPAY_WEBHOOK_SECRET=your-webhook-secret

COMMISSION_AGRONOME=10
COMMISSION_PREVENTE=5
COMMISSION_TRANSPORT=8
```

## Flux de Paiement

1. **Initialisation**:
   - L'utilisateur initie un achat
   - Une transaction est créée avec statut PENDING
   - Redirection vers Fedapay avec les détails du paiement

2. **Paiement**:
   - L'utilisateur effectue le paiement sur Fedapay
   - Fedapay traite le paiement

3. **Notification**:
   - Fedapay envoie un webhook à notre endpoint
   - Le statut de la transaction est mis à jour (SUCCESS ou FAILED)
   - Les actions post-paiement sont déclenchées

4. **Retour**:
   - L'utilisateur est redirigé vers notre callback
   - Affichage du résultat du paiement

## Sécurité

- Vérification de signature HMAC SHA256 pour les webhooks
- Authentification JWT requise pour les endpoints utilisateur
- Validation stricte des montants et types de transaction
- Logs détaillés de toutes les opérations

## Tests

Exécuter les tests:
```bash
python manage.py test apps.payments
```

Les tests couvrent:
- Création et gestion des transactions
- Calcul des commissions
- Initialisation de paiements (avec mocks Fedapay)
- Mise à jour des statuts
- Vérification des signatures webhook

## Utilisation

### Exemple: Initialiser un paiement

```python
from apps.payments.services import FedapayService, TransactionService

# Créer une transaction
transaction = TransactionService.create_transaction(
    utilisateur=request.user,
    type_transaction='ACHAT_DOCUMENT',
    montant=Decimal('5000.00'),
    reference_externe='doc_123'
)

# Initialiser le paiement Fedapay
fedapay_service = FedapayService()
payment_data = fedapay_service.initiate_payment(
    transaction=transaction,
    callback_url='https://example.com/callback',
    description='Achat document technique'
)

# Rediriger l'utilisateur vers payment_data['payment_url']
```

### Exemple: Requête API

```bash
curl -X POST https://api.haroo.tg/api/v1/payments/initiate \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type_transaction": "ACHAT_DOCUMENT",
    "montant": 5000.00,
    "reference_externe": "doc_123",
    "description": "Achat document technique maïs"
  }'
```

Réponse:
```json
{
  "success": true,
  "transaction_id": "uuid-here",
  "fedapay_transaction_id": "fedapay_id",
  "payment_url": "https://checkout.fedapay.com/...",
  "token": "payment_token",
  "message": "Redirection vers Fedapay pour finaliser le paiement"
}
```

## TODO

- [ ] Implémenter les actions post-paiement selon le type de transaction
- [ ] Ajouter le support des remboursements
- [ ] Créer un dashboard admin pour le suivi des transactions
- [ ] Implémenter les notifications utilisateur après paiement
- [ ] Ajouter des métriques de monitoring (Prometheus)
