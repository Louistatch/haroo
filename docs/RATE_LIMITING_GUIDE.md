# Guide du Rate Limiting - Haroo

## Vue d'ensemble

Haroo implémente un système de rate limiting robuste à plusieurs niveaux pour protéger l'API contre les abus, les attaques par force brute et les dénis de service (DoS).

## Architecture

### Niveaux de protection

```
┌─────────────────────────────────────────────────────────┐
│                    Client (Browser/App)                  │
└────────────────────────┬────────────────────────────────┘
                         │
                    ┌────▼────┐
                    │  Nginx  │ ← Rate Limiting Infrastructure
                    │  Proxy  │   (200 req/min global)
                    └────┬────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────▼────┐     ┌────▼────┐     ┌────▼────┐
   │  Auth   │     │   API   │     │ Payment │
   │ 5/min   │     │ 10/sec  │     │  2/min  │
   └────┬────┘     └────┬────┘     └────┬────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
                    ┌────▼────┐
                    │ Django  │ ← Rate Limiting Application
                    │   App   │   (Sliding Window)
                    └────┬────┘
                         │
                    ┌────▼────┐
                    │  Redis  │ ← Stockage des compteurs
                    └─────────┘
```

### Composants

1. **Nginx Rate Limiting** (Infrastructure)
   - Protection au niveau du reverse proxy
   - Bloque les requêtes avant qu'elles n'atteignent Django
   - Très performant (pas de traitement Python)

2. **Django Rate Limiting** (Application)
   - Sliding window pour comptage précis
   - Rate limiting par utilisateur authentifié
   - Décorateurs pour faciliter l'utilisation

3. **Redis** (Stockage)
   - Stockage des compteurs de requêtes
   - Expiration automatique des clés
   - Performance élevée

## Configuration

### Limites par défaut

| Endpoint | Limite | Fenêtre | Burst |
|----------|--------|---------|-------|
| `/api/v1/auth/login` | 5 req | 1 min | 2 |
| `/api/v1/auth/register` | 3 req | 5 min | 1 |
| `/api/v1/auth/verify-sms` | 10 req | 1 min | 5 |
| `/api/v1/payments/*` | 2 req | 1 min | 1 |
| `/api/*` (général) | 10 req | 1 sec | 20 |
| Global | 200 req | 1 min | 20 |

### Modifier les limites

#### Django (Application)

Éditez `apps/core/rate_limiting.py`:

```python
class RateLimitConfig:
    # Modifier la limite de login
    AUTH_LOGIN = SlidingWindowRateLimiter(
        max_requests=10,  # Augmenter à 10
        window_seconds=60,
        key_prefix="rate_limit:auth:login"
    )
```

#### Nginx (Infrastructure)

Éditez `nginx/nginx-rate-limit.conf`:

```nginx
# Modifier la zone de rate limiting
limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=10r/m;  # 10 req/min

# Modifier le burst
location ~ ^/api/v1/auth/login {
    limit_req zone=auth_limit burst=5 nodelay;  # Burst de 5
    ...
}
```

## Utilisation

### Décorateur sur une vue

```python
from apps.core.rate_limiting import rate_limit, RateLimitConfig
from rest_framework.decorators import api_view

@rate_limit(RateLimitConfig.AUTH_LOGIN)
@api_view(['POST'])
def custom_login(request):
    # Votre logique ici
    return Response({'message': 'Success'})
```

### Créer un limiter personnalisé

```python
from apps.core.rate_limiting import SlidingWindowRateLimiter, rate_limit

# Créer un limiter pour un endpoint spécifique
custom_limiter = SlidingWindowRateLimiter(
    max_requests=20,
    window_seconds=300,  # 20 requêtes par 5 minutes
    key_prefix="rate_limit:custom"
)

@rate_limit(custom_limiter)
@api_view(['POST'])
def my_endpoint(request):
    return Response({'data': 'something'})
```

### Vérifier manuellement le rate limit

```python
from apps.core.rate_limiting import RateLimitConfig, get_client_identifier

def my_view(request):
    identifier = get_client_identifier(request)
    is_allowed, info = RateLimitConfig.AUTH_LOGIN.is_allowed(identifier)
    
    if not is_allowed:
        return Response({
            'error': 'Trop de requêtes',
            'retry_after': info['retry_after']
        }, status=429)
    
    # Continuer le traitement
    ...
```

## Réponses d'erreur

### Format de réponse 429

```json
{
  "error": "Trop de requêtes",
  "message": "Limite de 5 requêtes par 60 secondes atteinte.",
  "retry_after": 45,
  "reset_at": "2026-03-06T15:30:00Z"
}
```

### Headers de réponse

```
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 2026-03-06T15:30:00Z
Retry-After: 45
```

## Monitoring

### Logs de sécurité

Les tentatives d'abus sont loggées dans `logs/security.log`:

```
2026-03-06 15:25:30 WARNING Rate limit exceeded: ip:192.168.1.100 | 
Path: /api/v1/auth/login | Method: POST | 
User-Agent: curl/7.68.0 | Retry after: 45s
```

### Métriques Redis

Vérifier les clés de rate limiting:

```bash
# Connexion à Redis
docker-compose exec redis redis-cli

# Lister les clés de rate limiting
KEYS rate_limit:*

# Voir le contenu d'une clé
GET rate_limit:auth:login:ip:192.168.1.100

# Supprimer une clé (débloquer un utilisateur)
DEL rate_limit:auth:login:ip:192.168.1.100
```

### Dashboard Nginx

Vérifier les logs Nginx:

```bash
# Voir les requêtes bloquées par rate limit
docker-compose exec frontend tail -f /var/log/nginx/haroo_error.log | grep "limiting requests"

# Compter les 429 par IP
docker-compose exec frontend awk '$9 == 429 {print $1}' /var/log/nginx/haroo_access.log | sort | uniq -c | sort -rn
```

## Sécurité

### User Agents bloqués

Les user agents suivants sont automatiquement bloqués:

- `bot`, `crawler`, `spider`, `scraper`
- `curl`, `wget`, `python-requests`
- `masscan`, `nmap`, `nikto`, `sqlmap`

### Débloquer un utilisateur

Si un utilisateur légitime est bloqué:

```bash
# Via Redis CLI
docker-compose exec redis redis-cli
DEL rate_limit:auth:login:ip:192.168.1.100

# Via Django shell
docker-compose exec backend python manage.py shell
>>> from django.core.cache import cache
>>> cache.delete('rate_limit:auth:login:ip:192.168.1.100')
```

### Whitelist d'IPs

Pour exempter certaines IPs du rate limiting (ex: monitoring):

Éditez `nginx/nginx-rate-limit.conf`:

```nginx
# Définir une map pour les IPs whitelistées
geo $limit {
    default 1;
    192.168.1.50 0;  # IP de monitoring
    10.0.0.0/8 0;    # Réseau interne
}

map $limit $limit_key {
    0 "";
    1 $binary_remote_addr;
}

# Utiliser $limit_key au lieu de $binary_remote_addr
limit_req_zone $limit_key zone=auth_limit:10m rate=5r/m;
```

## Tests

### Tester le rate limiting

```bash
# Exécuter les tests
docker-compose exec backend pytest apps/core/tests/test_rate_limiting.py -v

# Tester manuellement avec curl
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/v1/auth/login-email \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"wrong"}' \
    -w "\nStatus: %{http_code}\n"
  sleep 1
done
```

### Test de charge

```bash
# Installer Apache Bench
sudo apt-get install apache2-utils

# Tester avec 100 requêtes, 10 concurrentes
ab -n 100 -c 10 -p login.json -T application/json \
  http://localhost:8000/api/v1/auth/login-email

# Contenu de login.json
echo '{"email":"test@example.com","password":"test"}' > login.json
```

## Troubleshooting

### Problème: Utilisateurs légitimes bloqués

**Symptôme**: Des utilisateurs normaux reçoivent des erreurs 429

**Solutions**:
1. Augmenter les limites dans la configuration
2. Vérifier si plusieurs utilisateurs partagent la même IP (NAT)
3. Utiliser l'authentification pour rate limiting par user_id

### Problème: Rate limiting ne fonctionne pas

**Symptôme**: Pas de blocage même après beaucoup de requêtes

**Vérifications**:
1. Redis est-il actif? `docker-compose ps redis`
2. Le middleware est-il activé dans settings?
3. Les logs montrent-ils des erreurs?

```bash
# Vérifier Redis
docker-compose exec redis redis-cli ping
# Devrait retourner: PONG

# Vérifier les logs Django
docker-compose logs backend | grep -i "rate"
```

### Problème: Performance dégradée

**Symptôme**: L'API est lente

**Solutions**:
1. Vérifier la latence Redis: `redis-cli --latency`
2. Augmenter la mémoire Redis si nécessaire
3. Optimiser les clés de cache (TTL plus court)

## Best Practices

### 1. Rate limiting par utilisateur authentifié

Préférez le rate limiting par user_id plutôt que par IP pour les utilisateurs authentifiés:

```python
def get_client_identifier(request) -> str:
    if hasattr(request, 'user') and request.user.is_authenticated:
        return f"user:{request.user.id}"  # ✅ Meilleur
    return f"ip:{get_ip(request)}"  # ⚠️ Fallback
```

### 2. Messages d'erreur clairs

Toujours inclure `retry_after` dans les réponses 429:

```python
return Response({
    'error': 'Trop de requêtes',
    'retry_after': info['retry_after'],  # ✅ Important
    'reset_at': info['reset_at']
}, status=429)
```

### 3. Limites différenciées

Utilisez des limites différentes selon le type d'endpoint:

- **Authentification**: Très restrictif (5/min)
- **Lecture**: Modéré (100/min)
- **Écriture**: Restrictif (30/min)
- **Paiement**: Très restrictif (2/min)

### 4. Monitoring proactif

Configurez des alertes pour:
- Taux élevé de 429 (> 5% des requêtes)
- IPs avec beaucoup de tentatives bloquées
- Patterns d'attaque (même endpoint, même user agent)

### 5. Documentation API

Documentez les limites dans votre API:

```python
@extend_schema(
    summary="Login",
    description="Rate limit: 5 requêtes par minute",
    responses={
        200: UserSerializer,
        429: OpenApiResponse(description="Trop de requêtes")
    }
)
def login_view(request):
    ...
```

## Références

- [OWASP Rate Limiting](https://owasp.org/www-community/controls/Blocking_Brute_Force_Attacks)
- [Nginx Rate Limiting](https://www.nginx.com/blog/rate-limiting-nginx/)
- [Redis Best Practices](https://redis.io/docs/manual/patterns/rate-limiter/)
- [RFC 6585 - HTTP 429](https://tools.ietf.org/html/rfc6585#section-4)

## Support

Pour toute question ou problème:
- Ouvrir une issue sur GitHub
- Contacter l'équipe DevOps
- Consulter les logs: `docker-compose logs -f backend`
