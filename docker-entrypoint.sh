#!/bin/bash
# Script d'entrée Docker pour Haroo Backend
# TASK-2.1: Gestion du démarrage avec migrations

set -e

echo "🚀 Démarrage de Haroo Backend..."

# Attendre que PostgreSQL soit prêt
echo "⏳ Attente de PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "✅ PostgreSQL est prêt!"

# Attendre que Redis soit prêt
echo "⏳ Attente de Redis..."
while ! nc -z ${REDIS_HOST:-redis} 6379; do
  sleep 0.1
done
echo "✅ Redis est prêt!"

# Exécuter les migrations
echo "🔄 Exécution des migrations..."
python manage.py migrate --noinput

# Collecter les fichiers statiques
echo "📦 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

# Créer un superutilisateur si nécessaire (dev ou local_prod avec CREATE_SUPERUSER=true)
if [ "$DJANGO_SETTINGS_MODULE" = "haroo.settings.dev" ] || [ "$CREATE_SUPERUSER" = "true" ]; then
    echo "👤 Création du superutilisateur..."
    python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@haroo.tg', 'changeme123')
    print('✅ Superutilisateur créé: admin / changeme123')
else:
    print('ℹ️  Superutilisateur existe déjà')
END
fi

echo "✅ Initialisation terminée!"
echo "🚀 Démarrage de l'application..."

# Exécuter la commande passée en argument
exec "$@"
