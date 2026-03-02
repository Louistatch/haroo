#!/bin/bash

# Script de démarrage pour le développement
# Plateforme Agricole Togo

echo "🌾 Démarrage de la Plateforme Agricole Togo"
echo "=========================================="
echo ""

# Couleurs pour les messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Fonction pour vérifier si un port est utilisé
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0
    else
        return 1
    fi
}

# Vérifier Python
echo "🔍 Vérification de Python..."
if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python n'est pas installé${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python trouvé: $(python --version)${NC}"
echo ""

# Vérifier Node.js
echo "🔍 Vérification de Node.js..."
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js n'est pas installé${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Node.js trouvé: $(node --version)${NC}"
echo ""

# Vérifier si les ports sont disponibles
echo "🔍 Vérification des ports..."
if check_port 8000; then
    echo -e "${YELLOW}⚠️  Port 8000 déjà utilisé (Backend Django)${NC}"
    echo "   Arrêtez le processus ou utilisez un autre port"
fi

if check_port 5173; then
    echo -e "${YELLOW}⚠️  Port 5173 déjà utilisé (Frontend Vite)${NC}"
    echo "   Arrêtez le processus ou utilisez un autre port"
fi
echo ""

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo -e "${GREEN}✅ Environnement virtuel activé${NC}"
elif [ -d "venv" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✅ Environnement virtuel activé${NC}"
else
    echo -e "${YELLOW}⚠️  Aucun environnement virtuel trouvé${NC}"
    echo "   Créez-en un avec: python -m venv .venv"
fi
echo ""

# Démarrer le backend
echo "🚀 Démarrage du backend Django..."
echo "   URL: http://localhost:8000"
echo "   Admin: http://localhost:8000/admin"
echo ""

# Ouvrir un nouveau terminal pour le backend
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    osascript -e 'tell app "Terminal" to do script "cd '"$(pwd)"' && source .venv/bin/activate && python manage.py runserver"'
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    gnome-terminal -- bash -c "cd $(pwd) && source .venv/bin/activate && python manage.py runserver; exec bash"
else
    echo -e "${YELLOW}⚠️  Démarrage manuel requis${NC}"
    echo "   Ouvrez un terminal et exécutez:"
    echo "   python manage.py runserver"
fi

sleep 2

# Démarrer le frontend
echo "🚀 Démarrage du frontend Vite..."
echo "   URL: http://localhost:5173"
echo ""

# Ouvrir un nouveau terminal pour le frontend
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    osascript -e 'tell app "Terminal" to do script "cd '"$(pwd)/frontend"' && npm run dev"'
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    gnome-terminal -- bash -c "cd $(pwd)/frontend && npm run dev; exec bash"
else
    echo -e "${YELLOW}⚠️  Démarrage manuel requis${NC}"
    echo "   Ouvrez un terminal et exécutez:"
    echo "   cd frontend && npm run dev"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✨ Serveurs en cours de démarrage...${NC}"
echo ""
echo "📝 Commandes utiles:"
echo "   - Backend: http://localhost:8000"
echo "   - Frontend: http://localhost:5173"
echo "   - Admin: http://localhost:8000/admin"
echo "   - API Docs: http://localhost:8000/api/v1/"
echo ""
echo "🛑 Pour arrêter les serveurs:"
echo "   Ctrl+C dans chaque terminal"
echo ""
echo "📚 Documentation:"
echo "   - DEMARRAGE_RAPIDE.md"
echo "   - MARKETPLACE_DOCUMENTS_SUMMARY.md"
echo "=========================================="
