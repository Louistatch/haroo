#!/bin/bash
# =============================================================================
# TASK-10.1: Script de déploiement production pour Haroo
#
# Usage:
#   ./scripts/deploy-production.sh deploy     # Déployer la dernière version
#   ./scripts/deploy-production.sh rollback   # Revenir à la version précédente
#   ./scripts/deploy-production.sh backup     # Backup base de données
#   ./scripts/deploy-production.sh status     # Vérifier l'état des services
#   ./scripts/deploy-production.sh health     # Health check complet
# =============================================================================

set -euo pipefail

# --- Configuration ---
APP_DIR="${APP_DIR:-/opt/haroo}"
BACKUP_DIR="${BACKUP_DIR:-/opt/haroo/backups}"
ENV_FILE="${APP_DIR}/.env.prod"
COMPOSE_FILE="${APP_DIR}/docker-compose.yml"
MAX_BACKUPS=7
HEALTH_CHECK_URL="http://localhost:8000/api/v1/health/"
HEALTH_CHECK_RETRIES=10
HEALTH_CHECK_INTERVAL=5
LOG_FILE="${APP_DIR}/logs/deploy.log"

# --- Couleurs ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE" 2>/dev/null || echo "$1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE" 2>/dev/null || echo "$1"; }
error() { echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE" 2>/dev/null || echo "$1"; }

# --- Fonctions ---

backup_database() {
    log "📦 Backup de la base de données..."
    mkdir -p "$BACKUP_DIR"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="${BACKUP_DIR}/haroo_db_${timestamp}.sql.gz"

    docker-compose -f "$COMPOSE_FILE" exec -T db \
        pg_dump -U haroo_prod_user haroo_prod --clean --if-exists | gzip > "$backup_file"

    if [ $? -eq 0 ] && [ -s "$backup_file" ]; then
        log "✅ Backup créé: $backup_file ($(du -h "$backup_file" | cut -f1))"
    else
        error "❌ Échec du backup"
        rm -f "$backup_file"
        return 1
    fi

    # Rotation: garder les N derniers backups
    local count=$(ls -1 "$BACKUP_DIR"/haroo_db_*.sql.gz 2>/dev/null | wc -l)
    if [ "$count" -gt "$MAX_BACKUPS" ]; then
        ls -1t "$BACKUP_DIR"/haroo_db_*.sql.gz | tail -n +$((MAX_BACKUPS + 1)) | xargs rm -f
        log "🗑️  Anciens backups supprimés (conservation: $MAX_BACKUPS)"
    fi
}

backup_media() {
    log "📦 Backup des fichiers media..."
    mkdir -p "$BACKUP_DIR"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="${BACKUP_DIR}/haroo_media_${timestamp}.tar.gz"

    if [ -d "${APP_DIR}/media" ]; then
        tar -czf "$backup_file" -C "${APP_DIR}" media/ 2>/dev/null
        log "✅ Media backup: $backup_file ($(du -h "$backup_file" | cut -f1))"
    else
        warn "Pas de dossier media à sauvegarder"
    fi
}

health_check() {
    log "🏥 Health check..."
    local retries=$HEALTH_CHECK_RETRIES

    while [ $retries -gt 0 ]; do
        local status=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_CHECK_URL" 2>/dev/null || echo "000")
        if [ "$status" = "200" ]; then
            log "✅ Health check OK (HTTP $status)"
            return 0
        fi
        retries=$((retries - 1))
        warn "Health check échoué (HTTP $status), $retries tentatives restantes..."
        sleep $HEALTH_CHECK_INTERVAL
    done

    error "❌ Health check échoué après $HEALTH_CHECK_RETRIES tentatives"
    return 1
}

deploy() {
    log "🚀 Déploiement en production..."

    # Vérifier les prérequis
    if [ ! -f "$ENV_FILE" ]; then
        error "Fichier $ENV_FILE introuvable. Copiez .env.prod.example vers .env.prod"
        exit 1
    fi

    # 1. Backup pré-déploiement
    log "📦 Backup pré-déploiement..."
    backup_database || { error "Backup échoué, déploiement annulé"; exit 1; }

    # 2. Sauvegarder la version actuelle pour rollback
    local current_images=$(docker-compose -f "$COMPOSE_FILE" images -q 2>/dev/null || true)
    echo "$current_images" > "${BACKUP_DIR}/.previous_images"
    docker-compose -f "$COMPOSE_FILE" config > "${BACKUP_DIR}/.previous_compose.yml" 2>/dev/null || true

    # 3. Pull les nouvelles images
    log "⬇️  Pull des nouvelles images..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" pull

    # 4. Arrêter et redémarrer les services
    log "🔄 Redémarrage des services..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d

    # 5. Attendre que les services démarrent
    log "⏳ Attente du démarrage des services..."
    sleep 15

    # 6. Exécuter les migrations
    log "🔄 Exécution des migrations..."
    docker-compose -f "$COMPOSE_FILE" exec -T backend python manage.py migrate --noinput

    # 7. Collecter les fichiers statiques
    log "📦 Collecte des fichiers statiques..."
    docker-compose -f "$COMPOSE_FILE" exec -T backend python manage.py collectstatic --noinput

    # 8. Health check
    if health_check; then
        log "🎉 Déploiement réussi!"
        docker-compose -f "$COMPOSE_FILE" ps
    else
        error "❌ Déploiement échoué, rollback automatique..."
        rollback
        exit 1
    fi
}

rollback() {
    log "⏪ Rollback vers la version précédente..."

    if [ ! -f "${BACKUP_DIR}/.previous_compose.yml" ]; then
        error "Pas de version précédente disponible pour le rollback"
        exit 1
    fi

    # Arrêter les services actuels
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down

    # Redémarrer avec la config précédente
    docker-compose -f "${BACKUP_DIR}/.previous_compose.yml" up -d

    sleep 15

    if health_check; then
        log "✅ Rollback réussi"
    else
        error "❌ Rollback échoué - intervention manuelle requise"
        exit 1
    fi
}

status() {
    log "📊 État des services Haroo:"
    docker-compose -f "$COMPOSE_FILE" ps
    echo ""
    log "📊 Utilisation des ressources:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" \
        $(docker-compose -f "$COMPOSE_FILE" ps -q 2>/dev/null) 2>/dev/null || warn "Impossible de récupérer les stats"
}

# --- Main ---
case "${1:-help}" in
    deploy)   deploy ;;
    rollback) rollback ;;
    backup)   backup_database && backup_media ;;
    status)   status ;;
    health)   health_check ;;
    *)
        echo "Usage: $0 {deploy|rollback|backup|status|health}"
        echo ""
        echo "  deploy    - Déployer la dernière version (avec backup auto)"
        echo "  rollback  - Revenir à la version précédente"
        echo "  backup    - Backup base de données + media"
        echo "  status    - État des services"
        echo "  health    - Health check"
        ;;
esac
