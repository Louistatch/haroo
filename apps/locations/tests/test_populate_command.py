"""
Tests pour la commande de peuplement des données administratives
"""
from django.test import TestCase
from django.core.management import call_command
from apps.locations.models import Region, Prefecture, Canton


class PopulateAdministrativeDataCommandTest(TestCase):
    """Tests pour la commande populate_administrative_data"""
    
    def test_populate_command_creates_regions(self):
        """Vérifie que la commande crée les 5 régions"""
        call_command('populate_administrative_data')
        self.assertEqual(Region.objects.count(), 5)
    
    def test_populate_command_creates_prefectures(self):
        """Vérifie que la commande crée les préfectures"""
        call_command('populate_administrative_data')
        # Devrait créer 38 préfectures (5+9+7+6+8 = 35 + quelques autres)
        self.assertGreaterEqual(Prefecture.objects.count(), 35)
    
    def test_populate_command_creates_cantons(self):
        """Vérifie que la commande crée plus de 300 cantons"""
        call_command('populate_administrative_data')
        self.assertGreaterEqual(Canton.objects.count(), 300)
    
    def test_hierarchical_consistency(self):
        """Vérifie la cohérence hiérarchique des données"""
        call_command('populate_administrative_data')
        
        # Vérifier qu'une région a des préfectures
        region = Region.objects.first()
        self.assertGreater(region.prefectures.count(), 0)
        
        # Vérifier qu'une préfecture a des cantons
        prefecture = Prefecture.objects.first()
        self.assertGreater(prefecture.cantons.count(), 0)
        
        # Vérifier qu'un canton a une préfecture et une région
        canton = Canton.objects.first()
        self.assertIsNotNone(canton.prefecture)
        self.assertIsNotNone(canton.prefecture.region)
    
    def test_cantons_have_gps_coordinates(self):
        """Vérifie que les cantons ont des coordonnées GPS"""
        call_command('populate_administrative_data')
        
        # Vérifier qu'au moins un canton a des coordonnées
        canton_with_coords = Canton.objects.filter(
            coordonnees_centre__isnull=False
        ).first()
        self.assertIsNotNone(canton_with_coords)
        self.assertIsNotNone(canton_with_coords.coordonnees_centre)
    
    def test_command_is_idempotent(self):
        """Vérifie que la commande peut être exécutée plusieurs fois"""
        # Première exécution
        call_command('populate_administrative_data')
        first_count = Canton.objects.count()
        
        # Deuxième exécution
        call_command('populate_administrative_data')
        second_count = Canton.objects.count()
        
        # Le nombre devrait rester le même
        self.assertEqual(first_count, second_count)
    
    def test_clear_option_removes_existing_data(self):
        """Vérifie que l'option --clear supprime les données existantes"""
        # Créer des données
        call_command('populate_administrative_data')
        initial_count = Canton.objects.count()
        self.assertGreater(initial_count, 0)
        
        # Supprimer et recréer
        call_command('populate_administrative_data', clear=True)
        final_count = Canton.objects.count()
        
        # Les données devraient être recréées
        self.assertEqual(initial_count, final_count)
