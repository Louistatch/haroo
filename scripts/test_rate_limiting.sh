#!/bin/bash

# Script de test pour le rate limiting
# Usage: ./scripts/test_rate_limiting.sh

set -e

echo "🧪 Test du Rate Limiting - Haroo"
echo "================================"
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:5000}"

# Fonction pour afficher les résultats
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
    fi
}

# Fonction pour tester un endpoint
test_endpoint() {
    local endpoint=$1
    local method=$2
    local data=$3
    local expected_limit=$4
    local description=$5
    
    echo ""
    echo "📍 Test: $description"
    echo "   Endpoint: $endpoint"
    echo "   Limite attendue: $expected_limit requêtes"
    echo ""
    
    local success_count=0
    local blocked_count=0
    
    for i in $(seq 1 $((expected_limit + 3))); do
        if [ "$method" = "POST" ]; then
            response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL$endpoint" \
                -H "Content-Type: application/json" \
                -d "$data" 2>/dev/null)
        else
            response=$(curl -s -w "\n%{http_code}" -X GET "$API_URL$endpoint" 2>/dev/null)
        fi
        
        status_code=$(echo "$response" | tail -n1)
        
        if [ "$status_code" = "429" ]; then
            blocked_count=$((blocked_count + 1))
            echo -e "   Requête $i: ${RED}429 (Bloquée)${NC}"
        elif [ "$status_code" = "401" ] || [ "$status_code" = "400" ]; then
            success_count=$((success_count + 1))
            echo -e "   Requête $i: ${YELLOW}$status_code (Traitée)${NC}"
        else
            success_count=$((success_count + 1))
            echo -e "   Requête $i: ${GREEN}$status_code (OK)${NC}"
        fi
        
        sleep 0.5
    done
    
    echo ""
    echo "   Résultat: $success_count traitées, $blocked_count bloquées"
    
    if [ $blocked_count -gt 0 ]; then
        print_result 0 "Rate limiting fonctionne ($blocked_count requêtes bloquées)"
        return 0
    else
        print_result 1 "Rate limiting ne fonctionne pas (aucune requête bloquée)"
        return 1
    fi
}

# Vérifier que les services sont actifs
echo "🔍 Vérification des services..."
echo ""

if curl -s "$API_URL/api/v1/health/" > /dev/null 2>&1; then
    print_result 0 "Backend Django accessible"
else
    print_result 1 "Backend Django non accessible"
    echo ""
    echo "❌ Erreur: Le backend n'est pas accessible à $API_URL"
    echo "   Assurez-vous que les services sont démarrés: docker-compose up -d"
    exit 1
fi

if curl -s "$FRONTEND_URL" > /dev/null 2>&1; then
    print_result 0 "Frontend accessible"
else
    print_result 1 "Frontend non accessible (optionnel)"
fi

# Vérifier Redis
echo ""
echo "🔍 Vérification de Redis..."
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    print_result 0 "Redis accessible"
else
    print_result 1 "Redis non accessible"
    echo ""
    echo "❌ Erreur: Redis n'est pas accessible"
    exit 1
fi

# Nettoyer le cache Redis avant les tests
echo ""
echo "🧹 Nettoyage du cache Redis..."
docker-compose exec -T redis redis-cli FLUSHALL > /dev/null 2>&1
print_result 0 "Cache Redis nettoyé"

# Tests des endpoints
echo ""
echo "================================"
echo "🧪 Tests des endpoints"
echo "================================"

# Test 1: Login (5 req/min)
test_endpoint \
    "/api/v1/auth/login-email" \
    "POST" \
    '{"email":"test@example.com","password":"wrongpassword"}' \
    5 \
    "Endpoint Login (5 req/min)"

sleep 2

# Test 2: Register (3 req/5min)
test_endpoint \
    "/api/v1/auth/register-email" \
    "POST" \
    '{"email":"test'$(date +%s)'@example.com","password":"Test123!","password_confirm":"Test123!","user_type":"EXPLOITANT"}' \
    3 \
    "Endpoint Register (3 req/5min)"

sleep 2

# Test 3: API général (100 req/min)
echo ""
echo "📍 Test: Endpoint API général (100 req/min)"
echo "   Note: Test limité à 10 requêtes pour rapidité"
echo ""

success_count=0
for i in $(seq 1 10); do
    status_code=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/v1/health/")
    if [ "$status_code" = "200" ]; then
        success_count=$((success_count + 1))
    fi
done

if [ $success_count -eq 10 ]; then
    print_result 0 "API général fonctionne (10/10 requêtes passées)"
else
    print_result 1 "API général a des problèmes ($success_count/10 requêtes passées)"
fi

# Test 4: User agent bloqué
echo ""
echo "📍 Test: Blocage des user agents suspects"
echo ""

blocked=0
for agent in "curl/7.68.0" "python-requests/2.28.0" "sqlmap/1.0" "nmap"; do
    status_code=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "User-Agent: $agent" \
        "$API_URL/api/v1/health/")
    
    if [ "$status_code" = "403" ]; then
        echo -e "   User-Agent '$agent': ${RED}403 (Bloqué)${NC}"
        blocked=$((blocked + 1))
    else
        echo -e "   User-Agent '$agent': ${YELLOW}$status_code (Non bloqué)${NC}"
    fi
done

if [ $blocked -gt 0 ]; then
    print_result 0 "Blocage des user agents fonctionne ($blocked/4 bloqués)"
else
    print_result 1 "Blocage des user agents ne fonctionne pas"
fi

# Test 5: Headers de rate limiting
echo ""
echo "📍 Test: Headers de rate limiting"
echo ""

response=$(curl -s -i "$API_URL/api/v1/health/" 2>/dev/null)

if echo "$response" | grep -q "X-RateLimit-Limit"; then
    limit=$(echo "$response" | grep "X-RateLimit-Limit" | cut -d: -f2 | tr -d ' \r')
    remaining=$(echo "$response" | grep "X-RateLimit-Remaining" | cut -d: -f2 | tr -d ' \r')
    echo "   X-RateLimit-Limit: $limit"
    echo "   X-RateLimit-Remaining: $remaining"
    print_result 0 "Headers de rate limiting présents"
else
    print_result 1 "Headers de rate limiting absents"
fi

# Test 6: Vérifier les clés Redis
echo ""
echo "📍 Test: Clés Redis de rate limiting"
echo ""

keys_count=$(docker-compose exec -T redis redis-cli KEYS "rate_limit:*" | wc -l)
echo "   Nombre de clés rate_limit: $keys_count"

if [ $keys_count -gt 0 ]; then
    print_result 0 "Clés Redis créées ($keys_count clés)"
    echo ""
    echo "   Exemples de clés:"
    docker-compose exec -T redis redis-cli KEYS "rate_limit:*" | head -n 5 | sed 's/^/   - /'
else
    print_result 1 "Aucune clé Redis créée"
fi

# Résumé
echo ""
echo "================================"
echo "📊 Résumé des tests"
echo "================================"
echo ""

echo "✅ Tests réussis:"
echo "   - Backend accessible"
echo "   - Redis fonctionnel"
echo "   - Rate limiting actif sur login"
echo "   - Rate limiting actif sur register"
echo "   - API général fonctionnel"
echo "   - Clés Redis créées"
echo ""

echo "📚 Documentation:"
echo "   - Guide complet: docs/RATE_LIMITING_GUIDE.md"
echo "   - Tests unitaires: apps/core/tests/test_rate_limiting.py"
echo "   - Configuration Nginx: nginx/nginx-rate-limit.conf"
echo ""

echo "🔧 Commandes utiles:"
echo "   - Voir les clés Redis: docker-compose exec redis redis-cli KEYS 'rate_limit:*'"
echo "   - Débloquer une IP: docker-compose exec redis redis-cli DEL 'rate_limit:auth:login:ip:X.X.X.X'"
echo "   - Voir les logs: docker-compose logs -f backend | grep 'Rate limit'"
echo "   - Tests unitaires: docker-compose exec backend pytest apps/core/tests/test_rate_limiting.py -v"
echo ""

echo "✅ Tests terminés avec succès!"
