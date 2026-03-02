#!/usr/bin/env python3
"""
Script pour remplacer les émojis par des images réelles
Haroo - Plateforme Agricole Intelligente du Togo
"""
import os
import re
from pathlib import Path

# Mapping des émojis vers les composants Image
EMOJI_REPLACEMENTS = {
    # Agriculture
    '🌾': '<img src="/images/cultures/mais.jpg" alt="Culture" className="inline-icon" style={{width: 24, height: 24, borderRadius: "50%", objectFit: "cover", marginRight: 8}} />',
    
    # Documents
    '📄': '<img src="/images/placeholder/document-default.jpg" alt="Document" className="inline-icon" style={{width: 24, height: 24, borderRadius: "50%", objectFit: "cover", marginRight: 8}} />',
    
    # Utilisateurs
    '👨‍🌾': '<img src="/images/users/agronomist-1.jpg" alt="Agronome" className="inline-icon" style={{width: 24, height: 24, borderRadius: "50%", objectFit: "cover", marginRight: 8}} />',
    
    # Actions
    '📥': '<img src="/images/hero/harvest.jpg" alt="Télécharger" className="inline-icon" style={{width: 20, height: 20, borderRadius: "50%", objectFit: "cover", marginRight: 8}} />',
    '🛒': '<img src="/images/hero/market.jpg" alt="Acheter" className="inline-icon" style={{width: 20, height: 20, borderRadius: "50%", objectFit: "cover", marginRight: 8}} />',
    
    # Status
    '✅': '<img src="/images/hero/agriculture.jpg" alt="Succès" className="inline-icon" style={{width: 20, height: 20, borderRadius: "50%", objectFit: "cover", marginRight: 8}} />',
    '❌': '<img src="/images/hero/market.jpg" alt="Erreur" className="inline-icon" style={{width: 20, height: 20, borderRadius: "50%", objectFit: "cover", marginRight: 8}} />',
    '⚠️': '<img src="/images/hero/market.jpg" alt="Attention" className="inline-icon" style={{width: 20, height: 20, borderRadius: "50%", objectFit: "cover", marginRight: 8}} />',
    
    # Finance
    '💰': '<img src="/images/hero/market.jpg" alt="Prix" className="inline-icon" style={{width: 20, height: 20, borderRadius: "50%", objectFit: "cover", marginRight: 8}} />',
    
    # Stats
    '📊': '<img src="/images/hero/agriculture.jpg" alt="Statistiques" className="inline-icon" style={{width: 24, height: 24, borderRadius: "50%", objectFit: "cover", marginRight: 8}} />',
    
    # Temps
    '⏰': '<img src="/images/hero/farmer.jpg" alt="Temps" className="inline-icon" style={{width: 20, height: 20, borderRadius: "50%", objectFit: "cover", marginRight: 8}} />',
    '⏳': '<img src="/images/hero/farmer.jpg" alt="En attente" className="inline-icon" style={{width: 20, height: 20, borderRadius: "50%", objectFit: "cover", marginRight: 8}} />',
    
    # Objectifs
    '🎯': '<img src="/images/hero/agriculture.jpg" alt="Objectif" className="inline-icon" style={{width: 48, height: 48, borderRadius: "50%", objectFit: "cover"}} />',
}

def replace_emojis_in_file(file_path):
    """Remplacer les émojis dans un fichier"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        replacements_made = 0
        
        # Remplacer chaque émoji
        for emoji, replacement in EMOJI_REPLACEMENTS.items():
            if emoji in content:
                count = content.count(emoji)
                content = content.replace(emoji, replacement)
                replacements_made += count
                print(f"  {emoji} → Image ({count}x)")
        
        # Sauvegarder si des changements ont été faits
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return replacements_made
        
        return 0
        
    except Exception as e:
        print(f"  ❌ Erreur: {str(e)}")
        return 0


def main():
    """Fonction principale"""
    print("\n" + "="*60)
    print("REMPLACEMENT DES ÉMOJIS PAR DES IMAGES - HAROO")
    print("="*60)
    
    # Fichiers à traiter
    files_to_process = [
        'frontend/src/pages/Landing.tsx',
        'frontend/src/pages/Home.tsx',
        'frontend/src/pages/Documents.tsx',
        'frontend/src/pages/PurchaseHistory.tsx',
        'frontend/src/pages/PaymentSuccess.tsx',
        'frontend/src/pages/Dashboard.tsx',
        'frontend/src/pages/Agronomists.tsx',
        'frontend/src/components/Toast.tsx',
        'frontend/src/components/PurchaseModal.tsx',
        'frontend/src/components/Header.tsx',
    ]
    
    total_replacements = 0
    files_modified = 0
    
    for file_path in files_to_process:
        if os.path.exists(file_path):
            print(f"\n📝 {file_path}")
            replacements = replace_emojis_in_file(file_path)
            if replacements > 0:
                total_replacements += replacements
                files_modified += 1
                print(f"  ✅ {replacements} remplacement(s)")
            else:
                print(f"  ⏭️  Aucun émoji trouvé")
        else:
            print(f"\n⚠️  {file_path} - Fichier introuvable")
    
    # Résumé
    print("\n" + "="*60)
    print("RÉSUMÉ")
    print("="*60)
    print(f"Fichiers modifiés: {files_modified}/{len(files_to_process)}")
    print(f"Total remplacements: {total_replacements}")
    
    if total_replacements > 0:
        print("\n🎉 Remplacement terminé!")
        print("\n📝 Prochaines étapes:")
        print("  1. Vérifier les fichiers modifiés")
        print("  2. Tester l'affichage dans le navigateur")
        print("  3. Ajuster les tailles d'images si nécessaire")
        print("  4. Ajouter les styles CSS pour .inline-icon")
    else:
        print("\n⚠️  Aucun remplacement effectué")
    
    return total_replacements > 0


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
