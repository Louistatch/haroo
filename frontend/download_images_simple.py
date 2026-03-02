#!/usr/bin/env python3
"""
Script simple pour télécharger des images réelles
Utilise des URLs directes de sources gratuites
"""

import os
import urllib.request
import time
from pathlib import Path

# Configuration
BASE_DIR = Path("public/images")

# URLs d'images réelles (sources gratuites et libres de droits)
IMAGES = {
    "hero": [
        {
            "url": "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=1920&h=1080&fit=crop",
            "name": "agriculture.jpg",
            "desc": "Agriculture africaine"
        },
        {
            "url": "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=1920&h=1080&fit=crop",
            "name": "farmer.jpg",
            "desc": "Agriculteur au travail"
        },
        {
            "url": "https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=1920&h=1080&fit=crop",
            "name": "harvest.jpg",
            "desc": "Récolte"
        },
        {
            "url": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1920&h=1080&fit=crop",
            "name": "market.jpg",
            "desc": "Marché local"
        }
    ],
    "cultures": [
        {
            "url": "https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?w=800&h=600&fit=crop",
            "name": "mais.jpg",
            "desc": "Maïs"
        },
        {
            "url": "https://images.unsplash.com/photo-1536304993881-ff6e9eefa2a6?w=800&h=600&fit=crop",
            "name": "riz.jpg",
            "desc": "Riz"
        },
        {
            "url": "https://images.unsplash.com/photo-1592921870789-04563d55041c?w=800&h=600&fit=crop",
            "name": "tomate.jpg",
            "desc": "Tomates"
        },
        {
            "url": "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=800&h=600&fit=crop",
            "name": "oignon.jpg",
            "desc": "Oignons"
        },
        {
            "url": "https://images.unsplash.com/photo-1589927986089-35812388d1f4?w=800&h=600&fit=crop",
            "name": "arachide.jpg",
            "desc": "Arachides"
        },
        {
            "url": "https://images.unsplash.com/photo-1595855759920-86582396756a?w=800&h=600&fit=crop",
            "name": "manioc.jpg",
            "desc": "Manioc"
        },
        {
            "url": "https://images.unsplash.com/photo-1560493676-04071c5f467b?w=800&h=600&fit=crop",
            "name": "soja.jpg",
            "desc": "Soja"
        },
        {
            "url": "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=800&h=600&fit=crop",
            "name": "coton.jpg",
            "desc": "Coton"
        }
    ],
    "users": [
        {
            "url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=faces",
            "name": "agronomist-1.jpg",
            "desc": "Agronome 1"
        },
        {
            "url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=400&fit=crop&crop=faces",
            "name": "agronomist-2.jpg",
            "desc": "Agronome 2"
        },
        {
            "url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=400&fit=crop&crop=faces",
            "name": "agronomist-3.jpg",
            "desc": "Agronome 3"
        },
        {
            "url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=400&fit=crop&crop=faces",
            "name": "agronomist-4.jpg",
            "desc": "Agronome 4"
        },
        {
            "url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop&crop=faces",
            "name": "agronomist-5.jpg",
            "desc": "Agronome 5"
        },
        {
            "url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&h=400&fit=crop&crop=faces",
            "name": "agronomist-6.jpg",
            "desc": "Agronome 6"
        },
        {
            "url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400&h=400&fit=crop&crop=faces",
            "name": "agronomist-7.jpg",
            "desc": "Agronome 7"
        },
        {
            "url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&h=400&fit=crop&crop=faces",
            "name": "agronomist-8.jpg",
            "desc": "Agronome 8"
        },
        {
            "url": "https://images.unsplash.com/photo-1531427186611-ecfd6d936c79?w=400&h=400&fit=crop&crop=faces",
            "name": "agronomist-9.jpg",
            "desc": "Agronome 9"
        },
        {
            "url": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=400&h=400&fit=crop&crop=faces",
            "name": "agronomist-10.jpg",
            "desc": "Agronome 10"
        },
        {
            "url": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=400&h=400&fit=crop&crop=faces",
            "name": "agronomist-11.jpg",
            "desc": "Agronome 11"
        },
        {
            "url": "https://images.unsplash.com/photo-1488426862026-3ee34a7d66df?w=400&h=400&fit=crop&crop=faces",
            "name": "agronomist-12.jpg",
            "desc": "Agronome 12"
        }
    ],
    "placeholder": [
        {
            "url": "https://images.unsplash.com/photo-1511367461989-f85a21fda167?w=400&h=400&fit=crop",
            "name": "user-default.jpg",
            "desc": "Avatar par défaut"
        },
        {
            "url": "https://images.unsplash.com/photo-1568667256549-094345857637?w=800&h=600&fit=crop",
            "name": "document-default.jpg",
            "desc": "Document par défaut"
        },
        {
            "url": "https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?w=800&h=600&fit=crop",
            "name": "culture-default.jpg",
            "desc": "Culture par défaut"
        }
    ]
}

def create_directories():
    """Créer la structure de dossiers"""
    print("📁 Création des dossiers...")
    for folder in IMAGES.keys():
        folder_path = BASE_DIR / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        print(f"   ✓ {folder}/")

def download_image(url, filepath, description):
    """Télécharger une image"""
    try:
        print(f"   📥 {description}...", end=" ", flush=True)
        
        # Ajouter un User-Agent pour éviter les blocages
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()
            with open(filepath, 'wb') as f:
                f.write(data)
        
        size = len(data) / 1024  # KB
        print(f"✓ ({size:.0f} KB)")
        return True
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False

def download_all_images():
    """Télécharger toutes les images"""
    total = sum(len(images) for images in IMAGES.values())
    downloaded = 0
    
    for folder, images in IMAGES.items():
        print(f"\n📸 {folder.upper()}")
        print("─" * 60)
        
        for img in images:
            filepath = BASE_DIR / folder / img["name"]
            if download_image(img["url"], filepath, img["desc"]):
                downloaded += 1
            time.sleep(0.5)  # Pause pour respecter les limites
    
    return downloaded, total

def create_summary():
    """Créer un résumé des images téléchargées"""
    summary_file = BASE_DIR / "IMAGES_SUMMARY.txt"
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("RÉSUMÉ DES IMAGES TÉLÉCHARGÉES\n")
        f.write("Plateforme Agricole Intelligente du Togo\n")
        f.write("=" * 70 + "\n\n")
        
        for folder, images in IMAGES.items():
            f.write(f"\n📁 {folder.upper()}/\n")
            f.write("─" * 70 + "\n")
            
            for img in images:
                filepath = BASE_DIR / folder / img["name"]
                if filepath.exists():
                    size = filepath.stat().st_size / 1024
                    f.write(f"  ✓ {img['name']:<30} {size:>8.1f} KB  {img['desc']}\n")
                else:
                    f.write(f"  ✗ {img['name']:<30} {'MANQUANT':>8}     {img['desc']}\n")
        
        f.write("\n" + "=" * 70 + "\n")
        f.write("Source: Unsplash (https://unsplash.com)\n")
        f.write("License: Unsplash License (libre d'utilisation)\n")
        f.write("=" * 70 + "\n")
    
    print(f"\n📋 Résumé créé: {summary_file}")

def main():
    """Fonction principale"""
    print("\n" + "=" * 70)
    print("🖼️  TÉLÉCHARGEMENT D'IMAGES RÉELLES")
    print("=" * 70)
    print("Plateforme Agricole Intelligente du Togo")
    print("Source: Unsplash (libre de droits)")
    print("=" * 70 + "\n")
    
    # Créer les dossiers
    create_directories()
    
    # Télécharger les images
    print("\n🚀 Début du téléchargement...")
    downloaded, total = download_all_images()
    
    # Créer le résumé
    create_summary()
    
    # Afficher le résultat
    print("\n" + "=" * 70)
    print("🎉 TÉLÉCHARGEMENT TERMINÉ!")
    print("=" * 70)
    print(f"✓ {downloaded}/{total} images téléchargées avec succès")
    print("\n📝 Prochaines étapes:")
    print("   1. Vérifiez les images dans public/images/")
    print("   2. Optimisez-les: node optimize-images.js")
    print("   3. Testez le site: npm run dev")
    print("\n✨ Toutes les images sont libres de droits (Unsplash License)")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Téléchargement interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n\n❌ Erreur: {e}")
