#!/bin/bash
# Script pour démarrer MailHog et ouvrir l'interface web
# Haroo - Plateforme Agricole Intelligente du Togo

echo "========================================"
echo "DEMARRAGE MAILHOG - HAROO"
echo "========================================"
echo ""

# Vérifier si MailHog est installé
if ! command -v mailhog &> /dev/null; then
    echo "[ERREUR] MailHog n'est pas installé"
    echo ""
    echo "Installation:"
    echo "  macOS: brew install mailhog"
    echo "  Linux: wget https://github.com/mailhog/MailHog/releases/download/v1.0.1/MailHog_linux_amd64"
    echo "         chmod +x MailHog_linux_amd64"
    echo "         sudo mv MailHog_linux_amd64 /usr/local/bin/mailhog"
    echo ""
    exit 1
fi

echo "[OK] MailHog est installé"
echo ""

# Vérifier si MailHog est déjà en cours d'exécution
if lsof -Pi :1025 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "[INFO] MailHog semble déjà en cours d'exécution"
    echo ""
    read -p "Voulez-vous ouvrir l'interface web? (o/n) " OPEN_WEB
    if [[ "$OPEN_WEB" =~ ^[Oo]$ ]]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            open http://localhost:8025
        else
            xdg-open http://localhost:8025 2>/dev/null || echo "Ouvrez http://localhost:8025 dans votre navigateur"
        fi
    fi
    exit 0
fi

echo "[INFO] Démarrage de MailHog..."
echo ""
echo "Interface web: http://localhost:8025"
echo "Serveur SMTP: localhost:1025"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter MailHog"
echo "========================================"
echo ""

# Démarrer MailHog en arrière-plan
mailhog &
MAILHOG_PID=$!

# Attendre 2 secondes
sleep 2

# Ouvrir l'interface web
if [[ "$OSTYPE" == "darwin"* ]]; then
    open http://localhost:8025
else
    xdg-open http://localhost:8025 2>/dev/null || echo "Ouvrez http://localhost:8025 dans votre navigateur"
fi

echo ""
echo "[OK] MailHog démarré! (PID: $MAILHOG_PID)"
echo "[OK] Interface web ouverte dans le navigateur"
echo ""
echo "Pour envoyer des emails de test:"
echo "  1. Ouvrir un nouveau terminal"
echo "  2. Activer l'environnement virtuel: source .venv/bin/activate"
echo "  3. Exécuter: python send_test_emails.py"
echo ""
echo "Pour arrêter MailHog: kill $MAILHOG_PID"
echo ""

# Attendre que l'utilisateur arrête MailHog
wait $MAILHOG_PID
