"""
Formats personnalisés pour le français (Togo)
Conforme aux exigences 38.2, 38.3, 38.4
"""

# Format de date: JJ/MM/AAAA
DATE_FORMAT = 'd/m/Y'
SHORT_DATE_FORMAT = 'd/m/Y'
DATETIME_FORMAT = 'd/m/Y H:i'
SHORT_DATETIME_FORMAT = 'd/m/Y H:i'
TIME_FORMAT = 'H:i'

# Format de date pour les inputs
DATE_INPUT_FORMATS = [
    '%d/%m/%Y',  # '25/12/2024'
    '%d-%m-%Y',  # '25-12-2024'
    '%Y-%m-%d',  # '2024-12-25' (ISO)
]

DATETIME_INPUT_FORMATS = [
    '%d/%m/%Y %H:%M',  # '25/12/2024 14:30'
    '%d/%m/%Y %H:%M:%S',  # '25/12/2024 14:30:00'
    '%Y-%m-%d %H:%M:%S',  # '2024-12-25 14:30:00' (ISO)
]

# Format de nombre: virgule comme séparateur décimal
DECIMAL_SEPARATOR = ','
THOUSAND_SEPARATOR = ' '  # Espace insécable
NUMBER_GROUPING = 3

# Premiers jours de la semaine (Lundi)
FIRST_DAY_OF_WEEK = 1

# Format de mois
MONTH_DAY_FORMAT = 'j F'
YEAR_MONTH_FORMAT = 'F Y'
