# Makefile pour Haroo - Simplification des commandes Docker

.PHONY: help build up down logs shell migrate test clean restart

help: ## Afficher l'aide
	@echo "Commandes disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build les images Docker
	docker-compose build

up: ## Démarrer tous les services
	docker-compose up -d

down: ## Arrêter tous les services
	docker-compose down

logs: ## Afficher les logs (usage: make logs SERVICE=backend)
	@if [ -z "$(SERVICE)" ]; then \
		docker-compose logs -f; \
	else \
		docker-compose logs -f $(SERVICE); \
	fi

shell: ## Ouvrir un shell dans le backend
	docker-compose exec backend bash

shell-db: ## Ouvrir un shell PostgreSQL
	docker-compose exec db psql -U haroo_user haroo_db

shell-redis: ## Ouvrir un shell Redis
	docker-compose exec redis redis-cli

migrate: ## Exécuter les migrations
	docker-compose exec backend python manage.py migrate

makemigrations: ## Créer de nouvelles migrations
	docker-compose exec backend python manage.py makemigrations

collectstatic: ## Collecter les fichiers statiques
	docker-compose exec backend python manage.py collectstatic --noinput

createsuperuser: ## Créer un superutilisateur
	docker-compose exec backend python manage.py createsuperuser

test: ## Exécuter les tests
	docker-compose exec backend pytest

test-cov: ## Exécuter les tests avec couverture
	docker-compose exec backend pytest --cov=apps --cov-report=html

lint: ## Vérifier la qualité du code
	docker-compose exec backend flake8 apps/ haroo/
	docker-compose exec backend black --check apps/ haroo/
	docker-compose exec backend isort --check-only apps/ haroo/

format: ## Formater le code
	docker-compose exec backend black apps/ haroo/
	docker-compose exec backend isort apps/ haroo/

restart: ## Redémarrer tous les services
	docker-compose restart

restart-backend: ## Redémarrer le backend
	docker-compose restart backend

restart-frontend: ## Redémarrer le frontend
	docker-compose restart frontend

ps: ## Afficher l'état des services
	docker-compose ps

clean: ## Nettoyer les conteneurs et volumes
	docker-compose down -v
	docker system prune -f

backup-db: ## Backup de la base de données
	docker-compose exec db pg_dump -U haroo_user haroo_db > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore-db: ## Restaurer la base de données (usage: make restore-db FILE=backup.sql)
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make restore-db FILE=backup.sql"; \
	else \
		docker-compose exec -T db psql -U haroo_user haroo_db < $(FILE); \
	fi

dev: ## Démarrer en mode développement
	docker-compose up

prod: ## Démarrer en mode production
	docker-compose --env-file .env.prod up -d

health: ## Vérifier la santé des services
	@echo "Backend health:"
	@curl -f http://localhost:8000/admin/ || echo "Backend DOWN"
	@echo "\nFrontend health:"
	@curl -f http://localhost:5000/ || echo "Frontend DOWN"
	@echo "\nDocker services:"
	@docker-compose ps
