# Configuration de l'Internationalisation (i18n)

## Vue d'Ensemble

La plateforme Haroo est configurée pour supporter le français comme langue principale, avec une structure permettant l'ajout futur des langues Ewe et Kabyè.

## Configuration

### Langue par Défaut
- **Langue**: Français (fr)
- **Fuseau horaire**: Africa/Lome
- **Formats**: Formats français pour dates, nombres et devise

### Formats de Date (Exigence 38.2)
- **Format standard**: JJ/MM/AAAA (ex: 25/12/2024)
- **Format avec heure**: JJ/MM/AAAA HH:MM (ex: 25/12/2024 14:30)

### Formats de Nombre (Exigence 38.4)
- **Séparateur décimal**: Virgule (,)
- **Séparateur de milliers**: Espace insécable
- **Exemple**: 1 500,50

### Format de Devise (Exigence 38.3)
- **Devise**: Franc CFA (FCFA)
- **Format**: Montant avec espace + FCFA
- **Exemples**:
  - 1 000 FCFA
  - 1 500,50 FCFA
  - 1,5 M FCFA (format compact)

## Utilisation dans le Code

### 1. Dans les Templates Django

```django
{% load currency_tags %}

{# Formater un montant en FCFA #}
{{ transaction.montant|fcfa }}
{# Résultat: 1 000 FCFA #}

{# Avec décimales #}
{{ prix.montant|fcfa:2 }}
{# Résultat: 1 500,50 FCFA #}

{# Format compact #}
{{ total|fcfa_short }}
{# Résultat: 1,5 M FCFA #}

{# Tag de formatage #}
{% format_currency montant 'FCFA' 2 %}
```

### 2. Dans les Serializers DRF

```python
from apps.core.fields import FCFAField, FCFADecimalField

class TransactionSerializer(serializers.ModelSerializer):
    # Montant formaté avec symbole FCFA
    montant = FCFAField(max_digits=12, decimal_places=0)
    
    # Montant avec décimales (sans symbole pour calculs)
    prix_unitaire = FCFADecimalField(max_digits=10, decimal_places=2)
```

### 3. Dans le Code Python

```python
from apps.core.currency import format_fcfa, parse_fcfa, format_fcfa_short

# Formater un montant
montant_formate = format_fcfa(1000)  # "1 000 FCFA"
montant_formate = format_fcfa(1500.50, decimal_places=2)  # "1 500,50 FCFA"

# Parser un montant
montant = parse_fcfa("1 000 FCFA")  # Decimal('1000')
montant = parse_fcfa("1 500,50")  # Decimal('1500.50')

# Format compact
compact = format_fcfa_short(1500000)  # "1,5 M FCFA"
```

### 4. Dans les Modèles

```python
from django.db import models
from django.utils.formats import date_format, number_format

class Transaction(models.Model):
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    
    def get_montant_display(self):
        """Retourne le montant formaté en FCFA"""
        from apps.core.currency import format_fcfa
        return format_fcfa(self.montant)
    
    def get_date_display(self):
        """Retourne la date formatée en français"""
        return date_format(self.date, format='SHORT_DATE_FORMAT')
```

## Génération des Fichiers de Traduction

### Créer/Mettre à jour les fichiers de traduction

```bash
# Extraire les chaînes à traduire
python manage.py makemessages -l fr

# Compiler les traductions
python manage.py compilemessages
```

### Marquer les chaînes pour traduction

```python
from django.utils.translation import gettext_lazy as _

# Dans les modèles
class Document(models.Model):
    titre = models.CharField(_("Titre"), max_length=200)

# Dans les vues
message = _("Document acheté avec succès")

# Dans les serializers
class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['titre', 'description']
        extra_kwargs = {
            'titre': {'label': _('Titre')},
            'description': {'label': _('Description')},
        }
```

## Structure pour Langues Futures (Exigence 38.5)

La plateforme est structurée pour faciliter l'ajout de langues supplémentaires:

### 1. Ajouter une langue dans settings.py

```python
LANGUAGES = [
    ('fr', 'Français'),
    ('ee', 'Ewe'),  # Décommenter pour activer
    ('kbp', 'Kabyè'),  # Décommenter pour activer
]
```

### 2. Créer les fichiers de traduction

```bash
# Pour Ewe
python manage.py makemessages -l ee

# Pour Kabyè
python manage.py makemessages -l kbp
```

### 3. Créer les formats personnalisés

Créer `haroo/formats/ee.py` et `haroo/formats/kbp.py` avec les formats appropriés.

## Tests

### Tester les formats

```python
from django.test import TestCase
from apps.core.currency import format_fcfa, parse_fcfa

class CurrencyFormattingTestCase(TestCase):
    def test_format_fcfa(self):
        self.assertEqual(format_fcfa(1000), "1 000 FCFA")
        self.assertEqual(format_fcfa(1500.50, decimal_places=2), "1 500,50 FCFA")
    
    def test_parse_fcfa(self):
        self.assertEqual(parse_fcfa("1 000 FCFA"), Decimal('1000'))
        self.assertEqual(parse_fcfa("1 500,50"), Decimal('1500.50'))
```

## Références

- **Django i18n**: https://docs.djangoproject.com/en/4.2/topics/i18n/
- **Django Formats**: https://docs.djangoproject.com/en/4.2/topics/i18n/formatting/
- **Exigences**: 38.1, 38.2, 38.3, 38.4, 38.5
