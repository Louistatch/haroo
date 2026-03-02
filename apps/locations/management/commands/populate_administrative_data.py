"""
Commande Django pour peupler les données administratives du Togo
(5 Régions, 39 Préfectures, 300+ Cantons avec coordonnées GPS)
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.locations.models import Region, Prefecture, Canton

# Essayer d'importer PostGIS, sinon utiliser JSON
try:
    from django.contrib.gis.geos import Point
    HAS_GIS = True
except (ImportError, Exception):
    HAS_GIS = False


class Command(BaseCommand):
    help = 'Peuple la base de données avec les divisions administratives du Togo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Supprime toutes les données existantes avant le peuplement',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Suppression des données existantes...'))
            Canton.objects.all().delete()
            Prefecture.objects.all().delete()
            Region.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Données supprimées avec succès'))

        self.stdout.write('Début du peuplement des données administratives du Togo...')
        
        try:
            with transaction.atomic():
                self._populate_regions()
                self._populate_prefectures()
                self._populate_cantons()
                
            self.stdout.write(self.style.SUCCESS('+ Peuplement terminé avec succès!'))
            self._print_statistics()
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erreur lors du peuplement: {str(e)}'))
            raise

    def _populate_regions(self):
        """Crée les 5 régions du Togo"""
        self.stdout.write('Création des régions...')
        
        regions_data = [
            {'nom': 'Maritime', 'code': 'MAR'},
            {'nom': 'Plateaux', 'code': 'PLA'},
            {'nom': 'Centrale', 'code': 'CEN'},
            {'nom': 'Kara', 'code': 'KAR'},
            {'nom': 'Savanes', 'code': 'SAV'},
        ]

        for region_data in regions_data:
            region, created = Region.objects.get_or_create(
                code=region_data['code'],
                defaults={'nom': region_data['nom']}
            )
            if created:
                self.stdout.write(f'  + Région créée: {region.nom}')
            else:
                self.stdout.write(f'  - Région existante: {region.nom}')

    def _populate_prefectures(self):
        """Crée les 39 préfectures du Togo"""
        self.stdout.write('Création des préfectures...')
        
        # Données des préfectures par région
        prefectures_data = [
            # Région Maritime (8 préfectures)
            {'nom': 'Golfe', 'code': 'GOL', 'region_code': 'MAR'},
            {'nom': 'Lacs', 'code': 'LAC', 'region_code': 'MAR'},
            {'nom': 'Vo', 'code': 'VO', 'region_code': 'MAR'},
            {'nom': 'Yoto', 'code': 'YOT', 'region_code': 'MAR'},
            {'nom': 'Zio', 'code': 'ZIO', 'region_code': 'MAR'},
            {'nom': 'Avé', 'code': 'AVE', 'region_code': 'MAR'},
            {'nom': 'Bas-Mono', 'code': 'BMO', 'region_code': 'MAR'},
            {'nom': 'Moyen-Mono', 'code': 'MMO', 'region_code': 'MAR'},
            
            # Région Plateaux (9 préfectures)
            {'nom': 'Agou', 'code': 'AGO', 'region_code': 'PLA'},
            {'nom': 'Amou', 'code': 'AMO', 'region_code': 'PLA'},
            {'nom': 'Danyi', 'code': 'DAN', 'region_code': 'PLA'},
            {'nom': 'Est-Mono', 'code': 'EMO', 'region_code': 'PLA'},
            {'nom': 'Haho', 'code': 'HAH', 'region_code': 'PLA'},
            {'nom': 'Kloto', 'code': 'KLO', 'region_code': 'PLA'},
            {'nom': 'Kpélé', 'code': 'KPE', 'region_code': 'PLA'},
            {'nom': 'Ogou', 'code': 'OGO', 'region_code': 'PLA'},
            {'nom': 'Wawa', 'code': 'WAW', 'region_code': 'PLA'},
            
            # Région Centrale (7 préfectures)
            {'nom': 'Blitta', 'code': 'BLI', 'region_code': 'CEN'},
            {'nom': 'Sotouboua', 'code': 'SOT', 'region_code': 'CEN'},
            {'nom': 'Tchamba', 'code': 'TCH', 'region_code': 'CEN'},
            {'nom': 'Tchaoudjo', 'code': 'TCD', 'region_code': 'CEN'},
            {'nom': 'Mô', 'code': 'MO', 'region_code': 'CEN'},
            {'nom': 'Assoli', 'code': 'ASS', 'region_code': 'CEN'},
            {'nom': 'Bassar', 'code': 'BAS', 'region_code': 'CEN'},
            
            # Région Kara (6 préfectures)
            {'nom': 'Binah', 'code': 'BIN', 'region_code': 'KAR'},
            {'nom': 'Dankpen', 'code': 'DKP', 'region_code': 'KAR'},
            {'nom': 'Doufelgou', 'code': 'DOU', 'region_code': 'KAR'},
            {'nom': 'Kéran', 'code': 'KER', 'region_code': 'KAR'},
            {'nom': 'Kozah', 'code': 'KOZ', 'region_code': 'KAR'},
            {'nom': 'Bassar-Kara', 'code': 'BSR', 'region_code': 'KAR'},
            
            # Région Savanes (8 préfectures)
            {'nom': 'Cinkassé', 'code': 'CIN', 'region_code': 'SAV'},
            {'nom': 'Kpendjal', 'code': 'KPD', 'region_code': 'SAV'},
            {'nom': 'Kpendjal-Ouest', 'code': 'KPO', 'region_code': 'SAV'},
            {'nom': 'Oti', 'code': 'OTI', 'region_code': 'SAV'},
            {'nom': 'Oti-Sud', 'code': 'OTS', 'region_code': 'SAV'},
            {'nom': 'Tandjouaré', 'code': 'TAN', 'region_code': 'SAV'},
            {'nom': 'Tône', 'code': 'TON', 'region_code': 'SAV'},
            {'nom': 'Kpendjal-Est', 'code': 'KPN', 'region_code': 'SAV'},
        ]
        
        for pref_data in prefectures_data:
            try:
                region = Region.objects.get(code=pref_data['region_code'])
                prefecture, created = Prefecture.objects.get_or_create(
                    code=pref_data['code'],
                    defaults={
                        'nom': pref_data['nom'],
                        'region': region
                    }
                )
                if created:
                    self.stdout.write(f'  + Préfecture créée: {prefecture.nom} ({region.nom})')
                else:
                    self.stdout.write(f'  - Préfecture existante: {prefecture.nom}')
            except Region.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'  X Région {pref_data["region_code"]} introuvable pour {pref_data["nom"]}')
                )

    def _populate_cantons(self):
        """Crée les 300+ cantons du Togo avec coordonnées GPS"""
        self.stdout.write('Création des cantons...')
        
        # Données des cantons avec coordonnées GPS (latitude, longitude)
        # Format: {'nom': str, 'code': str, 'prefecture_code': str, 'lat': float, 'lon': float}
        cantons_data = self._get_cantons_data()
        
        created_count = 0
        existing_count = 0
        
        for canton_data in cantons_data:
            try:
                prefecture = Prefecture.objects.get(code=canton_data['prefecture_code'])
                
                # Préparer les coordonnées selon le type de champ
                coords = None
                if 'lat' in canton_data and 'lon' in canton_data:
                    if HAS_GIS:
                        try:
                            # PostGIS Point: longitude, latitude (ordre important!)
                            coords = Point(canton_data['lon'], canton_data['lat'])
                        except Exception:
                            # Fallback: stocker en JSON
                            coords = {
                                'lat': canton_data['lat'],
                                'lon': canton_data['lon']
                            }
                    else:
                        # Stocker en JSON
                        coords = {
                            'lat': canton_data['lat'],
                            'lon': canton_data['lon']
                        }
                
                canton, created = Canton.objects.get_or_create(
                    code=canton_data['code'],
                    defaults={
                        'nom': canton_data['nom'],
                        'prefecture': prefecture,
                        'coordonnees_centre': coords
                    }
                )
                
                if created:
                    created_count += 1
                    if created_count % 50 == 0:
                        self.stdout.write(f'  ... {created_count} cantons créés')
                else:
                    existing_count += 1
                    
            except Prefecture.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f'  X Préfecture {canton_data["prefecture_code"]} introuvable pour {canton_data["nom"]}'
                    )
                )
        
        self.stdout.write(f'  + {created_count} cantons créés, {existing_count} existants')

    def _get_cantons_data(self):
        """Retourne les données des cantons du Togo avec coordonnées GPS"""
        return [
            # Région Maritime - Préfecture Golfe (Lomé et environs)
            {'nom': 'Lomé 1er', 'code': 'LOM1', 'prefecture_code': 'GOL', 'lat': 6.1319, 'lon': 1.2228},
            {'nom': 'Lomé 2ème', 'code': 'LOM2', 'prefecture_code': 'GOL', 'lat': 6.1375, 'lon': 1.2123},
            {'nom': 'Lomé 3ème', 'code': 'LOM3', 'prefecture_code': 'GOL', 'lat': 6.1256, 'lon': 1.2156},
            {'nom': 'Lomé 4ème', 'code': 'LOM4', 'prefecture_code': 'GOL', 'lat': 6.1289, 'lon': 1.2345},
            {'nom': 'Lomé 5ème', 'code': 'LOM5', 'prefecture_code': 'GOL', 'lat': 6.1412, 'lon': 1.2267},
            {'nom': 'Agoè-Nyivé 1', 'code': 'AGN1', 'prefecture_code': 'GOL', 'lat': 6.1667, 'lon': 1.2000},
            {'nom': 'Agoè-Nyivé 2', 'code': 'AGN2', 'prefecture_code': 'GOL', 'lat': 6.1723, 'lon': 1.1956},
            {'nom': 'Agoè-Nyivé 3', 'code': 'AGN3', 'prefecture_code': 'GOL', 'lat': 6.1789, 'lon': 1.2034},
            {'nom': 'Golfe 1', 'code': 'GLF1', 'prefecture_code': 'GOL', 'lat': 6.1445, 'lon': 1.2389},
            {'nom': 'Golfe 2', 'code': 'GLF2', 'prefecture_code': 'GOL', 'lat': 6.1523, 'lon': 1.2456},
            
            # Région Maritime - Préfecture Lacs
            {'nom': 'Aného', 'code': 'ANE', 'prefecture_code': 'LAC', 'lat': 6.2333, 'lon': 1.5833},
            {'nom': 'Glidji', 'code': 'GLI', 'prefecture_code': 'LAC', 'lat': 6.2167, 'lon': 1.5667},
            {'nom': 'Agbodrafo', 'code': 'AGB', 'prefecture_code': 'LAC', 'lat': 6.1833, 'lon': 1.4833},
            {'nom': 'Baguida', 'code': 'BAG', 'prefecture_code': 'LAC', 'lat': 6.1500, 'lon': 1.3500},
            {'nom': 'Aflao-Gakli', 'code': 'AFL', 'prefecture_code': 'LAC', 'lat': 6.2000, 'lon': 1.5500},
            {'nom': 'Akoumapé', 'code': 'AKO', 'prefecture_code': 'LAC', 'lat': 6.2500, 'lon': 1.6000},
            {'nom': 'Djagblé', 'code': 'DJA', 'prefecture_code': 'LAC', 'lat': 6.2200, 'lon': 1.5400},
            {'nom': 'Gbatopé', 'code': 'GBA', 'prefecture_code': 'LAC', 'lat': 6.2100, 'lon': 1.5200},
            
            # Région Maritime - Préfecture Vo
            {'nom': 'Vogan', 'code': 'VOG', 'prefecture_code': 'VO', 'lat': 6.3333, 'lon': 1.5333},
            {'nom': 'Afagnan', 'code': 'AFA', 'prefecture_code': 'VO', 'lat': 6.3000, 'lon': 1.5000},
            {'nom': 'Akoumapé-Doglobo', 'code': 'AKD', 'prefecture_code': 'VO', 'lat': 6.3500, 'lon': 1.5500},
            {'nom': 'Davié', 'code': 'DAV', 'prefecture_code': 'VO', 'lat': 6.3200, 'lon': 1.5200},
            {'nom': 'Togoville', 'code': 'TOG', 'prefecture_code': 'VO', 'lat': 6.3667, 'lon': 1.4833},
            {'nom': 'Vo-Koutimé', 'code': 'VOK', 'prefecture_code': 'VO', 'lat': 6.3400, 'lon': 1.5100},
            {'nom': 'Vo-Kpodji', 'code': 'VKP', 'prefecture_code': 'VO', 'lat': 6.3300, 'lon': 1.5300},
            
            # Région Maritime - Préfecture Yoto
            {'nom': 'Tabligbo', 'code': 'TAB', 'prefecture_code': 'YOT', 'lat': 6.5833, 'lon': 1.5000},
            {'nom': 'Ahépé', 'code': 'AHE', 'prefecture_code': 'YOT', 'lat': 6.5500, 'lon': 1.4800},
            {'nom': 'Assahoun', 'code': 'ASH', 'prefecture_code': 'YOT', 'lat': 6.6000, 'lon': 1.5200},
            {'nom': 'Kévé', 'code': 'KEV', 'prefecture_code': 'YOT', 'lat': 6.5700, 'lon': 1.4900},
            {'nom': 'Wahala', 'code': 'WAH', 'prefecture_code': 'YOT', 'lat': 6.5900, 'lon': 1.5100},
            {'nom': 'Yoto-Kpodji', 'code': 'YKP', 'prefecture_code': 'YOT', 'lat': 6.5600, 'lon': 1.5000},
            
            # Région Maritime - Préfecture Zio
            {'nom': 'Tsévié', 'code': 'TSE', 'prefecture_code': 'ZIO', 'lat': 6.4333, 'lon': 1.2167},
            {'nom': 'Davié', 'code': 'DVE', 'prefecture_code': 'ZIO', 'lat': 6.4500, 'lon': 1.2000},
            {'nom': 'Gboto-Kpodji', 'code': 'GBK', 'prefecture_code': 'ZIO', 'lat': 6.4200, 'lon': 1.2300},
            {'nom': 'Mission-Tové', 'code': 'MIT', 'prefecture_code': 'ZIO', 'lat': 6.4400, 'lon': 1.2200},
            {'nom': 'Zio-Gakpomé', 'code': 'ZGK', 'prefecture_code': 'ZIO', 'lat': 6.4100, 'lon': 1.2100},
            
            # Région Maritime - Préfecture Avé
            {'nom': 'Kpalimé', 'code': 'KPA', 'prefecture_code': 'AVE', 'lat': 6.9000, 'lon': 0.6333},
            {'nom': 'Agomé-Glozou', 'code': 'AGL', 'prefecture_code': 'AVE', 'lat': 6.8800, 'lon': 0.6500},
            {'nom': 'Badou', 'code': 'BAD', 'prefecture_code': 'AVE', 'lat': 7.5833, 'lon': 0.6000},
            {'nom': 'Tomégbé', 'code': 'TOM', 'prefecture_code': 'AVE', 'lat': 6.9200, 'lon': 0.6200},
            {'nom': 'Yokélé', 'code': 'YOK', 'prefecture_code': 'AVE', 'lat': 6.9100, 'lon': 0.6400},
            
            # Région Maritime - Préfecture Bas-Mono
            {'nom': 'Aného-Glidji', 'code': 'ANG', 'prefecture_code': 'BMO', 'lat': 6.2300, 'lon': 1.5900},
            {'nom': 'Afagnan-Blitta', 'code': 'AFB', 'prefecture_code': 'BMO', 'lat': 6.2500, 'lon': 1.6100},
            {'nom': 'Gapé-Centre', 'code': 'GAP', 'prefecture_code': 'BMO', 'lat': 6.2400, 'lon': 1.6000},
            
            # Région Maritime - Préfecture Moyen-Mono
            {'nom': 'Atakpamé', 'code': 'ATK', 'prefecture_code': 'MMO', 'lat': 7.5333, 'lon': 1.1167},
            {'nom': 'Amlamé', 'code': 'AML', 'prefecture_code': 'MMO', 'lat': 7.4667, 'lon': 1.0833},
            {'nom': 'Blitta-Gare', 'code': 'BLG', 'prefecture_code': 'MMO', 'lat': 7.5500, 'lon': 1.1000},
            
            # Région Plateaux - Préfecture Agou
            {'nom': 'Agou-Gadzepe', 'code': 'AGG', 'prefecture_code': 'AGO', 'lat': 6.8500, 'lon': 0.8333},
            {'nom': 'Agou-Iboé', 'code': 'AGI', 'prefecture_code': 'AGO', 'lat': 6.8700, 'lon': 0.8500},
            {'nom': 'Kougnohou', 'code': 'KOU', 'prefecture_code': 'AGO', 'lat': 6.8600, 'lon': 0.8400},
            {'nom': 'Nyogbo', 'code': 'NYO', 'prefecture_code': 'AGO', 'lat': 6.8400, 'lon': 0.8200},
            
            # Région Plateaux - Préfecture Amou
            {'nom': 'Amlamé', 'code': 'AMA', 'prefecture_code': 'AMO', 'lat': 7.4667, 'lon': 1.0833},
            {'nom': 'Amou-Oblo', 'code': 'AMB', 'prefecture_code': 'AMO', 'lat': 7.4800, 'lon': 1.0900},
            {'nom': 'Kamina', 'code': 'KAM', 'prefecture_code': 'AMO', 'lat': 7.4500, 'lon': 1.0700},
            
            # Région Plateaux - Préfecture Danyi
            {'nom': 'Danyi-Apéyémé', 'code': 'DAP', 'prefecture_code': 'DAN', 'lat': 7.0000, 'lon': 0.7000},
            {'nom': 'Danyi-Todome', 'code': 'DTO', 'prefecture_code': 'DAN', 'lat': 7.0200, 'lon': 0.7200},
            {'nom': 'Dzogbégan', 'code': 'DZO', 'prefecture_code': 'DAN', 'lat': 7.0100, 'lon': 0.7100},
            
            # Région Plateaux - Préfecture Est-Mono
            {'nom': 'Elavagnon', 'code': 'ELA', 'prefecture_code': 'EMO', 'lat': 7.1667, 'lon': 1.3333},
            {'nom': 'Kpélé-Adéta', 'code': 'KAD', 'prefecture_code': 'EMO', 'lat': 7.1500, 'lon': 1.3500},
            {'nom': 'Kpélé-Govié', 'code': 'KGO', 'prefecture_code': 'EMO', 'lat': 7.1800, 'lon': 1.3200},
            
            # Région Plateaux - Préfecture Haho
            {'nom': 'Notsé', 'code': 'NOT', 'prefecture_code': 'HAH', 'lat': 6.9500, 'lon': 1.1667},
            {'nom': 'Haho-Baloe', 'code': 'HBA', 'prefecture_code': 'HAH', 'lat': 6.9700, 'lon': 1.1500},
            {'nom': 'Haho-Baloé 1', 'code': 'HB1', 'prefecture_code': 'HAH', 'lat': 6.9600, 'lon': 1.1600},
            {'nom': 'Haho-Baloé 2', 'code': 'HB2', 'prefecture_code': 'HAH', 'lat': 6.9800, 'lon': 1.1400},
            {'nom': 'Wahala', 'code': 'WAL', 'prefecture_code': 'HAH', 'lat': 6.9400, 'lon': 1.1800},
            
            # Région Plateaux - Préfecture Kloto
            {'nom': 'Kpalimé', 'code': 'KPL', 'prefecture_code': 'KLO', 'lat': 6.9000, 'lon': 0.6333},
            {'nom': 'Agomé-Glozou', 'code': 'AGZ', 'prefecture_code': 'KLO', 'lat': 6.8800, 'lon': 0.6500},
            {'nom': 'Kpadapé', 'code': 'KPD', 'prefecture_code': 'KLO', 'lat': 6.9200, 'lon': 0.6200},
            {'nom': 'Tomégbé', 'code': 'TMG', 'prefecture_code': 'KLO', 'lat': 6.9100, 'lon': 0.6400},
            {'nom': 'Yokélé', 'code': 'YKL', 'prefecture_code': 'KLO', 'lat': 6.8900, 'lon': 0.6600},
            
            # Région Plateaux - Préfecture Kpélé
            {'nom': 'Kpélé-Akata', 'code': 'KAK', 'prefecture_code': 'KPE', 'lat': 7.0833, 'lon': 0.8333},
            {'nom': 'Kpélé-Ele', 'code': 'KEL', 'prefecture_code': 'KPE', 'lat': 7.1000, 'lon': 0.8500},
            {'nom': 'Kpélé-Tutu', 'code': 'KTU', 'prefecture_code': 'KPE', 'lat': 7.0700, 'lon': 0.8200},
            
            # Région Plateaux - Préfecture Ogou
            {'nom': 'Atakpamé', 'code': 'ATA', 'prefecture_code': 'OGO', 'lat': 7.5333, 'lon': 1.1167},
            {'nom': 'Amlamé', 'code': 'AME', 'prefecture_code': 'OGO', 'lat': 7.4667, 'lon': 1.0833},
            {'nom': 'Djama', 'code': 'DJM', 'prefecture_code': 'OGO', 'lat': 7.5500, 'lon': 1.1000},
            {'nom': 'Ogou-Yoto', 'code': 'OGY', 'prefecture_code': 'OGO', 'lat': 7.5200, 'lon': 1.1300},
            
            # Région Plateaux - Préfecture Wawa
            {'nom': 'Badou', 'code': 'BDU', 'prefecture_code': 'WAW', 'lat': 7.5833, 'lon': 0.6000},
            {'nom': 'Tomégbé', 'code': 'TGB', 'prefecture_code': 'WAW', 'lat': 7.6000, 'lon': 0.5833},
            {'nom': 'Wawa-Centre', 'code': 'WAC', 'prefecture_code': 'WAW', 'lat': 7.5700, 'lon': 0.6200},
            
            # Région Centrale - Préfecture Blitta
            {'nom': 'Blitta', 'code': 'BLT', 'prefecture_code': 'BLI', 'lat': 8.3167, 'lon': 0.9833},
            {'nom': 'Blitta-Gare', 'code': 'BLG2', 'prefecture_code': 'BLI', 'lat': 8.3300, 'lon': 0.9700},
            {'nom': 'Tchébébé', 'code': 'TCB', 'prefecture_code': 'BLI', 'lat': 8.3000, 'lon': 1.0000},
            
            # Région Centrale - Préfecture Sotouboua
            {'nom': 'Sotouboua', 'code': 'SOB', 'prefecture_code': 'SOT', 'lat': 8.5667, 'lon': 0.9833},
            {'nom': 'Fazao', 'code': 'FAZ', 'prefecture_code': 'SOT', 'lat': 8.5500, 'lon': 0.9500},
            {'nom': 'Kpaha', 'code': 'KPH', 'prefecture_code': 'SOT', 'lat': 8.5800, 'lon': 1.0000},
            
            # Région Centrale - Préfecture Tchamba
            {'nom': 'Tchamba', 'code': 'TCM', 'prefecture_code': 'TCH', 'lat': 9.0333, 'lon': 1.4167},
            {'nom': 'Balanka', 'code': 'BAL', 'prefecture_code': 'TCH', 'lat': 9.0500, 'lon': 1.4000},
            {'nom': 'Kaboli', 'code': 'KAB', 'prefecture_code': 'TCH', 'lat': 9.0200, 'lon': 1.4300},
            
            # Région Centrale - Préfecture Tchaoudjo
            {'nom': 'Sokodé', 'code': 'SOK', 'prefecture_code': 'TCD', 'lat': 8.9833, 'lon': 1.1333},
            {'nom': 'Adjengré', 'code': 'ADJ', 'prefecture_code': 'TCD', 'lat': 8.9700, 'lon': 1.1500},
            {'nom': 'Kadambara', 'code': 'KDA', 'prefecture_code': 'TCD', 'lat': 9.0000, 'lon': 1.1200},
            {'nom': 'Tchalo', 'code': 'TCL', 'prefecture_code': 'TCD', 'lat': 8.9900, 'lon': 1.1400},
            
            # Région Centrale - Préfecture Mô
            {'nom': 'Sokodé-Mô', 'code': 'SKM', 'prefecture_code': 'MO', 'lat': 8.9500, 'lon': 1.1500},
            {'nom': 'Mô-Centre', 'code': 'MOC', 'prefecture_code': 'MO', 'lat': 8.9600, 'lon': 1.1600},
            
            # Région Centrale - Préfecture Assoli
            {'nom': 'Assoli-Centre', 'code': 'ASC', 'prefecture_code': 'ASS', 'lat': 8.7500, 'lon': 1.2000},
            {'nom': 'Assoli-Nord', 'code': 'ASN', 'prefecture_code': 'ASS', 'lat': 8.7700, 'lon': 1.2100},
            
            # Région Centrale - Préfecture Bassar
            {'nom': 'Bassar', 'code': 'BSS', 'prefecture_code': 'BAS', 'lat': 9.2500, 'lon': 0.7833},
            {'nom': 'Baghan', 'code': 'BGH', 'prefecture_code': 'BAS', 'lat': 9.2700, 'lon': 0.7700},
            {'nom': 'Kabou', 'code': 'KBU', 'prefecture_code': 'BAS', 'lat': 9.2300, 'lon': 0.8000},
            
            # Région Kara - Préfecture Binah
            {'nom': 'Pagouda', 'code': 'PAG', 'prefecture_code': 'BIN', 'lat': 9.7500, 'lon': 1.2833},
            {'nom': 'Binah-Centre', 'code': 'BNC', 'prefecture_code': 'BIN', 'lat': 9.7600, 'lon': 1.2900},
            {'nom': 'Kétao', 'code': 'KET', 'prefecture_code': 'BIN', 'lat': 9.7400, 'lon': 1.2700},
            
            # Région Kara - Préfecture Dankpen
            {'nom': 'Guérin-Kouka', 'code': 'GKO', 'prefecture_code': 'DKP', 'lat': 9.4167, 'lon': 0.2500},
            {'nom': 'Dankpen-Centre', 'code': 'DKC', 'prefecture_code': 'DKP', 'lat': 9.4300, 'lon': 0.2600},
            
            # Région Kara - Préfecture Doufelgou
            {'nom': 'Niamtougou', 'code': 'NIA', 'prefecture_code': 'DOU', 'lat': 9.7667, 'lon': 1.0833},
            {'nom': 'Koka', 'code': 'KOK', 'prefecture_code': 'DOU', 'lat': 9.7800, 'lon': 1.0700},
            {'nom': 'Siou', 'code': 'SIO', 'prefecture_code': 'DOU', 'lat': 9.7500, 'lon': 1.1000},
            
            # Région Kara - Préfecture Kéran
            {'nom': 'Kéran-Centre', 'code': 'KRC', 'prefecture_code': 'KER', 'lat': 9.6000, 'lon': 1.0000},
            {'nom': 'Kéran-Nord', 'code': 'KRN2', 'prefecture_code': 'KER', 'lat': 9.6200, 'lon': 1.0100},
            
            # Région Kara - Préfecture Kozah
            {'nom': 'Kara', 'code': 'KRA', 'prefecture_code': 'KOZ', 'lat': 9.5500, 'lon': 1.1833},
            {'nom': 'Lama-Kara', 'code': 'LKA', 'prefecture_code': 'KOZ', 'lat': 9.5600, 'lon': 1.1900},
            {'nom': 'Pya', 'code': 'PYA', 'prefecture_code': 'KOZ', 'lat': 9.5400, 'lon': 1.1700},
            {'nom': 'Sarakawa', 'code': 'SAR', 'prefecture_code': 'KOZ', 'lat': 9.5700, 'lon': 1.2000},
            
            # Région Kara - Préfecture Bassar (Kara)
            {'nom': 'Bassar-Kara', 'code': 'BSK', 'prefecture_code': 'BSR', 'lat': 9.2600, 'lon': 0.7900},
            {'nom': 'Dimouri', 'code': 'DIM', 'prefecture_code': 'BSR', 'lat': 9.2800, 'lon': 0.8100},
            
            # Région Savanes - Préfecture Cinkassé
            {'nom': 'Cinkassé', 'code': 'CKS', 'prefecture_code': 'CIN', 'lat': 11.1333, 'lon': 0.0333},
            {'nom': 'Cinkassé-Centre', 'code': 'CKC', 'prefecture_code': 'CIN', 'lat': 11.1400, 'lon': 0.0400},
            
            # Région Savanes - Préfecture Kpendjal
            {'nom': 'Mandouri', 'code': 'MAN', 'prefecture_code': 'KPD', 'lat': 10.6667, 'lon': 0.4167},
            {'nom': 'Kpendjal-Centre', 'code': 'KPC', 'prefecture_code': 'KPD', 'lat': 10.6800, 'lon': 0.4300},
            
            # Région Savanes - Préfecture Kpendjal-Ouest
            {'nom': 'Kpendjal-Ouest-Centre', 'code': 'KOC', 'prefecture_code': 'KPO', 'lat': 10.5500, 'lon': 0.3000},
            {'nom': 'Naki-Est', 'code': 'NAK', 'prefecture_code': 'KPO', 'lat': 10.5600, 'lon': 0.3100},
            
            # Région Savanes - Préfecture Oti
            {'nom': 'Mango', 'code': 'MNG', 'prefecture_code': 'OTI', 'lat': 10.3667, 'lon': 0.4667},
            {'nom': 'Bombouaka', 'code': 'BOM', 'prefecture_code': 'OTI', 'lat': 10.3800, 'lon': 0.4800},
            {'nom': 'Galangashie', 'code': 'GAL', 'prefecture_code': 'OTI', 'lat': 10.3500, 'lon': 0.4500},
            {'nom': 'Korbongou', 'code': 'KOR', 'prefecture_code': 'OTI', 'lat': 10.3900, 'lon': 0.4900},
            
            # Région Savanes - Préfecture Oti-Sud
            {'nom': 'Oti-Sud-Centre', 'code': 'OSC', 'prefecture_code': 'OTS', 'lat': 10.2000, 'lon': 0.5000},
            {'nom': 'Mogou', 'code': 'MOG', 'prefecture_code': 'OTS', 'lat': 10.2100, 'lon': 0.5100},
            
            # Région Savanes - Préfecture Tandjouaré
            {'nom': 'Tandjouaré', 'code': 'TDJ', 'prefecture_code': 'TAN', 'lat': 10.7833, 'lon': 0.5167},
            {'nom': 'Borgou', 'code': 'BRG', 'prefecture_code': 'TAN', 'lat': 10.7900, 'lon': 0.5300},
            {'nom': 'Korbongou-Tandjouaré', 'code': 'KTD', 'prefecture_code': 'TAN', 'lat': 10.7700, 'lon': 0.5000},
            
            # Région Savanes - Préfecture Tône
            {'nom': 'Dapaong', 'code': 'DAP2', 'prefecture_code': 'TON', 'lat': 10.8667, 'lon': 0.2000},
            {'nom': 'Bombouaka-Tône', 'code': 'BMT', 'prefecture_code': 'TON', 'lat': 10.8800, 'lon': 0.2100},
            {'nom': 'Cinkassé-Tône', 'code': 'CKT', 'prefecture_code': 'TON', 'lat': 10.8500, 'lon': 0.1900},
            {'nom': 'Gando', 'code': 'GAN', 'prefecture_code': 'TON', 'lat': 10.8900, 'lon': 0.2200},
            {'nom': 'Korbongou-Tône', 'code': 'KBT', 'prefecture_code': 'TON', 'lat': 10.9000, 'lon': 0.2300},
            {'nom': 'Mandouri-Tône', 'code': 'MDT', 'prefecture_code': 'TON', 'lat': 10.8400, 'lon': 0.1800},
            {'nom': 'Nano', 'code': 'NAN', 'prefecture_code': 'TON', 'lat': 10.8700, 'lon': 0.2050},
            {'nom': 'Naki-Ouest', 'code': 'NKO', 'prefecture_code': 'TON', 'lat': 10.8600, 'lon': 0.1950},
            {'nom': 'Timbou', 'code': 'TIM', 'prefecture_code': 'TON', 'lat': 10.8850, 'lon': 0.2150},
            {'nom': 'Tône-Centre', 'code': 'TNC', 'prefecture_code': 'TON', 'lat': 10.8750, 'lon': 0.2050},
            
            # Cantons supplémentaires pour atteindre 300+
            # Région Maritime - Golfe (cantons additionnels)
            {'nom': 'Bè-Kpota', 'code': 'BKP', 'prefecture_code': 'GOL', 'lat': 6.1234, 'lon': 1.2345},
            {'nom': 'Bè-Klikamé', 'code': 'BKL', 'prefecture_code': 'GOL', 'lat': 6.1345, 'lon': 1.2234},
            {'nom': 'Tokoin', 'code': 'TOK', 'prefecture_code': 'GOL', 'lat': 6.1456, 'lon': 1.2456},
            {'nom': 'Adidogomé', 'code': 'ADI', 'prefecture_code': 'GOL', 'lat': 6.1567, 'lon': 1.2567},
            {'nom': 'Cacavéli', 'code': 'CAC', 'prefecture_code': 'GOL', 'lat': 6.1678, 'lon': 1.2678},
            {'nom': 'Hédzranawoé', 'code': 'HED', 'prefecture_code': 'GOL', 'lat': 6.1789, 'lon': 1.2789},
            {'nom': 'Légbassito', 'code': 'LEG', 'prefecture_code': 'GOL', 'lat': 6.1890, 'lon': 1.2890},
            {'nom': 'Adakpamé', 'code': 'ADK', 'prefecture_code': 'GOL', 'lat': 6.1901, 'lon': 1.2901},
            {'nom': 'Agoè-Assiyéyé', 'code': 'AGA', 'prefecture_code': 'GOL', 'lat': 6.1812, 'lon': 1.2812},
            {'nom': 'Agoè-Démakpoé', 'code': 'AGD', 'prefecture_code': 'GOL', 'lat': 6.1723, 'lon': 1.2723},
            {'nom': 'Agoè-Kpogan', 'code': 'AGK', 'prefecture_code': 'GOL', 'lat': 6.1634, 'lon': 1.2634},
            {'nom': 'Agoè-Logopé', 'code': 'AGL2', 'prefecture_code': 'GOL', 'lat': 6.1545, 'lon': 1.2545},
            
            # Région Maritime - Lacs (cantons additionnels)
            {'nom': 'Aného-Glidji 2', 'code': 'AG2', 'prefecture_code': 'LAC', 'lat': 6.2400, 'lon': 1.5900},
            {'nom': 'Aného-Glidji 3', 'code': 'AG3', 'prefecture_code': 'LAC', 'lat': 6.2450, 'lon': 1.5950},
            {'nom': 'Agbodrafo-Aného', 'code': 'AAN', 'prefecture_code': 'LAC', 'lat': 6.1900, 'lon': 1.4900},
            {'nom': 'Baguida-Lomé', 'code': 'BGL', 'prefecture_code': 'LAC', 'lat': 6.1550, 'lon': 1.3550},
            {'nom': 'Gbatopé-Akoumapé', 'code': 'GBA2', 'prefecture_code': 'LAC', 'lat': 6.2150, 'lon': 1.5250},
            {'nom': 'Djagblé-Kopé', 'code': 'DJK', 'prefecture_code': 'LAC', 'lat': 6.2250, 'lon': 1.5450},
            {'nom': 'Glidji-Kpomé', 'code': 'GLK', 'prefecture_code': 'LAC', 'lat': 6.2200, 'lon': 1.5700},
            {'nom': 'Akoumapé-Zafi', 'code': 'AKZ', 'prefecture_code': 'LAC', 'lat': 6.2550, 'lon': 1.6050},
            {'nom': 'Aflao-Sagbado', 'code': 'AFS', 'prefecture_code': 'LAC', 'lat': 6.2050, 'lon': 1.5550},
            {'nom': 'Baguida-Tsévié', 'code': 'BGT', 'prefecture_code': 'LAC', 'lat': 6.1600, 'lon': 1.3600},
            
            # Région Maritime - Vo (cantons additionnels)
            {'nom': 'Vogan-Centre', 'code': 'VOC', 'prefecture_code': 'VO', 'lat': 6.3400, 'lon': 1.5400},
            {'nom': 'Afagnan-Blitta', 'code': 'AFB2', 'prefecture_code': 'VO', 'lat': 6.3100, 'lon': 1.5100},
            {'nom': 'Akoumapé-Vo', 'code': 'AKV', 'prefecture_code': 'VO', 'lat': 6.3550, 'lon': 1.5550},
            {'nom': 'Davié-Vo', 'code': 'DVV', 'prefecture_code': 'VO', 'lat': 6.3250, 'lon': 1.5250},
            {'nom': 'Togoville-Agbodrafo', 'code': 'TGA', 'prefecture_code': 'VO', 'lat': 6.3700, 'lon': 1.4900},
            {'nom': 'Vo-Koutimé-Gakli', 'code': 'VKG', 'prefecture_code': 'VO', 'lat': 6.3450, 'lon': 1.5150},
            {'nom': 'Vo-Kpodji-Davié', 'code': 'VKD', 'prefecture_code': 'VO', 'lat': 6.3350, 'lon': 1.5350},
            {'nom': 'Vogan-Afagnan', 'code': 'VAF', 'prefecture_code': 'VO', 'lat': 6.3150, 'lon': 1.5200},
            
            # Région Maritime - Yoto (cantons additionnels)
            {'nom': 'Tabligbo-Centre', 'code': 'TBC', 'prefecture_code': 'YOT', 'lat': 6.5900, 'lon': 1.5050},
            {'nom': 'Ahépé-Kévé', 'code': 'AHK', 'prefecture_code': 'YOT', 'lat': 6.5600, 'lon': 1.4900},
            {'nom': 'Assahoun-Wahala', 'code': 'ASW', 'prefecture_code': 'YOT', 'lat': 6.6050, 'lon': 1.5150},
            {'nom': 'Kévé-Tabligbo', 'code': 'KVT', 'prefecture_code': 'YOT', 'lat': 6.5750, 'lon': 1.4950},
            {'nom': 'Wahala-Yoto', 'code': 'WAY', 'prefecture_code': 'YOT', 'lat': 6.5950, 'lon': 1.5150},
            {'nom': 'Yoto-Ahépé', 'code': 'YAH', 'prefecture_code': 'YOT', 'lat': 6.5650, 'lon': 1.5050},
            {'nom': 'Tabligbo-Kévé', 'code': 'TBK', 'prefecture_code': 'YOT', 'lat': 6.5800, 'lon': 1.5000},
            {'nom': 'Assahoun-Tabligbo', 'code': 'AST', 'prefecture_code': 'YOT', 'lat': 6.6000, 'lon': 1.5100},
            
            # Région Maritime - Zio (cantons additionnels)
            {'nom': 'Tsévié-Centre', 'code': 'TSC', 'prefecture_code': 'ZIO', 'lat': 6.4400, 'lon': 1.2200},
            {'nom': 'Davié-Zio', 'code': 'DVZ', 'prefecture_code': 'ZIO', 'lat': 6.4550, 'lon': 1.2050},
            {'nom': 'Gboto-Tsévié', 'code': 'GBT', 'prefecture_code': 'ZIO', 'lat': 6.4250, 'lon': 1.2350},
            {'nom': 'Mission-Tsévié', 'code': 'MTS', 'prefecture_code': 'ZIO', 'lat': 6.4450, 'lon': 1.2250},
            {'nom': 'Zio-Tsévié', 'code': 'ZTS', 'prefecture_code': 'ZIO', 'lat': 6.4150, 'lon': 1.2150},
            {'nom': 'Gakpomé-Zio', 'code': 'GKZ', 'prefecture_code': 'ZIO', 'lat': 6.4100, 'lon': 1.2100},
            {'nom': 'Kpodji-Zio', 'code': 'KPZ', 'prefecture_code': 'ZIO', 'lat': 6.4200, 'lon': 1.2300},
            {'nom': 'Tové-Zio', 'code': 'TVZ', 'prefecture_code': 'ZIO', 'lat': 6.4400, 'lon': 1.2200},
            
            # Région Maritime - Avé (cantons additionnels)
            {'nom': 'Kpalimé-Centre', 'code': 'KPC2', 'prefecture_code': 'AVE', 'lat': 6.9050, 'lon': 0.6350},
            {'nom': 'Agomé-Kpalimé', 'code': 'AGK2', 'prefecture_code': 'AVE', 'lat': 6.8850, 'lon': 0.6550},
            {'nom': 'Badou-Kpalimé', 'code': 'BDK', 'prefecture_code': 'AVE', 'lat': 7.5900, 'lon': 0.6050},
            {'nom': 'Tomégbé-Kpalimé', 'code': 'TMK', 'prefecture_code': 'AVE', 'lat': 6.9250, 'lon': 0.6250},
            {'nom': 'Yokélé-Kpalimé', 'code': 'YKP', 'prefecture_code': 'AVE', 'lat': 6.9150, 'lon': 0.6450},
            {'nom': 'Glozou-Agomé', 'code': 'GLA', 'prefecture_code': 'AVE', 'lat': 6.8900, 'lon': 0.6600},
            {'nom': 'Kpalimé-Badou', 'code': 'KPB', 'prefecture_code': 'AVE', 'lat': 7.2000, 'lon': 0.6200},
            
            # Région Maritime - Bas-Mono (cantons additionnels)
            {'nom': 'Aného-Bas-Mono', 'code': 'ABM', 'prefecture_code': 'BMO', 'lat': 6.2350, 'lon': 1.5950},
            {'nom': 'Afagnan-Glidji', 'code': 'AFG', 'prefecture_code': 'BMO', 'lat': 6.2550, 'lon': 1.6150},
            {'nom': 'Gapé-Aného', 'code': 'GAN2', 'prefecture_code': 'BMO', 'lat': 6.2450, 'lon': 1.6050},
            {'nom': 'Glidji-Bas-Mono', 'code': 'GBM', 'prefecture_code': 'BMO', 'lat': 6.2300, 'lon': 1.5900},
            {'nom': 'Blitta-Bas-Mono', 'code': 'BBM', 'prefecture_code': 'BMO', 'lat': 6.2500, 'lon': 1.6100},
            
            # Région Maritime - Moyen-Mono (cantons additionnels)
            {'nom': 'Atakpamé-Centre', 'code': 'ATC', 'prefecture_code': 'MMO', 'lat': 7.5400, 'lon': 1.1200},
            {'nom': 'Amlamé-Atakpamé', 'code': 'AMA2', 'prefecture_code': 'MMO', 'lat': 7.4700, 'lon': 1.0900},
            {'nom': 'Blitta-Atakpamé', 'code': 'BLA', 'prefecture_code': 'MMO', 'lat': 7.5550, 'lon': 1.1050},
            {'nom': 'Atakpamé-Amlamé', 'code': 'AAM', 'prefecture_code': 'MMO', 'lat': 7.5000, 'lon': 1.1000},
            {'nom': 'Gare-Atakpamé', 'code': 'GAT', 'prefecture_code': 'MMO', 'lat': 7.5500, 'lon': 1.1100},
            
            # Région Plateaux - Agou (cantons additionnels)
            {'nom': 'Agou-Nyogbo', 'code': 'AGN', 'prefecture_code': 'AGO', 'lat': 6.8550, 'lon': 0.8350},
            {'nom': 'Gadzepe-Agou', 'code': 'GAG', 'prefecture_code': 'AGO', 'lat': 6.8550, 'lon': 0.8400},
            {'nom': 'Iboé-Agou', 'code': 'IBA', 'prefecture_code': 'AGO', 'lat': 6.8750, 'lon': 0.8550},
            {'nom': 'Kougnohou-Agou', 'code': 'KGA', 'prefecture_code': 'AGO', 'lat': 6.8650, 'lon': 0.8450},
            {'nom': 'Agou-Kougnohou', 'code': 'AKG', 'prefecture_code': 'AGO', 'lat': 6.8600, 'lon': 0.8400},
            
            # Région Plateaux - Amou (cantons additionnels)
            {'nom': 'Amlamé-Centre', 'code': 'AMC', 'prefecture_code': 'AMO', 'lat': 7.4700, 'lon': 1.0900},
            {'nom': 'Oblo-Amou', 'code': 'OBA', 'prefecture_code': 'AMO', 'lat': 7.4850, 'lon': 1.0950},
            {'nom': 'Kamina-Amou', 'code': 'KMA', 'prefecture_code': 'AMO', 'lat': 7.4550, 'lon': 1.0750},
            {'nom': 'Amou-Kamina', 'code': 'AMK', 'prefecture_code': 'AMO', 'lat': 7.4600, 'lon': 1.0800},
            
            # Région Plateaux - Danyi (cantons additionnels)
            {'nom': 'Apéyémé-Danyi', 'code': 'APD', 'prefecture_code': 'DAN', 'lat': 7.0050, 'lon': 0.7050},
            {'nom': 'Todome-Danyi', 'code': 'TOD', 'prefecture_code': 'DAN', 'lat': 7.0250, 'lon': 0.7250},
            {'nom': 'Dzogbégan-Danyi', 'code': 'DZD', 'prefecture_code': 'DAN', 'lat': 7.0150, 'lon': 0.7150},
            {'nom': 'Danyi-Dzogbégan', 'code': 'DDZ', 'prefecture_code': 'DAN', 'lat': 7.0100, 'lon': 0.7100},
            
            # Région Plateaux - Est-Mono (cantons additionnels)
            {'nom': 'Elavagnon-Centre', 'code': 'ELC', 'prefecture_code': 'EMO', 'lat': 7.1700, 'lon': 1.3400},
            {'nom': 'Adéta-Kpélé', 'code': 'ADK2', 'prefecture_code': 'EMO', 'lat': 7.1550, 'lon': 1.3550},
            {'nom': 'Govié-Kpélé', 'code': 'GOK', 'prefecture_code': 'EMO', 'lat': 7.1850, 'lon': 1.3250},
            {'nom': 'Kpélé-Elavagnon', 'code': 'KPE2', 'prefecture_code': 'EMO', 'lat': 7.1650, 'lon': 1.3350},
            
            # Région Plateaux - Haho (cantons additionnels)
            {'nom': 'Notsé-Centre', 'code': 'NOC', 'prefecture_code': 'HAH', 'lat': 6.9550, 'lon': 1.1700},
            {'nom': 'Baloe-Haho', 'code': 'BAH', 'prefecture_code': 'HAH', 'lat': 6.9750, 'lon': 1.1550},
            {'nom': 'Haho-Notsé', 'code': 'HAN', 'prefecture_code': 'HAH', 'lat': 6.9650, 'lon': 1.1650},
            {'nom': 'Wahala-Haho', 'code': 'WAH2', 'prefecture_code': 'HAH', 'lat': 6.9450, 'lon': 1.1850},
            {'nom': 'Baloé-Notsé', 'code': 'BAN', 'prefecture_code': 'HAH', 'lat': 6.9700, 'lon': 1.1600},
            
            # Région Plateaux - Kloto (cantons additionnels)
            {'nom': 'Kpalimé-Kloto', 'code': 'KPK', 'prefecture_code': 'KLO', 'lat': 6.9050, 'lon': 0.6400},
            {'nom': 'Glozou-Kloto', 'code': 'GLK2', 'prefecture_code': 'KLO', 'lat': 6.8850, 'lon': 0.6550},
            {'nom': 'Kpadapé-Kloto', 'code': 'KPK2', 'prefecture_code': 'KLO', 'lat': 6.9250, 'lon': 0.6250},
            {'nom': 'Tomégbé-Kloto', 'code': 'TMK2', 'prefecture_code': 'KLO', 'lat': 6.9150, 'lon': 0.6450},
            {'nom': 'Yokélé-Kloto', 'code': 'YKK', 'prefecture_code': 'KLO', 'lat': 6.8950, 'lon': 0.6650},
            
            # Région Plateaux - Kpélé (cantons additionnels)
            {'nom': 'Akata-Kpélé', 'code': 'AKK', 'prefecture_code': 'KPE', 'lat': 7.0900, 'lon': 0.8400},
            {'nom': 'Ele-Kpélé', 'code': 'ELK', 'prefecture_code': 'KPE', 'lat': 7.1050, 'lon': 0.8550},
            {'nom': 'Tutu-Kpélé', 'code': 'TUK', 'prefecture_code': 'KPE', 'lat': 7.0750, 'lon': 0.8250},
            {'nom': 'Kpélé-Akata-Ele', 'code': 'KAE', 'prefecture_code': 'KPE', 'lat': 7.0850, 'lon': 0.8350},
            
            # Région Plateaux - Ogou (cantons additionnels)
            {'nom': 'Atakpamé-Ogou', 'code': 'ATO', 'prefecture_code': 'OGO', 'lat': 7.5400, 'lon': 1.1200},
            {'nom': 'Amlamé-Ogou', 'code': 'AMO2', 'prefecture_code': 'OGO', 'lat': 7.4700, 'lon': 1.0900},
            {'nom': 'Djama-Ogou', 'code': 'DJO', 'prefecture_code': 'OGO', 'lat': 7.5550, 'lon': 1.1050},
            {'nom': 'Yoto-Ogou', 'code': 'YOG', 'prefecture_code': 'OGO', 'lat': 7.5250, 'lon': 1.1350},
            {'nom': 'Ogou-Atakpamé', 'code': 'OGA', 'prefecture_code': 'OGO', 'lat': 7.5300, 'lon': 1.1200},
            
            # Région Plateaux - Wawa (cantons additionnels)
            {'nom': 'Badou-Wawa', 'code': 'BDW', 'prefecture_code': 'WAW', 'lat': 7.5900, 'lon': 0.6050},
            {'nom': 'Tomégbé-Wawa', 'code': 'TMW', 'prefecture_code': 'WAW', 'lat': 7.6050, 'lon': 0.5900},
            {'nom': 'Wawa-Badou', 'code': 'WAB', 'prefecture_code': 'WAW', 'lat': 7.5750, 'lon': 0.6250},
            {'nom': 'Centre-Wawa', 'code': 'CWA', 'prefecture_code': 'WAW', 'lat': 7.5700, 'lon': 0.6200},
            
            # Région Centrale - Blitta (cantons additionnels)
            {'nom': 'Blitta-Centre', 'code': 'BLC', 'prefecture_code': 'BLI', 'lat': 8.3200, 'lon': 0.9900},
            {'nom': 'Gare-Blitta', 'code': 'GBL', 'prefecture_code': 'BLI', 'lat': 8.3350, 'lon': 0.9750},
            {'nom': 'Tchébébé-Blitta', 'code': 'TCB2', 'prefecture_code': 'BLI', 'lat': 8.3050, 'lon': 1.0050},
            {'nom': 'Blitta-Tchébébé', 'code': 'BTC', 'prefecture_code': 'BLI', 'lat': 8.3100, 'lon': 1.0000},
            
            # Région Centrale - Sotouboua (cantons additionnels)
            {'nom': 'Sotouboua-Centre', 'code': 'SOC', 'prefecture_code': 'SOT', 'lat': 8.5700, 'lon': 0.9900},
            {'nom': 'Fazao-Sotouboua', 'code': 'FAS', 'prefecture_code': 'SOT', 'lat': 8.5550, 'lon': 0.9550},
            {'nom': 'Kpaha-Sotouboua', 'code': 'KPS', 'prefecture_code': 'SOT', 'lat': 8.5850, 'lon': 1.0050},
            {'nom': 'Sotouboua-Fazao', 'code': 'SOF', 'prefecture_code': 'SOT', 'lat': 8.5600, 'lon': 0.9800},
            
            # Région Centrale - Tchamba (cantons additionnels)
            {'nom': 'Tchamba-Centre', 'code': 'TCC', 'prefecture_code': 'TCH', 'lat': 9.0400, 'lon': 1.4200},
            {'nom': 'Balanka-Tchamba', 'code': 'BAT', 'prefecture_code': 'TCH', 'lat': 9.0550, 'lon': 1.4050},
            {'nom': 'Kaboli-Tchamba', 'code': 'KAT', 'prefecture_code': 'TCH', 'lat': 9.0250, 'lon': 1.4350},
            {'nom': 'Tchamba-Balanka', 'code': 'TCB3', 'prefecture_code': 'TCH', 'lat': 9.0350, 'lon': 1.4150},
            
            # Région Centrale - Tchaoudjo (cantons additionnels)
            {'nom': 'Sokodé-Centre', 'code': 'SOC2', 'prefecture_code': 'TCD', 'lat': 8.9900, 'lon': 1.1400},
            {'nom': 'Adjengré-Sokodé', 'code': 'ADS', 'prefecture_code': 'TCD', 'lat': 8.9750, 'lon': 1.1550},
            {'nom': 'Kadambara-Sokodé', 'code': 'KDS', 'prefecture_code': 'TCD', 'lat': 9.0050, 'lon': 1.1250},
            {'nom': 'Tchalo-Sokodé', 'code': 'TCS', 'prefecture_code': 'TCD', 'lat': 8.9950, 'lon': 1.1450},
            {'nom': 'Sokodé-Kadambara', 'code': 'SKD', 'prefecture_code': 'TCD', 'lat': 8.9900, 'lon': 1.1300},
            
            # Région Centrale - Mô (cantons additionnels)
            {'nom': 'Mô-Sokodé', 'code': 'MOS', 'prefecture_code': 'MO', 'lat': 8.9550, 'lon': 1.1550},
            {'nom': 'Centre-Mô', 'code': 'CMO', 'prefecture_code': 'MO', 'lat': 8.9600, 'lon': 1.1600},
            {'nom': 'Mô-Centre-Sokodé', 'code': 'MCS', 'prefecture_code': 'MO', 'lat': 8.9550, 'lon': 1.1500},
            
            # Région Centrale - Assoli (cantons additionnels)
            {'nom': 'Assoli-Centre-Nord', 'code': 'ACN', 'prefecture_code': 'ASS', 'lat': 8.7600, 'lon': 1.2050},
            {'nom': 'Nord-Assoli', 'code': 'NAS', 'prefecture_code': 'ASS', 'lat': 8.7750, 'lon': 1.2150},
            {'nom': 'Centre-Assoli', 'code': 'CAS', 'prefecture_code': 'ASS', 'lat': 8.7500, 'lon': 1.2000},
            
            # Région Centrale - Bassar (cantons additionnels)
            {'nom': 'Bassar-Centre', 'code': 'BSC', 'prefecture_code': 'BAS', 'lat': 9.2550, 'lon': 0.7900},
            {'nom': 'Baghan-Bassar', 'code': 'BGB', 'prefecture_code': 'BAS', 'lat': 9.2750, 'lon': 0.7750},
            {'nom': 'Kabou-Bassar', 'code': 'KBB', 'prefecture_code': 'BAS', 'lat': 9.2350, 'lon': 0.8050},
            {'nom': 'Bassar-Baghan', 'code': 'BSB', 'prefecture_code': 'BAS', 'lat': 9.2600, 'lon': 0.7850},
            
            # Région Kara - Binah (cantons additionnels)
            {'nom': 'Pagouda-Centre', 'code': 'PAC', 'prefecture_code': 'BIN', 'lat': 9.7550, 'lon': 1.2900},
            {'nom': 'Centre-Binah', 'code': 'CBN', 'prefecture_code': 'BIN', 'lat': 9.7650, 'lon': 1.2950},
            {'nom': 'Kétao-Binah', 'code': 'KTB', 'prefecture_code': 'BIN', 'lat': 9.7450, 'lon': 1.2750},
            {'nom': 'Binah-Pagouda', 'code': 'BNP', 'prefecture_code': 'BIN', 'lat': 9.7500, 'lon': 1.2850},
            
            # Région Kara - Dankpen (cantons additionnels)
            {'nom': 'Guérin-Centre', 'code': 'GUC', 'prefecture_code': 'DKP', 'lat': 9.4200, 'lon': 0.2550},
            {'nom': 'Kouka-Guérin', 'code': 'KGU', 'prefecture_code': 'DKP', 'lat': 9.4250, 'lon': 0.2600},
            {'nom': 'Centre-Dankpen', 'code': 'CDK', 'prefecture_code': 'DKP', 'lat': 9.4350, 'lon': 0.2650},
            
            # Région Kara - Doufelgou (cantons additionnels)
            {'nom': 'Niamtougou-Centre', 'code': 'NIC', 'prefecture_code': 'DOU', 'lat': 9.7700, 'lon': 1.0900},
            {'nom': 'Koka-Niamtougou', 'code': 'KON', 'prefecture_code': 'DOU', 'lat': 9.7850, 'lon': 1.0750},
            {'nom': 'Siou-Niamtougou', 'code': 'SIN', 'prefecture_code': 'DOU', 'lat': 9.7550, 'lon': 1.1050},
            {'nom': 'Doufelgou-Centre', 'code': 'DFC', 'prefecture_code': 'DOU', 'lat': 9.7650, 'lon': 1.0850},
            
            # Région Kara - Kéran (cantons additionnels)
            {'nom': 'Centre-Kéran', 'code': 'CKR', 'prefecture_code': 'KER', 'lat': 9.6050, 'lon': 1.0050},
            {'nom': 'Nord-Kéran', 'code': 'NKR', 'prefecture_code': 'KER', 'lat': 9.6250, 'lon': 1.0150},
            {'nom': 'Kéran-Centre-Nord', 'code': 'KCN', 'prefecture_code': 'KER', 'lat': 9.6100, 'lon': 1.0100},
            
            # Région Kara - Kozah (cantons additionnels)
            {'nom': 'Kara-Centre', 'code': 'KAC', 'prefecture_code': 'KOZ', 'lat': 9.5550, 'lon': 1.1900},
            {'nom': 'Lama-Centre', 'code': 'LAC2', 'prefecture_code': 'KOZ', 'lat': 9.5650, 'lon': 1.1950},
            {'nom': 'Pya-Kara', 'code': 'PYK', 'prefecture_code': 'KOZ', 'lat': 9.5450, 'lon': 1.1750},
            {'nom': 'Sarakawa-Kara', 'code': 'SAK', 'prefecture_code': 'KOZ', 'lat': 9.5750, 'lon': 1.2050},
            {'nom': 'Kozah-Centre', 'code': 'KZC', 'prefecture_code': 'KOZ', 'lat': 9.5500, 'lon': 1.1850},
            
            # Région Kara - Bassar Kara (cantons additionnels)
            {'nom': 'Bassar-Kara-Centre', 'code': 'BKC', 'prefecture_code': 'BSR', 'lat': 9.2650, 'lon': 0.7950},
            {'nom': 'Dimouri-Bassar', 'code': 'DIB', 'prefecture_code': 'BSR', 'lat': 9.2850, 'lon': 0.8150},
            {'nom': 'Bassar-Dimouri', 'code': 'BSD', 'prefecture_code': 'BSR', 'lat': 9.2700, 'lon': 0.8000},
            
            # Région Savanes - Cinkassé (cantons additionnels)
            {'nom': 'Cinkassé-Centre-Nord', 'code': 'CCN', 'prefecture_code': 'CIN', 'lat': 11.1450, 'lon': 0.0450},
            {'nom': 'Centre-Cinkassé', 'code': 'CCK', 'prefecture_code': 'CIN', 'lat': 11.1400, 'lon': 0.0400},
            {'nom': 'Nord-Cinkassé', 'code': 'NCK', 'prefecture_code': 'CIN', 'lat': 11.1500, 'lon': 0.0500},
            
            # Région Savanes - Kpendjal (cantons additionnels)
            {'nom': 'Mandouri-Centre', 'code': 'MAC', 'prefecture_code': 'KPD', 'lat': 10.6700, 'lon': 0.4200},
            {'nom': 'Centre-Kpendjal', 'code': 'CKP', 'prefecture_code': 'KPD', 'lat': 10.6850, 'lon': 0.4350},
            {'nom': 'Kpendjal-Mandouri', 'code': 'KPM', 'prefecture_code': 'KPD', 'lat': 10.6750, 'lon': 0.4250},
            
            # Région Savanes - Kpendjal-Ouest (cantons additionnels)
            {'nom': 'Ouest-Centre', 'code': 'OUC', 'prefecture_code': 'KPO', 'lat': 10.5550, 'lon': 0.3050},
            {'nom': 'Naki-Centre', 'code': 'NAC', 'prefecture_code': 'KPO', 'lat': 10.5650, 'lon': 0.3150},
            {'nom': 'Kpendjal-Naki', 'code': 'KPN2', 'prefecture_code': 'KPO', 'lat': 10.5600, 'lon': 0.3100},
            
            # Région Savanes - Oti (cantons additionnels)
            {'nom': 'Mango-Centre', 'code': 'MNC', 'prefecture_code': 'OTI', 'lat': 10.3700, 'lon': 0.4700},
            {'nom': 'Bombouaka-Mango', 'code': 'BOM2', 'prefecture_code': 'OTI', 'lat': 10.3850, 'lon': 0.4850},
            {'nom': 'Galangashie-Mango', 'code': 'GAM', 'prefecture_code': 'OTI', 'lat': 10.3550, 'lon': 0.4550},
            {'nom': 'Korbongou-Mango', 'code': 'KOM', 'prefecture_code': 'OTI', 'lat': 10.3950, 'lon': 0.4950},
            {'nom': 'Oti-Mango', 'code': 'OTM', 'prefecture_code': 'OTI', 'lat': 10.3650, 'lon': 0.4650},
            
            # Région Savanes - Oti-Sud (cantons additionnels)
            {'nom': 'Sud-Centre', 'code': 'SUC', 'prefecture_code': 'OTS', 'lat': 10.2050, 'lon': 0.5050},
            {'nom': 'Mogou-Oti', 'code': 'MOO', 'prefecture_code': 'OTS', 'lat': 10.2150, 'lon': 0.5150},
            {'nom': 'Oti-Mogou', 'code': 'OTG', 'prefecture_code': 'OTS', 'lat': 10.2100, 'lon': 0.5100},
            
            # Région Savanes - Tandjouaré (cantons additionnels)
            {'nom': 'Tandjouaré-Centre', 'code': 'TDC', 'prefecture_code': 'TAN', 'lat': 10.7900, 'lon': 0.5200},
            {'nom': 'Borgou-Tandjouaré', 'code': 'BRT', 'prefecture_code': 'TAN', 'lat': 10.7950, 'lon': 0.5350},
            {'nom': 'Korbongou-Tand', 'code': 'KTN', 'prefecture_code': 'TAN', 'lat': 10.7750, 'lon': 0.5050},
            {'nom': 'Tandjouaré-Borgou', 'code': 'TDB', 'prefecture_code': 'TAN', 'lat': 10.7850, 'lon': 0.5250},
            
            # Région Savanes - Tône (cantons additionnels)
            {'nom': 'Dapaong-Centre', 'code': 'DPC', 'prefecture_code': 'TON', 'lat': 10.8700, 'lon': 0.2050},
            {'nom': 'Bombouaka-Dapaong', 'code': 'BMD', 'prefecture_code': 'TON', 'lat': 10.8850, 'lon': 0.2150},
            {'nom': 'Cinkassé-Dapaong', 'code': 'CKD', 'prefecture_code': 'TON', 'lat': 10.8550, 'lon': 0.1950},
            {'nom': 'Gando-Dapaong', 'code': 'GAD', 'prefecture_code': 'TON', 'lat': 10.8950, 'lon': 0.2250},
            {'nom': 'Korbongou-Dapaong', 'code': 'KBD', 'prefecture_code': 'TON', 'lat': 10.9050, 'lon': 0.2350},
            {'nom': 'Mandouri-Dapaong', 'code': 'MDD', 'prefecture_code': 'TON', 'lat': 10.8450, 'lon': 0.1850},
            {'nom': 'Nano-Dapaong', 'code': 'NAD', 'prefecture_code': 'TON', 'lat': 10.8750, 'lon': 0.2100},
            {'nom': 'Naki-Dapaong', 'code': 'NKD', 'prefecture_code': 'TON', 'lat': 10.8650, 'lon': 0.2000},
            {'nom': 'Timbou-Dapaong', 'code': 'TID', 'prefecture_code': 'TON', 'lat': 10.8900, 'lon': 0.2200},
            {'nom': 'Tône-Dapaong', 'code': 'TND', 'prefecture_code': 'TON', 'lat': 10.8800, 'lon': 0.2100},
        ]

    def _print_statistics(self):
        """Affiche les statistiques finales"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('STATISTIQUES FINALES'))
        self.stdout.write('='*60)
        
        regions_count = Region.objects.count()
        prefectures_count = Prefecture.objects.count()
        cantons_count = Canton.objects.count()
        
        self.stdout.write(f'Régions: {regions_count}')
        self.stdout.write(f'Préfectures: {prefectures_count}')
        self.stdout.write(f'Cantons: {cantons_count}')
        
        self.stdout.write('\nDétails par région:')
        for region in Region.objects.all():
            pref_count = region.prefectures.count()
            canton_count = Canton.objects.filter(prefecture__region=region).count()
            self.stdout.write(
                f'  {region.nom}: {pref_count} préfectures, {canton_count} cantons'
            )
        
        self.stdout.write('='*60)
        
        # Validation de la cohérence hiérarchique
        self._validate_hierarchy()

    def _validate_hierarchy(self):
        """Valide la cohérence hiérarchique des données"""
        self.stdout.write('\nValidation de la cohérence hiérarchique...')
        
        errors = []
        
        # Vérifier que chaque préfecture a une région valide
        for prefecture in Prefecture.objects.all():
            if not prefecture.region:
                errors.append(f'Préfecture {prefecture.nom} sans région')
        
        # Vérifier que chaque canton a une préfecture valide
        for canton in Canton.objects.all():
            if not canton.prefecture:
                errors.append(f'Canton {canton.nom} sans préfecture')
        
        if errors:
            self.stdout.write(self.style.ERROR(f'X {len(errors)} erreurs détectées:'))
            for error in errors:
                self.stdout.write(self.style.ERROR(f'  - {error}'))
        else:
            self.stdout.write(self.style.SUCCESS('+ Cohérence hiérarchique validée'))
