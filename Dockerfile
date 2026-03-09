# Dockerfile pour Haroo Backend (Django)
# TASK-2.1: Containerisation Backend

FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    gdal-bin \
    libgdal-dev \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Créer le répertoire de travail
WORKDIR /app

# Copier les requirements
COPY requirements-no-gdal.txt requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copier le code
COPY . .

# Créer les répertoires nécessaires
RUN mkdir -p /app/staticfiles /app/media /app/logs

# Collecter les fichiers statiques (peut échouer si DB pas prête)
RUN python manage.py collectstatic --noinput || true

# Exposer le port
EXPOSE 8000

# Script d'entrée
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["gunicorn", "haroo.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120"]
