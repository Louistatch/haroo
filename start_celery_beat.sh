#!/bin/bash
# Script pour démarrer Celery Beat (tâches planifiées)
# Haroo - Plateforme Agricole Intelligente du Togo

echo "========================================"
echo "DEMARRAGE CELERY BEAT - HAROO"
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

echo "[INFO] Tâches planifiées:"
echo "  - Rappels d'expiration: Toutes les heures"
echo "  - Anonymisation logs: Quotidien à 2h00"
echo "  - Nettoyage liens: Toutes les heures"
echo ""

echo "[INFO] Démarrage de Celery Beat..."
echo ""
echo "Appuyez sur Ctrl+C pour arrêter Beat"
echo "========================================"
echo ""

# Démarrer Beat
celery -A haroo beat -l info

echo ""
echo "[INFO] Celery Beat arrêté"
