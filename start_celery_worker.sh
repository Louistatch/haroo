#!/bin/bash
# Script pour démarrer le worker Celery
# Haroo - Plateforme Agricole Intelligente du Togo

echo "========================================"
echo "DEMARRAGE CELERY WORKER - HAROO"
echo "========================================"
echo ""

# Vérifier que l'environnement virtuel est activé
if [ -z "$VIRTUAL_ENV" ]; then
    echo "[ERREUR] Environnement virtuel non activé"
    echo ""
    echo "Activez l'environnement virtuel:"
    echo "  source .venv/bin/activate"
    echo ""
    exit 1
fi

echo "[OK] Environnement virtuel activé"
echo ""

# Vérifier que Redis est accessible
echo "[INFO] Vérification de Redis..."
if ! python -c "import redis; r = redis.Redis(host='localhost', port=6379); r.ping()" 2>/dev/null; then
    echo "[ERREUR] Redis n'est pas accessible"
    echo ""
    echo "Démarrez Redis:"
    echo "  redis-server"
    echo ""
    echo "Ou installez Redis:"
    echo "  macOS: brew install redis"
    echo "  Linux: sudo apt-get install redis-server"
    echo ""
    exit 1
fi

echo "[OK] Redis est accessible"
echo ""

echo "[INFO] Démarrage du worker Celery..."
echo ""
echo "Configuration:"
echo "  - Broker: Redis (localhost:6379/2)"
echo "  - Backend: Redis (localhost:6379/3)"
echo "  - Timezone: Africa/Lome"
echo "  - Log level: INFO"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter le worker"
echo "========================================"
echo ""

# Démarrer le worker
celery -A haroo worker -l info

echo ""
echo "[INFO] Worker Celery arrêté"
