# Dockerfile pour Haroo Frontend (React + Vite)
# TASK-2.2: Containerisation Frontend avec multi-stage build

# Stage 1: Builder
FROM node:20-alpine AS builder

WORKDIR /app

# Copier les fichiers de dépendances
COPY package.json package-lock.json* ./
RUN npm ci

# Copier le code source
COPY . .

# Build de production
RUN npm run build

# Stage 2: Production avec Nginx
FROM nginx:alpine

# Argument pour choisir la config nginx (dev ou prod)
ARG NGINX_CONF=nginx.conf

# Copier la configuration Nginx
COPY ${NGINX_CONF} /etc/nginx/conf.d/default.conf

# Copier les fichiers buildés depuis le stage builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Exposer le port 80
EXPOSE 80

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Démarrer Nginx
CMD ["nginx", "-g", "daemon off;"]
