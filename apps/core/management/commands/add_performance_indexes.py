"""
Commande Django pour ajouter des index de performance

Cette commande génère une migration pour ajouter des index sur les champs
fréquemment utilisés dans les requêtes.

Usage:
    python manage.py add_performance_indexes
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Génère une migration pour ajouter des index de performance'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Analyse des index nécessaires...'))
        
        # Liste des index recommandés
        indexes = [
            # Users
            ('users_user', 'email', 'Index sur email pour recherche rapide'),
            ('users_user', 'phone_number', 'Index sur téléphone pour recherche'),
            ('users_user', 'user_type', 'Index sur type d'utilisateur pour filtrage'),
            ('users_user', 'is_active', 'Index sur statut actif'),
            ('users_user', 'created_at', 'Index sur date de création pour tri'),
            
            # AgronomeProfile
            ('users_agronomeprofile', 'user_id', 'Index sur user_id (ForeignKey)'),
            ('users_agronomeprofile', 'is_validated', 'Index sur validation'),
            ('users_agronomeprofile', 'specialite', 'Index sur spécialité'),
            
            # ExploitantProfile
            ('users_exploitantprofile', 'user_id', 'Index sur user_id (ForeignKey)'),
            ('users_exploitantprofile', 'location_id', 'Index sur location_id (ForeignKey)'),
            ('users_exploitantprofile', 'is_verified', 'Index sur vérification'),
            
            # DocumentJustificatif
            ('users_documentjustificatif', 'user_id', 'Index sur user_id (ForeignKey)'),
            ('users_documentjustificatif', 'type_document', 'Index sur type de document'),
            ('users_documentjustificatif', 'is_validated', 'Index sur validation'),
        ]
        
        self.stdout.write('\nIndex recommandés:')
        self.stdout.write('=' * 80)
        
        for table, column, description in indexes:
            self.stdout.write(f'\n📊 {table}.{column}')
            self.stdout.write(f'   {description}')
            
            # Vérifier si l'index existe déjà
            if self._index_exists(table, column):
                self.stdout.write(self.style.WARNING(f'   ⚠️  Index déjà existant'))
            else:
                self.stdout.write(self.style.SUCCESS(f'   ✅ À créer'))
        
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write('\nPour créer les index, ajoutez dans vos modèles:')
        self.stdout.write('\nclass Meta:')
        self.stdout.write('    indexes = [')
        self.stdout.write('        models.Index(fields=[\'field_name\'], name=\'idx_table_field\'),')
        self.stdout.write('    ]')
        self.stdout.write('\nPuis exécutez: python manage.py makemigrations')
        
    def _index_exists(self, table: str, column: str) -> bool:
        """Vérifie si un index existe déjà"""
        with connection.cursor() as cursor:
            # PostgreSQL
            if connection.vendor == 'postgresql':
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM pg_indexes
                    WHERE tablename = %s
                    AND indexdef LIKE %s
                """, [table, f'%{column}%'])
                return cursor.fetchone()[0] > 0
            
            # SQLite
            elif connection.vendor == 'sqlite':
                cursor.execute(f"PRAGMA index_list({table})")
                indexes = cursor.fetchall()
                for index in indexes:
                    cursor.execute(f"PRAGMA index_info({index[1]})")
                    columns = cursor.fetchall()
                    if any(col[2] == column for col in columns):
                        return True
                return False
            
            return False
