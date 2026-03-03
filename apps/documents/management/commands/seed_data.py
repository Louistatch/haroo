"""
Commande pour peupler la base de données avec des données de démonstration
"""
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile


class Command(BaseCommand):
    help = 'Peuple la base de données avec des données de démonstration (régions, documents)'

    def handle(self, *args, **options):
        self.stdout.write('Début du peuplement de la base de données...')
        self._create_locations()
        self._create_documents()
        self.stdout.write(self.style.SUCCESS('Base de données peuplée avec succès!'))

    def _create_locations(self):
        from apps.locations.models import Region, Prefecture, Canton

        regions_data = [
            {'nom': 'Maritime', 'code': 'MAR', 'prefectures': [
                {'nom': 'Golfe', 'code': 'GOL', 'cantons': ['Lomé-Centre', 'Agoè', 'Bè', 'Aflao']},
                {'nom': 'Zio', 'code': 'ZIO', 'cantons': ['Tsévié', 'Kpomé', 'Kpété-Béna']},
                {'nom': 'Vo', 'code': 'VOO', 'cantons': ['Vogan', 'Aného', 'Gboto']},
                {'nom': 'Lacs', 'code': 'LAC', 'cantons': ['Togoville', 'Glidji', 'Agbodrafo']},
            ]},
            {'nom': 'Plateaux', 'code': 'PLA', 'prefectures': [
                {'nom': 'Kloto', 'code': 'KLO', 'cantons': ['Kpalimé', 'Agou', 'Kpété']},
                {'nom': 'Danyi', 'code': 'DAN', 'cantons': ['Danyi-Apéyémé', 'Danyi-Dzogbégan', 'Danyi-Gblavé']},
                {'nom': 'Amou', 'code': 'AMO', 'cantons': ['Amou-Oblo', 'Weme', 'Kpekpleme']},
                {'nom': 'Ogou', 'code': 'OGO', 'cantons': ['Atakpamé', 'Badou', 'Blitta']},
            ]},
            {'nom': 'Centrale', 'code': 'CEN', 'prefectures': [
                {'nom': 'Tchaoudjo', 'code': 'TCH', 'cantons': ['Sokodé', 'Tchamba', 'Boua']},
                {'nom': 'Sotouboua', 'code': 'SOT', 'cantons': ['Sotouboua', 'Kambolé', 'Djarkpanga']},
                {'nom': 'Blitta', 'code': 'BLI', 'cantons': ['Blitta', 'Pagala', 'Anié']},
            ]},
            {'nom': 'Kara', 'code': 'KAR', 'prefectures': [
                {'nom': 'Kozah', 'code': 'KOZ', 'cantons': ['Kara', 'Lama-Kara', 'Pya']},
                {'nom': 'Binah', 'code': 'BIN', 'cantons': ['Niamtougou', 'Pagouda', 'Alédjo']},
                {'nom': 'Bassar', 'code': 'BAS', 'cantons': ['Bassar', 'Kabou', 'Katchamba']},
            ]},
            {'nom': 'Savanes', 'code': 'SAV', 'prefectures': [
                {'nom': 'Tone', 'code': 'TON', 'cantons': ['Dapaong', 'Bombouaka', 'Gando']},
                {'nom': 'Kpendjal', 'code': 'KPE', 'cantons': ['Mandouri', 'Kpantchéré', 'Naki-Est']},
                {'nom': 'Oti', 'code': 'OTI', 'cantons': ['Mango', 'Koumongou', 'Borgou']},
            ]},
        ]

        canton_counter = 0
        for region_data in regions_data:
            region, created = Region.objects.get_or_create(
                code=region_data['code'],
                defaults={'nom': region_data['nom']}
            )
            if created:
                self.stdout.write(f'  Région créée: {region.nom}')

            for pref_data in region_data['prefectures']:
                pref, created = Prefecture.objects.get_or_create(
                    code=pref_data['code'],
                    defaults={'nom': pref_data['nom'], 'region': region}
                )
                if created:
                    self.stdout.write(f'    Préfecture créée: {pref.nom}')

                for canton_nom in pref_data['cantons']:
                    canton_counter += 1
                    canton_code = f'C{canton_counter:03d}'
                    Canton.objects.get_or_create(
                        nom=canton_nom,
                        prefecture=pref,
                        defaults={'code': canton_code}
                    )

        self.stdout.write(self.style.SUCCESS(f'Localités créées: {Region.objects.count()} régions, {Prefecture.objects.count()} préfectures, {Canton.objects.count()} cantons'))

    def _create_documents(self):
        from apps.documents.models import DocumentTemplate, DocumentTechnique
        from apps.locations.models import Region, Prefecture, Canton

        fake_excel_content = b'PK\x03\x04' + b'\x00' * 26 + b'[Content_Types].xml' + b'\x00' * 100

        template_ce, _ = DocumentTemplate.objects.get_or_create(
            titre='Template Compte d\'Exploitation',
            defaults={
                'description': 'Template standard pour les comptes d\'exploitation prévisionnels',
                'type_document': 'COMPTE_EXPLOITATION',
                'format_fichier': 'EXCEL',
                'variables_requises': ['culture', 'superficie', 'region'],
                'version': 1,
            }
        )
        if not template_ce.fichier_template:
            template_ce.fichier_template.save('template_ce.xlsx', ContentFile(fake_excel_content), save=True)

        template_it, _ = DocumentTemplate.objects.get_or_create(
            titre='Template Itinéraire Technique',
            defaults={
                'description': 'Template standard pour les itinéraires techniques',
                'type_document': 'ITINERAIRE_TECHNIQUE',
                'format_fichier': 'WORD',
                'variables_requises': ['culture', 'region', 'saison'],
                'version': 1,
            }
        )
        if not template_it.fichier_template:
            template_it.fichier_template.save('template_it.docx', ContentFile(fake_excel_content), save=True)

        maritime = Region.objects.filter(code='MAR').first()
        plateaux = Region.objects.filter(code='PLA').first()
        centrale = Region.objects.filter(code='CEN').first()
        kara = Region.objects.filter(code='KAR').first()
        savanes = Region.objects.filter(code='SAV').first()

        golfe = Prefecture.objects.filter(code='GOL').first()
        kloto = Prefecture.objects.filter(code='KLO').first()
        kozah = Prefecture.objects.filter(code='KOZ').first()
        tone = Prefecture.objects.filter(code='TON').first()
        zio = Prefecture.objects.filter(code='ZIO').first()

        documents_data = [
            {
                'titre': 'Compte d\'Exploitation Maïs - Région Maritime',
                'description': 'Compte d\'exploitation prévisionnel pour la culture du maïs en région Maritime. Inclut les charges, les rendements estimés et les projections de revenus sur 12 mois.',
                'prix': '5000.00',
                'culture': 'Maïs',
                'region': maritime,
                'prefecture': golfe,
                'template': template_ce,
            },
            {
                'titre': 'Itinéraire Technique Manioc - Région des Plateaux',
                'description': 'Guide complet des pratiques culturales du manioc adapté aux sols et au climat de la région des Plateaux. Phases de préparation, plantation, entretien et récolte.',
                'prix': '3500.00',
                'culture': 'Manioc',
                'region': plateaux,
                'prefecture': kloto,
                'template': template_it,
            },
            {
                'titre': 'Compte d\'Exploitation Tomate - Préfecture de Zio',
                'description': 'Analyse financière détaillée pour la production de tomates sous serre et en plein champ dans la préfecture de Zio. Rentabilité et points de seuil inclus.',
                'prix': '7500.00',
                'culture': 'Tomate',
                'region': maritime,
                'prefecture': zio,
                'template': template_ce,
            },
            {
                'titre': 'Itinéraire Technique Riz - Région Centrale',
                'description': 'Guide technique complet pour la riziculture pluviale et irriguée en région Centrale. Variétés recommandées, gestion de l\'eau, fertilisation et protection des cultures.',
                'prix': '4500.00',
                'culture': 'Riz',
                'region': centrale,
                'template': template_it,
            },
            {
                'titre': 'Compte d\'Exploitation Arachide - Région Kara',
                'description': 'Plan financier pour la production d\'arachides en région Kara. Comprend les coûts de production, les prix de marché et les projections de bénéfices.',
                'prix': '4000.00',
                'culture': 'Arachide',
                'region': kara,
                'prefecture': kozah,
                'template': template_ce,
            },
            {
                'titre': 'Itinéraire Technique Sorgho - Région des Savanes',
                'description': 'Pratiques culturales optimisées pour le sorgho en zone soudanienne. Adapté aux conditions climatiques des Savanes avec gestion des périodes sèches.',
                'prix': '3000.00',
                'culture': 'Sorgho',
                'region': savanes,
                'prefecture': tone,
                'template': template_it,
            },
            {
                'titre': 'Compte d\'Exploitation Oignon - Préfecture de Tone',
                'description': 'Budget prévisionnel pour la culture d\'oignons irrigués dans la région des Savanes. Analyse de rentabilité sur deux campagnes culturales.',
                'prix': '6000.00',
                'culture': 'Oignon',
                'region': savanes,
                'prefecture': tone,
                'template': template_ce,
            },
            {
                'titre': 'Itinéraire Technique Igname - Région des Plateaux',
                'description': 'Guide complet pour la production d\'igname en région des Plateaux. Sélection des semenceaux, techniques de buttes, gestion des maladies et conservation.',
                'prix': '4200.00',
                'culture': 'Igname',
                'region': plateaux,
                'template': template_it,
            },
            {
                'titre': 'Compte d\'Exploitation Maraîchage - Région Maritime',
                'description': 'Compte d\'exploitation pour une exploitation maraîchère diversifiée (légumes feuilles, légumes-fruits) en périphérie de Lomé. Marché local et export.',
                'prix': '8500.00',
                'culture': 'Maraîchage',
                'region': maritime,
                'prefecture': golfe,
                'template': template_ce,
            },
            {
                'titre': 'Itinéraire Technique Coton - Région Centrale',
                'description': 'Guide des bonnes pratiques pour la culture cotonnière en région Centrale. Intrants recommandés, calendrier cultural et gestion intégrée des ravageurs.',
                'prix': '5500.00',
                'culture': 'Coton',
                'region': centrale,
                'template': template_it,
            },
            {
                'titre': 'Compte d\'Exploitation Manioc - Région Kara',
                'description': 'Analyse financière pour la culture et transformation du manioc (gari, farine) en région Kara. Intégration de la chaîne de valeur.',
                'prix': '6500.00',
                'culture': 'Manioc',
                'region': kara,
                'template': template_ce,
            },
            {
                'titre': 'Itinéraire Technique Niébé - Région des Savanes',
                'description': 'Pratiques culturales pour le niébé (haricot cowpea) en zone soudanienne. Association avec le sorgho, gestion des ennemis des cultures et stockage.',
                'prix': '2500.00',
                'culture': 'Niébé',
                'region': savanes,
                'template': template_it,
            },
        ]

        created_count = 0
        for doc_data in documents_data:
            doc, created = DocumentTechnique.objects.get_or_create(
                titre=doc_data['titre'],
                defaults={
                    'description': doc_data['description'],
                    'prix': doc_data['prix'],
                    'culture': doc_data['culture'],
                    'region': doc_data.get('region'),
                    'prefecture': doc_data.get('prefecture'),
                    'template': doc_data['template'],
                    'actif': True,
                }
            )
            if created:
                doc.fichier_genere.save(
                    f'doc_{doc.id}.xlsx',
                    ContentFile(fake_excel_content),
                    save=True
                )
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'{created_count} documents créés ({DocumentTechnique.objects.count()} au total)'))
