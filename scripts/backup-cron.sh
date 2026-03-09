#!/bin/bash
# =============================================================================
# TASK-10.3: Script de backup automatique pour Haroo
#
# Usage:
#   ./scripts/backup-cron.sh                  # Backup complet (DB + media)
#   ./scripts/backup-cron.sh db               # Backup base de données uniquement
#   ./scripts/backup-cron.sh media            # Backup fichiers media uniquement
#   ./scripts/backup-cron.sh restore <file>   # Restaurer un backup DB
#   ./scripts/backup-cron.sh list             # Lister les backups disponibles
#   ./scripts/backup-cron.sh setup-cron       # Installer le crontab automatique
#
# Crontab (backup quotidien à 2h du matin):
#   0 2 * * * /opt/haroo/scripts/backup-cron.sh >> /opt/haroo/logs/backup.log 2>&1
# =============================================================================

set -euo pipefail

# --- Configuration ---
APP_DIR="${APP_DIR:-/opt/haroo}"
BACKUP_DIR="${BACKUP_DIR:-/opt/haroo/backups}"
COMPOSE_FILE="${APP_DIR}/docker-compose.yml"
RETENTION_DAYS=7
LOG_FILE="${APP_DIR}/logs/backup.log"
DATE=$(date +%Y%m%d_%H%M%S)

# S3 Upload (optionnel)
S3_ENABLED="${S3_BACKUP_ENABLED:-false}"
S3_BUCKET="${S3_BACKUP_BUCKET:-}"
S3_PREFIX="${S3_BACKUP_PREFIX:-haroo-backups}"

# DB credentials (depuis docker-compose env)
DB_USER="${DB_USER:-haroo_prod_user}"
DB_NAME="${DB_NAME:-haroo_prod}"

# --- Couleurs ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE" 2>/dev/null || echo "$1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE" 2>/dev/null || echo "$1"; }
error() { echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE" 2>/dev/null || echo "$1"; }

# --- Fonctions ---

init() {
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$(dirname "$LOG_FILE")"
}

backup_database() {
    log "📦 Backup PostgreSQL..."
    local backup_file="${BACKUP_DIR}/haroo_db_${DATE}.sql.gz"

    docker-compose -f "$COMPOSE_FILE" exec -T db \
        pg_dump -U "$DB_USER" "$DB_NAME" --clean --if-exists | gzip > "$backup_file"

    if [ $? -eq 0 ] && [ -s "$backup_file" ]; then
        local size=$(du -h "$backup_file" | cut -f1)
        log "✅ DB backup: $backup_file ($size)"
        echo "$backup_file"
    else
        error "❌ Échec du backup DB"
        rm -f "$backup_file"
        return 1
    fi
}

backup_media() {
    log "📦 Backup fichiers media..."
    local backup_file="${BACKUP_DIR}/haroo_media_${DATE}.tar.gz"

    if [ -d "${APP_DIR}/media" ] && [ "$(ls -A "${APP_DIR}/media" 2>/dev/null)" ]; then
        tar -czf "$backup_file" -C "${APP_DIR}" media/ 2>/dev/null
        local size=$(du -h "$backup_file" | cut -f1)
        log "✅ Media backup: $backup_file ($size)"
        echo "$backup_file"
    else
        warn "Pas de fichiers media à sauvegarder"
    fi
}

upload_to_s3() {
    local file="$1"
    if [ "$S3_ENABLED" = "true" ] && [ -n "$S3_BUCKET" ]; then
        log "☁️  Upload vers S3: s3://${S3_BUCKET}/${S3_PREFIX}/$(basename "$file")"
        aws s3 cp "$file" "s3://${S3_BUCKET}/${S3_PREFIX}/$(basename "$file")" --quiet
        if [ $? -eq 0 ]; then
            log "✅ Upload S3 réussi"
        else
            warn "Upload S3 échoué (backup local conservé)"
        fi
    fi
}

cleanup_old_backups() {
    log "🗑️  Nettoyage des backups > ${RETENTION_DAYS} jours..."
    local count=0

    # Supprimer les backups DB anciens
    while IFS= read -r file; do
        rm -f "$file"
        count=$((count + 1))
    done < <(find "$BACKUP_DIR" -name "haroo_db_*.sql.gz" -mtime +${RETENTION_DAYS} 2>/dev/null)

    # Supprimer les backups media anciens
    while IFS= read -r file; do
        rm -f "$file"
        count=$((count + 1))
    done < <(find "$BACKUP_DIR" -name "haroo_media_*.tar.gz" -mtime +${RETENTION_DAYS} 2>/dev/null)

    if [ $count -gt 0 ]; then
        log "✅ $count ancien(s) backup(s) supprimé(s)"
    else
        log "Aucun ancien backup à supprimer"
    fi
}

restore_database() {
    local backup_file="$1"

    if [ ! -f "$backup_file" ]; then
        error "Fichier introuvable: $backup_file"
        exit 1
    fi

    warn "⚠️  Restauration de: $backup_file"
    warn "⚠️  Cela va ÉCRASER la base de données actuelle!"
    read -p "Continuer? (y/N): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        log "Restauration annulée"
        exit 0
    fi

    log "🔄 Restauration en cours..."
    if [[ "$backup_file" == *.gz ]]; then
        gunzip -c "$backup_file" | docker-compose -f "$COMPOSE_FILE" exec -T db \
            psql -U "$DB_USER" "$DB_NAME"
    else
        docker-compose -f "$COMPOSE_FILE" exec -T db \
            psql -U "$DB_USER" "$DB_NAME" < "$backup_file"
    fi

    if [ $? -eq 0 ]; then
        log "✅ Restauration réussie"
    else
        error "❌ Échec de la restauration"
        return 1
    fi
}

list_backups() {
    log "📋 Backups disponibles dans $BACKUP_DIR:"
    echo ""
    echo "--- Backups DB ---"
    ls -lh "$BACKUP_DIR"/haroo_db_*.sql.gz 2>/dev/null || echo "  Aucun backup DB"
    echo ""
    echo "--- Backups Media ---"
    ls -lh "$BACKUP_DIR"/haroo_media_*.tar.gz 2>/dev/null || echo "  Aucun backup media"
    echo ""

    local total_size=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)
    echo "Espace total utilisé: ${total_size:-0}"
}

setup_cron() {
    local cron_entry="0 2 * * * ${APP_DIR}/scripts/backup-cron.sh >> ${APP_DIR}/logs/backup.log 2>&1"

    # Vérifier si le cron existe déjà
    if crontab -l 2>/dev/null | grep -q "backup-cron.sh"; then
        warn "Crontab déjà configuré"
        crontab -l | grep "backup-cron.sh"
    else
        (crontab -l 2>/dev/null; echo "$cron_entry") | crontab -
        log "✅ Crontab installé: backup quotidien à 02:00"
        echo "  $cron_entry"
    fi

    # Ajouter aussi le renouvellement SSL
    local ssl_entry="0 3 * * * certbot renew --quiet --post-hook 'nginx -s reload'"
    if ! crontab -l 2>/dev/null | grep -q "certbot renew"; then
        (crontab -l 2>/dev/null; echo "$ssl_entry") | crontab -
        log "✅ Crontab SSL: renouvellement quotidien à 03:00"
    fi
}

full_backup() {
    log "=========================================="
    log "🚀 Backup complet Haroo - $DATE"
    log "=========================================="

    init

    # Backup DB
    local db_file
    db_file=$(backup_database) || { error "Backup DB échoué"; exit 1; }

    # Backup media
    local media_file
    media_file=$(backup_media) || true

    # Upload S3
    [ -n "${db_file:-}" ] && upload_to_s3 "$db_file"
    [ -n "${media_file:-}" ] && upload_to_s3 "$media_file"

    # Nettoyage
    cleanup_old_backups

    log "=========================================="
    log "✅ Backup complet terminé"
    log "=========================================="
}

# --- Main ---
init

case "${1:-full}" in
    full|"")    full_backup ;;
    db)         backup_database && cleanup_old_backups ;;
    media)      backup_media ;;
    restore)    restore_database "${2:-}" ;;
    list)       list_backups ;;
    setup-cron) setup_cron ;;
    cleanup)    cleanup_old_backups ;;
    *)
        echo "Usage: $0 {full|db|media|restore <file>|list|setup-cron|cleanup}"
        echo ""
        echo "  full        - Backup complet (DB + media + S3)"
        echo "  db          - Backup base de données uniquement"
        echo "  media       - Backup fichiers media uniquement"
        echo "  restore     - Restaurer un backup DB"
        echo "  list        - Lister les backups disponibles"
        echo "  setup-cron  - Installer le crontab automatique"
        echo "  cleanup     - Supprimer les anciens backups"
        ;;
esac
