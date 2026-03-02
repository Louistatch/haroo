#!/usr/bin/env python
"""Test rapide du projet"""
import os
import django

# Forcer le bon settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'haroo.settings.dev'

# Setup Django
django.setup()

# Tester les imports
from apps.locations.models import Region, Prefecture, Canton
from apps.users.models import User

print("✅ Django configuré correctement!")
print(f"✅ Régions dans la base: {Region.objects.count()}")
print(f"✅ Préfectures dans la base: {Prefecture.objects.count()}")
print(f"✅ Cantons dans la base: {Canton.objects.count()}")
print(f"✅ Utilisateurs dans la base: {User.objects.count()}")

print("\n🎉 Le projet fonctionne parfaitement!")
