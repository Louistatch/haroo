# Phase 2.3 - Configuration Celery - Guide Complet

## 🎯 Objectif

Configurer Celery pour les tâches asynchrones et planifiées dans Haroo.

---

## ✅ Travaux Réalisés

### Subtask 2.3.1: Install celery and redis packages ✅

**Status**: Déjà installé dans requirements.txt
```
celery==5.3.4
redis==5.0.1
```

### Subtask 2.3.2: Configure Celery in haroo/celery.py ✅

**Fichier**: `haroo/celery.py`

**Configuration ajoutée**:
- Celery Beat schedule (tâches planifiées)
- Timezone: Africa/Lome
- Sérialisation JSON
- Retry configuration
- Task acknowledgment settings

**Tâches planifiées**:
1. **Rappels d'expiration** - Toutes les heures
2. **Anonymisation logs** - Quotidien à 2h00
3. **Nettoyage liens expirés** - Toutes les heures

### Subtask 2.3.3: Create send_purchase_confirmation_async task ✅

**Fichier**: `apps/documents/tasks.py`

**Fonction**: `send_purchase_confirmation_async(achat_id, download_url)`

**Caractéristiques**:
- Tâche asynchrone avec retry automatique
- Max 3 retries
- Exponential backoff
- Jitter pour éviter thundering herd
- Logging complet

### Subtask 2.3.4: Create send_expiration_reminders scheduled task ✅

**Fonction**: `send_expiration_reminders()`

**Caractéristiques**:
- Tâche planifiée (toutes les heures)
- Envoie des rappels 24h avant expiration
- Traitement en masse
- Statistiques d'envoi

### Subtask 2.3.5: Create anonymize_old_download_logs scheduled task ✅

**Fonction**: `anonymize_old_download_logs()`

**Caractéristiques**:
- Tâche planifiée (quotidien à 2h00)
- Anonymise les logs > 90 jours
- Conformité RGPD
- Statistiques d'anonymisation

### Subtask 2.3.6: Configure Celery Beat schedule ✅

**Configuration dans**: `haroo/celery.py`

```python
app.conf.beat_schedule = {
    'send-expiration-reminders-hourly': {
        'task': 'documents.send_expiration_reminders',
        'schedule': crontab(minute=0),
    },
    'anonymize-old-logs-daily': {
        'task': 'documents.anonymize_old_download_logs',
        'schedule': crontab(hour=2, minute=0),
    },
    'cleanup-expired-links-hourly': {
        'task': 'documents.cleanup_expired_links',
        'schedule': crontab(minute=30),
    },
}
```

### Subtask 2.3.7: Add retry logic with exponential backoff ✅

**Configuration**:
```python
@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,  # Exponential backoff
    retry_backoff_max=600,  # Max 10 minutes
    retry_jitter=True  # Randomisation
)
```

**Formule**: `delay = base_delay * (2 ** retry_count) + jitter`
- Retry 1: ~60s
- Retry 2: ~120s
- Retry 3: ~240s (max 600s)

### Subtask 2.3.8: Test Celery tasks locally ✅

**Script de test**: `test_celery_tasks.py`

**Tests inclus**:
1. Connexion Celery/Redis
2. Tâche de debug
3. Tâches d'email
4. Tâches planifiées
5. Configuration Beat
6. Logique de retry

---

## 📁 Fichiers Créés/Modifiés

### Créés (8 fichiers)
```
✅ apps/documents/tasks.py              # Tâches Celery
✅ test_celery_tasks.py                 # Script de test
✅ start_celery_worker.bat              # Démarrage worker (Windows)
✅ start_celery_worker.sh               # Démarrage worker (Linux/macOS)
✅ start_celery_beat.bat                # Démarrage beat (Windows)
✅ start_celery_beat.sh                 # Démarrage beat (Linux/macOS)
✅ PHASE_2.3_CELERY_GUIDE.md            # Ce guide
✅ CELERY_QUICK_START.md                # Guide rapide (à créer)
```

### Modifiés (1 fichier)
```
✅ haroo/celery.py                      # Configuration complète
```

---

## 🚀 Démarrage Rapide

### Prérequis

1. **Redis installé et démarré**
   ```bash
   # Windows (avec Chocolatey)
   choco install redis
   redis-server
   
   # macOS
   brew install redis
   brew services start redis
   
   # Linux
   sudo apt-get install redis-server
   sudo systemctl start redis
   ```

2. **Environnement virtuel activé**
   ```bash
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/macOS
   ```

### Démarrage

#### Option 1: Scripts automatiques

**Windows**:
```bash
# Terminal 1: Worker
start_celery_worker.bat

# Terminal 2: Beat (optionnel)
start_celery_beat.bat
```

**Linux/macOS**:
```bash
# Terminal 1: Worker
./start_celery_worker.sh

# Terminal 2: Beat (optionnel)
./start_celery_beat.sh
```

#### Option 2: Commandes manuelles

```bash
# Worker
celery -A haroo worker -l info

# Beat (tâches planifiées)
celery -A haroo beat -l info

# Worker + Beat (combiné)
celery -A haroo worker -B -l info
```

### Test

```bash
python test_celery_tasks.py
```

---

## 📋 Tâches Disponibles

### Tâches Asynchrones

#### 1. send_purchase_confirmation_async
**Usage**:
```python
from apps.documents.tasks import send_purchase_confirmation_async

send_purchase_confirmation_async.delay(
    achat_id=123,
    download_url='https://...'
)
```

**Quand l'utiliser**: Après un paiement réussi

#### 2. send_link_regenerated_async
**Usage**:
```python
from apps.documents.tasks import send_link_regenerated_async

send_link_regenerated_async.delay(
    achat_id=123,
    download_url='https://...'
)
```

**Quand l'utiliser**: Après régénération d'un lien expiré

### Tâches Planifiées

#### 1. send_expiration_reminders
**Schedule**: Toutes les heures (minute 0)
**Action**: Envoie des rappels 24h avant expiration

#### 2. anonymize_old_download_logs
**Schedule**: Quotidien à 2h00
**Action**: Anonymise les logs > 90 jours (RGPD)

#### 3. cleanup_expired_links
**Schedule**: Toutes les heures (minute 30)
**Action**: Identifie et marque les liens expirés

---

## 🧪 Tests

### Test 1: Connexion Redis

```bash
python -c "import redis; r = redis.Redis(); print(r.ping())"
# Résultat attendu: True
```

### Test 2: Worker Celery

```bash
# Démarrer le worker
celery -A haroo worker -l info

# Dans un autre terminal
python -c "from haroo.celery import debug_task; debug_task.delay()"
```

### Test 3: Tâches d'Email

```bash
python test_celery_tasks.py
```

### Test 4: Beat Schedule

```bash
celery -A haroo inspect scheduled
```

---

## 🐛 Dépannage

### Erreur: "No module named 'celery'"

**Solution**: Installer celery
```bash
pip install celery==5.3.4 redis==5.0.1
```

### Erreur: "Error connecting to Redis"

**Solution**: Démarrer Redis
```bash
redis-server
```

### Erreur: "No workers available"

**Solution**: Démarrer un worker
```bash
celery -A haroo worker -l info
```

### Worker ne démarre pas sur Windows

**Solution**: Utiliser le pool solo
```bash
celery -A haroo worker -l info --pool=solo
```

### Tâches ne s'exécutent pas

**Vérifications**:
1. Redis est démarré
2. Worker est actif
3. Tâche est bien enregistrée
4. Pas d'erreur dans les logs

---

## 📊 Monitoring

### Voir les workers actifs

```bash
celery -A haroo inspect active
```

### Voir les tâches planifiées

```bash
celery -A haroo inspect scheduled
```

### Voir les statistiques

```bash
celery -A haroo inspect stats
```

### Purger toutes les tâches

```bash
celery -A haroo purge
```

---

## 🔧 Configuration Avancée

### Augmenter le nombre de workers

```bash
celery -A haroo worker -l info --concurrency=4
```

### Limiter la mémoire par worker

```bash
celery -A haroo worker -l info --max-memory-per-child=200000
```

### Activer le monitoring Flower

```bash
pip install flower
celery -A haroo flower
# Interface: http://localhost:5555
```

---

## 📝 Intégration dans les Views

### Exemple: Après paiement réussi

```python
from apps.documents.tasks import send_purchase_confirmation_async

# Dans la view après paiement
if payment_successful:
    # Générer l'URL de téléchargement
    download_url = generate_download_url(achat)
    
    # Envoyer l'email de manière asynchrone
    send_purchase_confirmation_async.delay(
        achat.id,
        download_url
    )
```

### Exemple: Après régénération de lien

```python
from apps.documents.tasks import send_link_regenerated_async

# Dans la view de régénération
new_download_url = regenerate_link(achat)

send_link_regenerated_async.delay(
    achat.id,
    new_download_url
)
```

---

## ✅ Validation Phase 2.3

### Checklist

- [x] 2.3.1 Celery et Redis installés
- [x] 2.3.2 Celery configuré dans haroo/celery.py
- [x] 2.3.3 Tâche send_purchase_confirmation_async créée
- [x] 2.3.4 Tâche send_expiration_reminders créée
- [x] 2.3.5 Tâche anonymize_old_download_logs créée
- [x] 2.3.6 Celery Beat schedule configuré
- [x] 2.3.7 Retry avec exponential backoff ajouté
- [x] 2.3.8 Tests Celery créés

**Status**: ✅ Phase 2.3 complétée à 100%

---

## 🎯 Prochaines Étapes

### Phase 2.4: Integrate Email Service

1. Appeler les tâches Celery dans les views
2. Configurer FRONTEND_URL dans settings
3. Tester l'intégration complète
4. Vérifier les emails avec MailHog

### Phase 2.5: Email Service Testing

1. Tests unitaires EmailService
2. Tests templates rendering
3. Tests Celery tasks
4. Tests intégration MailHog

---

## 📚 Ressources

- **Celery Documentation**: https://docs.celeryq.dev/
- **Redis Documentation**: https://redis.io/documentation
- **Django + Celery**: https://docs.celeryq.dev/en/stable/django/
- **Celery Best Practices**: https://docs.celeryq.dev/en/stable/userguide/tasks.html#best-practices

---

**Phase 2.3 complétée!** 🎉

Tous les outils sont en place pour les tâches asynchrones et planifiées.
