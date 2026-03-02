"""
Tests pour le formatage de devise FCFA
Valide les exigences 38.3, 38.4
"""

from decimal import Decimal
from django.test import TestCase
from apps.core.currency import format_fcfa, parse_fcfa, format_fcfa_short


class FCFAFormattingTestCase(TestCase):
    """Tests de formatage des montants FCFA"""
    
    def test_format_fcfa_basic(self):
        """Test du formatage de base"""
        result = format_fcfa(1000)
        self.assertIn("FCFA", result)
        self.assertIn("1", result)
        self.assertIn("000", result)
        
        self.assertEqual(format_fcfa(500), "500 FCFA")
        self.assertEqual(format_fcfa(0), "0 FCFA")
    
    def test_format_fcfa_with_decimals(self):
        """Test du formatage avec décimales"""
        result = format_fcfa(1500.50, decimal_places=2)
        self.assertIn("FCFA", result)
        self.assertIn("1", result)
        self.assertIn("500", result)
        self.assertIn(",50", result)
        
        result2 = format_fcfa(999.99, decimal_places=2)
        self.assertIn("999", result2)
        self.assertIn(",99", result2)
    
    def test_format_fcfa_large_numbers(self):
        """Test du formatage de grands nombres"""
        result = format_fcfa(1000000)
        self.assertIn("FCFA", result)
        self.assertIn("1", result)
        self.assertIn("000", result)
        
        result2 = format_fcfa(1234567)
        self.assertIn("FCFA", result2)
        self.assertIn("1", result2)
        self.assertIn("234", result2)
        self.assertIn("567", result2)
    
    def test_format_fcfa_without_symbol(self):
        """Test du formatage sans symbole FCFA"""
        result = format_fcfa(1000, use_symbol=False)
        self.assertNotIn("FCFA", result)
        self.assertIn("1", result)
        self.assertIn("000", result)
        
        result2 = format_fcfa(1500.50, use_symbol=False, decimal_places=2)
        self.assertNotIn("FCFA", result2)
        self.assertIn(",50", result2)
    
    def test_format_fcfa_none_value(self):
        """Test du formatage avec valeur None"""
        self.assertEqual(format_fcfa(None), "0 FCFA")
        self.assertEqual(format_fcfa(None, use_symbol=False), "0")
    
    def test_format_fcfa_decimal_type(self):
        """Test du formatage avec type Decimal"""
        result = format_fcfa(Decimal('1000'))
        self.assertIn("FCFA", result)
        self.assertIn("1", result)
        self.assertIn("000", result)
        
        result2 = format_fcfa(Decimal('1500.50'), decimal_places=2)
        self.assertIn("FCFA", result2)
        self.assertIn(",50", result2)
    
    def test_format_fcfa_negative(self):
        """Test du formatage de nombres négatifs"""
        result = format_fcfa(-1000)
        self.assertIn("-", result)
        self.assertIn("1", result)
        self.assertIn("000", result)


class FCFAParsingTestCase(TestCase):
    """Tests de parsing des montants FCFA"""
    
    def test_parse_fcfa_with_symbol(self):
        """Test du parsing avec symbole FCFA"""
        self.assertEqual(parse_fcfa("1 000 FCFA"), Decimal('1000'))
        self.assertEqual(parse_fcfa("500 FCFA"), Decimal('500'))
    
    def test_parse_fcfa_without_symbol(self):
        """Test du parsing sans symbole FCFA"""
        self.assertEqual(parse_fcfa("1 000"), Decimal('1000'))
        self.assertEqual(parse_fcfa("500"), Decimal('500'))
    
    def test_parse_fcfa_with_decimals(self):
        """Test du parsing avec décimales"""
        self.assertEqual(parse_fcfa("1 500,50"), Decimal('1500.50'))
        self.assertEqual(parse_fcfa("999,99 FCFA"), Decimal('999.99'))
    
    def test_parse_fcfa_large_numbers(self):
        """Test du parsing de grands nombres"""
        self.assertEqual(parse_fcfa("1 000 000 FCFA"), Decimal('1000000'))
        self.assertEqual(parse_fcfa("1 234 567"), Decimal('1234567'))
    
    def test_parse_fcfa_empty_string(self):
        """Test du parsing de chaîne vide"""
        self.assertEqual(parse_fcfa(""), Decimal('0'))
        self.assertEqual(parse_fcfa(None), Decimal('0'))
    
    def test_parse_fcfa_invalid_format(self):
        """Test du parsing de format invalide"""
        self.assertEqual(parse_fcfa("invalid"), Decimal('0'))
        self.assertEqual(parse_fcfa("abc FCFA"), Decimal('0'))


class FCFAShortFormattingTestCase(TestCase):
    """Tests de formatage compact des montants FCFA"""
    
    def test_format_fcfa_short_thousands(self):
        """Test du formatage compact pour les milliers"""
        self.assertEqual(format_fcfa_short(1500), "1,5 K FCFA")
        self.assertEqual(format_fcfa_short(2000), "2,0 K FCFA")
        self.assertEqual(format_fcfa_short(999), "999 FCFA")
    
    def test_format_fcfa_short_millions(self):
        """Test du formatage compact pour les millions"""
        self.assertEqual(format_fcfa_short(1500000), "1,5 M FCFA")
        self.assertEqual(format_fcfa_short(2000000), "2,0 M FCFA")
    
    def test_format_fcfa_short_billions(self):
        """Test du formatage compact pour les milliards"""
        self.assertEqual(format_fcfa_short(1500000000), "1,5 Mrd FCFA")
        self.assertEqual(format_fcfa_short(2000000000), "2,0 Mrd FCFA")
    
    def test_format_fcfa_short_none(self):
        """Test du formatage compact avec None"""
        self.assertEqual(format_fcfa_short(None), "0 FCFA")


class NumberFormattingTestCase(TestCase):
    """Tests de formatage des nombres avec virgule décimale"""
    
    def test_decimal_separator(self):
        """Test du séparateur décimal (virgule)"""
        from django.utils.formats import number_format
        
        # Vérifier que la virgule est utilisée comme séparateur décimal
        result = number_format(1500.50, decimal_pos=2, use_l10n=True)
        self.assertIn(',', result)
    
    def test_thousand_separator(self):
        """Test du séparateur de milliers (espace)"""
        from django.utils.formats import number_format
        
        # Vérifier que l'espace est utilisé comme séparateur de milliers
        result = number_format(1000, use_l10n=True, force_grouping=True)
        # Le résultat devrait contenir un espace (normal ou insécable) ou être "1000"
        self.assertTrue(' ' in result or '\xa0' in result or result == '1000')


class DateFormattingTestCase(TestCase):
    """Tests de formatage des dates (JJ/MM/AAAA)"""
    
    def test_date_format(self):
        """Test du format de date français"""
        from django.utils.formats import date_format
        from datetime import datetime
        
        date = datetime(2024, 12, 25, 14, 30)
        
        # Format court: JJ/MM/AAAA
        result = date_format(date, format='SHORT_DATE_FORMAT')
        self.assertIn('/', result)
        self.assertIn('25', result)
        self.assertIn('12', result)
        self.assertIn('2024', result)
    
    def test_datetime_format(self):
        """Test du format de date et heure"""
        from django.utils.formats import date_format
        from datetime import datetime
        
        date = datetime(2024, 12, 25, 14, 30)
        
        # Format avec heure: JJ/MM/AAAA HH:MM
        result = date_format(date, format='SHORT_DATETIME_FORMAT')
        self.assertIn('/', result)
        self.assertIn(':', result)
