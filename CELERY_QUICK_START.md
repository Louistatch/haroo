# Celery - Guide Rapide

## 🚀 Démarrage en 3 Minutes

### 1. Démarrer Redis
```bash
redis-server
```

### 2. Démarrer Celery Worker
```bash
# Windows
start_celery_worker.bat

# Linux/macOS
./start_celery_worker.sh
```

### 3. Tester
```bash
python test_celery_tasks.py
```

---

## 📋 Tâches Disponibles

### Asynchrones (à appeler manuellement)

```python
# Confirmation d'achat
from apps.documents.tasks import send_purchase_confirmation_async
send_purchase_confirmation_async.delay(achat_id, download_url)

# Lien régénéré
from apps.documents.tasks import send_link_regenerated_async
send_link_regenerated_async.delay(achat_id, download_url)
```

### Planifiées (automatiques)

- **Rappels d'expiration**: Toutes les heures
- **Anonymisation logs**: Quotidien à 2h00
- **Nettoyage liens**: Toutes les heures

---

## 🔧 Commandes Utiles

```bash
# Démarrer worker
celery -A haroo worker -l info

# Démarrer beat (tâches planifiées)
celery -A haroo beat -l info

# Worker + Beat combiné
celery -A haroo worker -B -l info

# Voir workers actifs
celery -A haroo inspect active

# Voir tâches planifiées
celery -A haroo inspect scheduled

# Purger toutes les tâches
celery -A haroo purge
```

---

## ✅ Phase 2.3 Complétée

Toutes les subtasks (2.3.1 à 2.3.8) sont terminées!

**Prochaine étape**: Phase 2.4 - Intégrer EmailService dans les views

---

## 📚 Documentation Complète

Voir `PHASE_2.3_CELERY_GUIDE.md` pour plus de détails.
