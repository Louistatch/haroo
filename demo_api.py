#!/usr/bin/env python
"""
Script de démonstration de l'API
Teste les principaux endpoints du MVP
"""
import os
import django

# Setup Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'haroo.settings.dev'
django.setup()

from apps.locations.models import Region, Prefecture, Canton
from apps.users.models import User, AgronomeProfile
from django.contrib.auth.hashers import make_password

print("=" * 60)
print("🚀 DÉMONSTRATION API - Plateforme Agricole du Togo")
print("=" * 60)

# 1. Découpage Administratif
print("\n📍 1. DÉCOUPAGE ADMINISTRATIF")
print("-" * 60)
regions = Region.objects.all()
print(f"✅ {regions.count()} régions chargées:")
for region in regions:
    prefectures_count = region.prefectures.count()
    print(f"   • {region.nom} ({region.code}) - {prefectures_count} préfectures")

# 2. Créer un utilisateur de test
print("\n👤 2. CRÉATION D'UTILISATEURS DE TEST")
print("-" * 60)

# Créer un exploitant
if not User.objects.filter(username='exploitant_demo').exists():
    exploitant = User.objects.create(
        username='exploitant_demo',
        email='exploitant@demo.tg',
        phone_number='+22890000001',
        password=make_password('Demo123!'),
        first_name='Jean',
        last_name='Kouassi',
        user_type='EXPLOITANT',
        phone_verified=True
    )
    print(f"✅ Exploitant créé: {exploitant.username}")
else:
    print("ℹ️  Exploitant existe déjà")

# Créer un agronome
if not User.objects.filter(username='agronome_demo').exists():
    canton = Canton.objects.first()
    agronome = User.objects.create(
        username='agronome_demo',
        email='agronome@demo.tg',
        phone_number='+22890000002',
        password=make_password('Demo123!'),
        first_name='Marie',
        last_name='Mensah',
        user_type='AGRONOME',
        phone_verified=True
    )
    
    # Créer le profil agronome
    AgronomeProfile.objects.create(
        user=agronome,
        canton_rattachement=canton,
        specialisations=['Maraîchage', 'Céréaliculture'],
        statut_validation='EN_ATTENTE'
    )
    print(f"✅ Agronome créé: {agronome.username} (En attente de validation)")
else:
    print("ℹ️  Agronome existe déjà")

# Créer un admin
if not User.objects.filter(username='admin_demo').exists():
    admin = User.objects.create(
        username='admin_demo',
        email='admin@demo.tg',
        phone_number='+22890000003',
        password=make_password('Admin123!'),
        first_name='Admin',
        last_name='Système',
        user_type='ADMIN',
        is_staff=True,
        is_superuser=True,
        phone_verified=True
    )
    print(f"✅ Admin créé: {admin.username}")
else:
    print("ℹ️  Admin existe déjà")

# 3. Statistiques
print("\n📊 3. STATISTIQUES DU SYSTÈME")
print("-" * 60)
print(f"✅ Utilisateurs totaux: {User.objects.count()}")
print(f"   • Exploitants: {User.objects.filter(user_type='EXPLOITANT').count()}")
print(f"   • Agronomes: {User.objects.filter(user_type='AGRONOME').count()}")
print(f"   • Admins: {User.objects.filter(is_staff=True).count()}")

agronomes_en_attente = AgronomeProfile.objects.filter(statut_validation='EN_ATTENTE').count()
agronomes_valides = AgronomeProfile.objects.filter(statut_validation='VALIDE').count()
print(f"\n✅ Agronomes:")
print(f"   • En attente: {agronomes_en_attente}")
print(f"   • Validés: {agronomes_valides}")

# 4. Endpoints disponibles
print("\n🌐 4. ENDPOINTS API DISPONIBLES")
print("-" * 60)
print("Authentification:")
print("  POST /api/v1/auth/register")
print("  POST /api/v1/auth/login")
print("  POST /api/v1/auth/verify-sms")
print("  POST /api/v1/auth/refresh-token")
print("\nDécopage Administratif:")
print("  GET  /api/v1/regions/")
print("  GET  /api/v1/regions/{id}/prefectures/")
print("  GET  /api/v1/prefectures/{id}/cantons/")
print("\nAgronomes:")
print("  POST /api/v1/agronomists/register")
print("  GET  /api/v1/agronomists (annuaire public)")
print("  POST /api/v1/agronomists/{id}/validate (admin)")
print("  GET  /api/v1/agronomists/pending (admin)")
print("\nDocuments:")
print("  GET  /api/v1/documents/")
print("  POST /api/v1/documents/{id}/purchase")
print("\nPaiements:")
print("  POST /api/v1/payments/initiate")
print("  POST /api/v1/payments/webhooks/fedapay")

# 5. Informations de connexion
print("\n🔑 5. INFORMATIONS DE CONNEXION")
print("-" * 60)
print("Exploitant:")
print("  Username: exploitant_demo")
print("  Password: Demo123!")
print("\nAgronome:")
print("  Username: agronome_demo")
print("  Password: Demo123!")
print("\nAdmin:")
print("  Username: admin_demo")
print("  Password: Admin123!")

print("\n" + "=" * 60)
print("✅ Démonstration terminée!")
print("🚀 Démarrez le serveur: python manage.py runserver")
print("📖 Accédez à l'admin: http://localhost:8000/admin")
print("=" * 60)
