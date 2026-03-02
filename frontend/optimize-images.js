/**
 * Script d'optimisation des images
 * Optimise automatiquement toutes les images du dossier public/images
 * 
 * Usage: node optimize-images.js
 */

const fs = require('fs');
const path = require('path');

// Vérifier si sharp est installé
try {
  require.resolve('sharp');
} catch (e) {
  console.error('❌ Sharp n\'est pas installé!');
  console.log('📦 Installation: npm install sharp');
  process.exit(1);
}

const sharp = require('sharp');

// Configuration des dossiers
const config = [
  {
    name: 'Hero Images',
    input: './public/images/raw/hero',
    output: './public/images/hero',
    width: 1920,
    height: 1080,
    quality: 85
  },
  {
    name: 'User Avatars',
    input: './public/images/raw/users',
    output: './public/images/users',
    width: 400,
    height: 400,
    quality: 90
  },
  {
    name: 'Culture Images',
    input: './public/images/raw/cultures',
    output: './public/images/cultures',
    width: 800,
    height: 600,
    quality: 85
  }
];

// Créer les dossiers de sortie s'ils n'existent pas
config.forEach(dir => {
  if (!fs.existsSync(dir.output)) {
    fs.mkdirSync(dir.output, { recursive: true });
  }
});

// Fonction d'optimisation
async function optimizeImage(inputPath, outputPath, width, height, quality) {
  try {
    await sharp(inputPath)
      .resize(width, height, {
        fit: 'cover',
        position: 'center'
      })
      .jpeg({
        quality: quality,
        progressive: true,
        mozjpeg: true
      })
      .toFile(outputPath);
    
    // Calculer la réduction de taille
    const inputStats = fs.statSync(inputPath);
    const outputStats = fs.statSync(outputPath);
    const reduction = ((1 - outputStats.size / inputStats.size) * 100).toFixed(1);
    
    return {
      success: true,
      inputSize: inputStats.size,
      outputSize: outputStats.size,
      reduction: reduction
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

// Fonction pour formater la taille
function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// Traiter tous les dossiers
async function processAll() {
  console.log('🖼️  Optimisation des images');
  console.log('============================\n');

  let totalProcessed = 0;
  let totalErrors = 0;
  let totalSaved = 0;

  for (const dir of config) {
    console.log(`📁 ${dir.name}`);
    console.log(`   Input:  ${dir.input}`);
    console.log(`   Output: ${dir.output}`);
    console.log(`   Size:   ${dir.width}x${dir.height}px @ ${dir.quality}% quality\n`);

    // Vérifier si le dossier d'entrée existe
    if (!fs.existsSync(dir.input)) {
      console.log(`   ⚠️  Dossier non trouvé, création...\n`);
      fs.mkdirSync(dir.input, { recursive: true });
      continue;
    }

    // Lire tous les fichiers
    const files = fs.readdirSync(dir.input);
    const imageFiles = files.filter(file => 
      file.match(/\.(jpg|jpeg|png|webp)$/i)
    );

    if (imageFiles.length === 0) {
      console.log(`   ℹ️  Aucune image trouvée\n`);
      continue;
    }

    // Traiter chaque image
    for (const file of imageFiles) {
      const inputPath = path.join(dir.input, file);
      const outputFile = file.replace(/\.(png|jpeg|webp)$/i, '.jpg');
      const outputPath = path.join(dir.output, outputFile);

      process.stdout.write(`   Processing ${file}... `);

      const result = await optimizeImage(
        inputPath,
        outputPath,
        dir.width,
        dir.height,
        dir.quality
      );

      if (result.success) {
        const saved = result.inputSize - result.outputSize;
        totalSaved += saved;
        totalProcessed++;
        
        console.log(`✅ ${formatSize(result.inputSize)} → ${formatSize(result.outputSize)} (-${result.reduction}%)`);
      } else {
        totalErrors++;
        console.log(`❌ Erreur: ${result.error}`);
      }
    }

    console.log('');
  }

  // Résumé
  console.log('============================');
  console.log('📊 Résumé');
  console.log('============================');
  console.log(`✅ Images optimisées: ${totalProcessed}`);
  console.log(`❌ Erreurs: ${totalErrors}`);
  console.log(`💾 Espace économisé: ${formatSize(totalSaved)}`);
  console.log('');

  if (totalProcessed > 0) {
    console.log('🎉 Optimisation terminée avec succès!');
  } else {
    console.log('⚠️  Aucune image n\'a été optimisée.');
    console.log('');
    console.log('📝 Instructions:');
    console.log('   1. Créez le dossier: public/images/raw/');
    console.log('   2. Ajoutez vos images dans les sous-dossiers:');
    console.log('      - public/images/raw/hero/');
    console.log('      - public/images/raw/users/');
    console.log('      - public/images/raw/cultures/');
    console.log('   3. Relancez: node optimize-images.js');
  }
}

// Exécuter
processAll().catch(error => {
  console.error('❌ Erreur fatale:', error);
  process.exit(1);
});
