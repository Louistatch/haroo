#!/usr/bin/env python3
"""
Script pour télécharger des images réelles pour la Plateforme Agricole Togo
Utilise des sources gratuites et libres de droits
"""

import os
import requests
import time
from pathlib import Path

# Configuration
BASE_DIR = Path("public/images")
TIMEOUT = 30

# Sources d'images gratuites (pas besoin d'API key)
UNSPLASH_SOURCE = "https://source.unsplash.com"
PICSUM_SOURCE = "https://picsum.photos"

def create_directories():
    """Créer la structure de dossiers"""
    directories = [
        BASE_DIR / "hero",
        BASE_DIR / "users",
        BASE_DIR / "cultures",
        BASE_DIR / "icons",
        BASE_DIR / "placeholder"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ Dossier créé: {directory}")

def download_image(url, filepath, description=""):
    """Télécharger une image depuis une URL"""
    try:
        print(f"📥 Téléchargement: {description or filepath.name}...")
        response = requests.get(url, timeout=TIMEOUT, stream=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        file_size = filepath.stat().st_size / 1024  # KB
        print(f"   ✓ Sauvegardé: {filepath.name} ({file_size:.1f} KB)")
        return True
    except Exception as e:
        print(f"   ✗ Erreur: {e}")
        return False

def download_hero_images():
    """Télécharger les images de bannière (agriculture africaine)"""
    print("\n🌾 TÉLÉCHARGEMENT DES IMAGES DE HERO")
    print("=" * 60)
    
    hero_images = [
        {
            "name": "agriculture.jpg",
            "query": "african-agriculture",
            "description": "Agriculture africaine"
        },
        {
            "name": "farmer.jpg",
            "query": "african-farmer",
            "description": "Agriculteur africain"
        },
        {
            "name": "harvest.jpg",
            "query": "harvest-africa",
            "description": "Récolte en Afrique"
        }
    ]
    
    for img in hero_images:
        url = f"{UNSPLASH_SOURCE}/1920x1080/?{img['query']}"
        filepath = BASE_DIR / "hero" / img["name"]
        download_image(url, filepath, img["description"])
        time.sleep(1)  # Respecter les limites de taux

def download_user_avatars():
    """Télécharger les avatars d'agronomes"""
    print("\n👤 TÉLÉCHARGEMENT DES AVATARS D'AGRONOMES")
    print("=" * 60)
    
    # Utiliser des portraits génériques
    for i in range(1, 16):
        url = f"{UNSPLASH_SOURCE}/400x400/?portrait,professional,face&sig={i}"
        filepath = BASE_DIR / "users" / f"agronomist-{i}.jpg"
        download_image(url, filepath, f"Agronome {i}")
        time.sleep(1)

def download_culture_images():
    """Télécharger les images de cultures"""
    print("\n🌱 TÉLÉCHARGEMENT DES IMAGES DE CULTURES")
    print("=" * 60)
    
    cultures = [
        {"name": "mais.jpg", "query": "corn-field", "description": "Maïs"},
        {"name": "riz.jpg", "query": "rice-field", "description": "Riz"},
        {"name": "manioc.jpg", "query": "cassava-plant", "description": "Manioc"},
        {"name": "tomate.jpg", "query": "tomato-plant", "description": "Tomate"},
        {"name": "oignon.jpg", "query": "onion-field", "description": "Oignon"},
        {"name": "arachide.jpg", "query": "peanut-plant", "description": "Arachide"},
        {"name": "soja.jpg", "query": "soybean-field", "description": "Soja"},
        {"name": "coton.jpg", "query": "cotton-field", "description": "Coton"}
    ]
    
    for culture in cultures:
        url = f"{UNSPLASH_SOURCE}/800x600/?{culture['query']}"
        filepath = BASE_DIR / "cultures" / culture["name"]
        download_image(url, filepath, culture["description"])
        time.sleep(1)

def download_placeholder_images():
    """Télécharger les images placeholder"""
    print("\n🎨 TÉLÉCHARGEMENT DES PLACEHOLDERS")
    print("=" * 60)
    
    placeholders = [
        {
            "name": "user-default.jpg",
            "url": f"{PICSUM_PHOTOS}/400/400?grayscale",
            "description": "Avatar par défaut"
        },
        {
            "name": "document-default.jpg",
            "url": f"{PICSUM_PHOTOS}/800/600?grayscale",
            "description": "Document par défaut"
        },
        {
            "name": "culture-default.jpg",
            "url": f"{UNSPLASH_SOURCE}/800x600/?plant",
            "description": "Culture par défaut"
        }
    ]
    
    for placeholder in placeholders:
        filepath = BASE_DIR / "placeholder" / placeholder["name"]
        download_image(placeholder["url"], filepath, placeholder["description"])
        time.sleep(1)

def download_additional_images():
    """Télécharger des images supplémentaires pour le contexte togolais"""
    print("\n🇹🇬 TÉLÉCHARGEMENT D'IMAGES CONTEXTUELLES")
    print("=" * 60)
    
    additional = [
        {
            "folder": "hero",
            "name": "togo-landscape.jpg",
            "query": "west-africa-landscape",
            "size": "1920x1080",
            "description": "Paysage du Togo"
        },
        {
            "folder": "hero",
            "name": "market.jpg",
            "query": "african-market",
            "size": "1920x1080",
            "description": "Marché africain"
        },
        {
            "folder": "cultures",
            "name": "igname.jpg",
            "query": "yam-plant",
            "size": "800x600",
            "description": "Igname"
        },
        {
            "folder": "cultures",
            "name": "cafe.jpg",
            "query": "coffee-plantation",
            "size": "800x600",
            "description": "Café"
        },
        {
            "folder": "cultures",
            "name": "cacao.jpg",
            "query": "cocoa-plantation",
            "size": "800x600",
            "description": "Cacao"
        }
    ]
    
    for img in additional:
        url = f"{UNSPLASH_SOURCE}/{img['size']}/?{img['query']}"
        filepath = BASE_DIR / img["folder"] / img["name"]
        download_image(url, filepath, img["description"])
        time.sleep(1)

def create_image_manifest():
    """Créer un fichier manifest avec toutes les images téléchargées"""
    print("\n📋 CRÉATION DU MANIFEST")
    print("=" * 60)
    
    manifest = []
    
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith(('.jpg', '.jpeg', '.png')):
                filepath = Path(root) / file
                size = filepath.stat().st_size / 1024  # KB
                relative_path = filepath.relative_to(BASE_DIR)
                manifest.append(f"{relative_path} ({size:.1f} KB)")
    
    manifest_file = BASE_DIR / "MANIFEST.txt"
    with open(manifest_file, 'w', encoding='utf-8') as f:
        f.write("IMAGES TÉLÉCHARGÉES\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Total: {len(manifest)} images\n\n")
        for item in sorted(manifest):
            f.write(f"✓ {item}\n")
    
    print(f"✅ Manifest créé: {manifest_file}")
    print(f"   Total: {len(manifest)} images téléchargées")

def main():
    """Fonction principale"""
    print("🖼️  TÉLÉCHARGEMENT D'IMAGES RÉELLES")
    print("=" * 60)
    print("Plateforme Agricole Intelligente du Togo")
    print("Sources: Unsplash (libre de droits)")
    print("=" * 60)
    
    # Créer les dossiers
    create_directories()
    
    # Télécharger les images
    download_hero_images()
    download_user_avatars()
    download_culture_images()
    download_placeholder_images()
    download_additional_images()
    
    # Créer le manifest
    create_image_manifest()
    
    print("\n" + "=" * 60)
    print("🎉 TÉLÉCHARGEMENT TERMINÉ!")
    print("=" * 60)
    print("\n📝 Prochaines étapes:")
    print("   1. Vérifiez les images dans public/images/")
    print("   2. Optimisez-les: node optimize-images.js")
    print("   3. Testez le site: npm run dev")
    print("\n✨ Toutes les images sont libres de droits (Unsplash License)")

if __name__ == "__main__":
    main()
