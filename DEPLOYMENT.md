# 🚀 Guide de Déploiement Production - Haroo

## Prérequis Serveur

- Ubuntu 22.04 LTS (ou Debian 12)
- Docker 20.10+ et Docker Compose 2.0+
- Nginx (installé sur l'hôte pour SSL)
- Certbot (Let's Encrypt)
- 2 vCPU, 4 GB RAM minimum
- 40 GB SSD minimum
- Domaine configuré (haroo.tg → IP serveur)

## 1. Installation Initiale

### 1.1 Préparer le serveur

```bash
# Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# Installer Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Installer Docker Compose
sudo apt install docker-compose-plugin -y

# Installer Nginx et Certbot
sudo apt install nginx certbot python3-certbot-nginx -y

# Installer AWS CLI (optionnel, pour backups S3)
sudo apt install awscli -y
```

### 1.2 Cloner le projet

```bash
sudo mkdir -p /opt/haroo
sudo chown $USER:$USER /opt/haroo
git clone <repository-url> /opt/haroo
cd /opt/haroo
```

### 1.3 Configurer l'environnement

```bash
cp .env.prod.example .env.prod

# Éditer avec vos valeurs de production
nano .env.prod
```

Variables critiques à configurer :
- `SECRET_KEY` : chaîne aléatoire de 50+ caractères
- `DB_PASSWORD` : mot de passe PostgreSQL fort
- `ALLOWED_HOSTS` : votre domaine (haroo.tg)
- `SENTRY_DSN` : URL Sentry pour le monitoring

### 1.4 Configurer SSL/TLS

```bash
# Générer les certificats Let's Encrypt
sudo certbot certonly --standalone -d haroo.tg -d www.haroo.tg

# Copier la config Nginx SSL
sudo cp nginx/nginx-ssl.conf /etc/nginx/sites-available/haroo
sudo ln -sf /etc/nginx/sites-available/haroo /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Tester et recharger Nginx
sudo nginx -t
sudo systemctl reload nginx
```

### 1.5 Créer les répertoires

```bash
mkdir -p /opt/haroo/{logs,backups,media,staticfiles}
```

## 2. Déploiement

### Premier déploiement

```bash
cd /opt/haroo

# Build et démarrer
docker-compose --env-file .env.prod build
docker-compose --env-file .env.prod up -d

# Exécuter les migrations
docker-compose exec backend python manage.py migrate

# Collecter les fichiers statiques
docker-compose exec backend python manage.py collectstatic --noinput

# Créer le superutilisateur
docker-compose exec backend python manage.py createsuperuser

# Vérifier la santé
curl http://localhost:8000/api/v1/health/
```

### Déploiements suivants

```bash
# Utiliser le script de déploiement automatisé
./scripts/deploy-production.sh deploy
```

Le script effectue automatiquement :
1. Backup pré-déploiement de la base de données
2. Pull des nouvelles images Docker
3. Redémarrage des services
4. Exécution des migrations
5. Collecte des fichiers statiques
6. Health check avec retries
7. Rollback automatique en cas d'échec

## 3. Rollback

```bash
# Rollback automatique vers la version précédente
./scripts/deploy-production.sh rollback

# Vérifier l'état après rollback
./scripts/deploy-production.sh health
```

## 4. Backups

### Backup manuel

```bash
# Backup complet (DB + media)
./scripts/backup-cron.sh

# Backup DB uniquement
./scripts/backup-cron.sh db

# Lister les backups
./scripts/backup-cron.sh list
```

### Backup automatique (crontab)

```bash
# Installer le cron de backup quotidien (02:00)
./scripts/backup-cron.sh setup-cron

# Vérifier le crontab
crontab -l
```

Crontab installé :
- `0 2 * * *` : Backup complet quotidien
- `0 3 * * *` : Renouvellement SSL Let's Encrypt

### Restauration

```bash
# Lister les backups disponibles
./scripts/backup-cron.sh list

# Restaurer un backup spécifique
./scripts/backup-cron.sh restore /opt/haroo/backups/haroo_db_20260306_020000.sql.gz
```

### Upload S3 (optionnel)

Ajouter dans `.env.prod` :
```bash
S3_BACKUP_ENABLED=true
S3_BACKUP_BUCKET=haroo-backups
S3_BACKUP_PREFIX=production
```

## 5. Monitoring

### Health check

```bash
# Health check rapide
./scripts/deploy-production.sh health

# Health check détaillé (admin requis)
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/health/detailed/
```

### État des services

```bash
# État Docker
./scripts/deploy-production.sh status

# Logs en temps réel
docker-compose logs -f backend

# Logs d'un service spécifique
docker-compose logs -f celery_worker
```

### Sentry

Le monitoring Sentry est configuré dans `haroo/settings/prod.py`. Les erreurs et performances sont automatiquement remontées vers le dashboard Sentry configuré via `SENTRY_DSN`.

## 6. Commandes Utiles

```bash
# Shell Django
docker-compose exec backend python manage.py shell

# Shell PostgreSQL
docker-compose exec db psql -U haroo_prod_user haroo_prod

# Shell Redis
docker-compose exec redis redis-cli

# Redémarrer un service
docker-compose restart backend

# Voir les ressources
docker stats
```

## 7. Troubleshooting

| Problème | Solution |
|----------|----------|
| Backend ne démarre pas | `docker-compose logs backend` pour voir les erreurs |
| Erreur de migration | `docker-compose exec backend python manage.py showmigrations` |
| Redis connexion refusée | `docker-compose restart redis` |
| Certificat SSL expiré | `sudo certbot renew --force-renewal` |
| Espace disque plein | `./scripts/backup-cron.sh cleanup` + `docker system prune` |
| Health check échoue | Vérifier DB et Redis : `docker-compose ps` |
| 502 Bad Gateway | Backend down, vérifier les logs et redémarrer |

## 8. Checklist Production

- [ ] `.env.prod` configuré avec valeurs sécurisées
- [ ] `SECRET_KEY` unique (50+ caractères)
- [ ] `DEBUG=False`
- [ ] `ALLOWED_HOSTS` configuré
- [ ] Certificats SSL installés
- [ ] Crontab backup configuré
- [ ] Sentry DSN configuré
- [ ] Firewall : ports 80, 443 uniquement
- [ ] SSH : authentification par clé uniquement
- [ ] Premier backup vérifié
- [ ] Health check fonctionnel
