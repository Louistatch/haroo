"""
Commande pour initialiser les politiques de rétention des données
Exigence: 45.6
"""
from django.core.management.base import BaseCommand
from apps.compliance.services import DataRetentionService


class Command(BaseCommand):
    help = 'Initialise les politiques de rétention des données'
    
    def handle(self, *args, **options):
        self.stdout.write('Initialisation des politiques de rétention...')
        
        DataRetentionService.initialize_policies()
        
        self.stdout.write(
            self.style.SUCCESS('Politiques de rétention initialisées avec succès')
        )
