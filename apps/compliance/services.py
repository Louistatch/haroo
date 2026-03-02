"""
Services pour la conformité réglementaire
Exigences: 45.1, 45.2, 45.3, 45.4, 45.5, 45.6, 33.6
"""
import json
from datetime import datetime, timedelta
from decimal import Decimal
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from .models import (
    CGUAcceptance,
    ElectronicReceipt,
    DataRetentionPolicy,
    AccountDeletionRequest
)


class CGUService:
    """
    Service pour la gestion des CGU
    Exigence: 45.2, 45.3
    """
    
    CURRENT_CGU_VERSION = "1.0"
    
    @staticmethod
    def record_acceptance(user, ip_address, user_agent, version=None):
        """
        Enregistre l'acceptation des CGU par un utilisateur
        Exigence: 45.3
        """
        if version is None:
            version = CGUService.CURRENT_CGU_VERSION
        
        acceptance = CGUAcceptance.objects.create(
            user=user,
            version_cgu=version,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return acceptance
    
    @staticmethod
    def has_accepted_current_version(user):
        """
        Vérifie si l'utilisateur a accepté la version actuelle des CGU
        """
        return CGUAcceptance.objects.filter(
            user=user,
            version_cgu=CGUService.CURRENT_CGU_VERSION
        ).exists()
    
    @staticmethod
    def get_user_acceptances(user):
        """
        Récupère l'historique des acceptations CGU d'un utilisateur
        """
        return CGUAcceptance.objects.filter(user=user).order_by('-accepted_at')


class ReceiptService:
    """
    Service pour la génération de reçus électroniques
    Exigence: 45.5
    """
    
    @staticmethod
    def generate_receipt_number():
        """
        Génère un numéro de reçu unique
        Format: REC-YYYY-NNNNN
        """
        year = datetime.now().year
        last_receipt = ElectronicReceipt.objects.filter(
            receipt_number__startswith=f'REC-{year}-'
        ).order_by('-receipt_number').first()
        
        if last_receipt:
            last_number = int(last_receipt.receipt_number.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f'REC-{year}-{new_number:05d}'
    
    @staticmethod
    def create_receipt(transaction_obj):
        """
        Crée un reçu électronique pour une transaction
        Exigence: 45.5
        """
        # Vérifier si un reçu existe déjà
        if hasattr(transaction_obj, 'receipt'):
            return transaction_obj.receipt
        
        user = transaction_obj.utilisateur
        receipt_number = ReceiptService.generate_receipt_number()
        
        # Calculer les montants (TVA à 18% au Togo)
        amount = transaction_obj.montant
        tax_rate = Decimal('0.18')
        tax_amount = amount * tax_rate
        total_amount = amount + tax_amount
        
        receipt = ElectronicReceipt.objects.create(
            transaction=transaction_obj,
            receipt_number=receipt_number,
            buyer_name=user.get_full_name() or user.username,
            buyer_phone=user.phone_number,
            description=transaction_obj.get_type_transaction_display(),
            amount=amount,
            tax_amount=tax_amount,
            total_amount=total_amount
        )
        
        # Générer le PDF
        pdf_content = ReceiptService._generate_pdf(receipt)
        receipt.pdf_file.save(
            f'{receipt_number}.pdf',
            ContentFile(pdf_content),
            save=True
        )
        
        return receipt
    
    @staticmethod
    def _generate_pdf(receipt):
        """
        Génère le PDF du reçu
        """
        from io import BytesIO
        buffer = BytesIO()
        
        # Créer le document PDF
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        # Contenu
        story = []
        
        # Titre
        story.append(Paragraph("REÇU ÉLECTRONIQUE", title_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Informations de la plateforme
        story.append(Paragraph("<b>Plateforme Agricole Intelligente du Togo</b>", styles['Normal']))
        story.append(Paragraph("Lomé, Togo", styles['Normal']))
        story.append(Spacer(1, 0.5*cm))
        
        # Numéro de reçu et date
        story.append(Paragraph(f"<b>Numéro de reçu:</b> {receipt.receipt_number}", styles['Normal']))
        story.append(Paragraph(
            f"<b>Date d'émission:</b> {receipt.issued_at.strftime('%d/%m/%Y %H:%M')}",
            styles['Normal']
        ))
        story.append(Spacer(1, 1*cm))
        
        # Informations client
        story.append(Paragraph("<b>INFORMATIONS CLIENT</b>", styles['Heading2']))
        story.append(Paragraph(f"Nom: {receipt.buyer_name}", styles['Normal']))
        story.append(Paragraph(f"Téléphone: {receipt.buyer_phone}", styles['Normal']))
        story.append(Spacer(1, 1*cm))
        
        # Détails de la transaction
        story.append(Paragraph("<b>DÉTAILS DE LA TRANSACTION</b>", styles['Heading2']))
        story.append(Paragraph(f"Description: {receipt.description}", styles['Normal']))
        story.append(Spacer(1, 0.5*cm))
        
        # Tableau des montants
        data = [
            ['Description', 'Montant'],
            ['Montant HT', f'{receipt.amount:,.2f} FCFA'],
            ['TVA (18%)', f'{receipt.tax_amount:,.2f} FCFA'],
            ['<b>Total TTC</b>', f'<b>{receipt.total_amount:,.2f} FCFA</b>'],
        ]
        
        table = Table(data, colWidths=[10*cm, 5*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 1*cm))
        
        # Pied de page
        story.append(Paragraph(
            "<i>Ce reçu électronique est conforme à la réglementation togolaise.</i>",
            styles['Normal']
        ))
        story.append(Paragraph(
            f"<i>ID Transaction: {receipt.transaction.id}</i>",
            styles['Normal']
        ))
        
        # Construire le PDF
        doc.build(story)
        
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content


class DataExportService:
    """
    Service pour l'export des données personnelles
    Exigence: 33.6
    """
    
    @staticmethod
    def export_user_data(user):
        """
        Exporte toutes les données personnelles d'un utilisateur au format JSON
        Exigence: 33.6
        """
        data = {
            'user_info': {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone_number': user.phone_number,
                'user_type': user.user_type,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
            },
            'profile': DataExportService._get_profile_data(user),
            'transactions': DataExportService._get_transactions_data(user),
            'cgu_acceptances': DataExportService._get_cgu_data(user),
            'export_date': timezone.now().isoformat(),
        }
        
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    @staticmethod
    def _get_profile_data(user):
        """Récupère les données de profil selon le type d'utilisateur"""
        profile_data = {}
        
        if user.user_type == 'EXPLOITANT' and hasattr(user, 'exploitant_profile'):
            profile = user.exploitant_profile
            profile_data = {
                'type': 'Exploitant',
                'superficie_totale': str(profile.superficie_totale),
                'canton_principal': profile.canton_principal.nom,
                'statut_verification': profile.statut_verification,
                'cultures_actuelles': profile.cultures_actuelles,
            }
        elif user.user_type == 'AGRONOME' and hasattr(user, 'agronome_profile'):
            profile = user.agronome_profile
            profile_data = {
                'type': 'Agronome',
                'canton_rattachement': profile.canton_rattachement.nom,
                'specialisations': profile.specialisations,
                'statut_validation': profile.statut_validation,
                'note_moyenne': str(profile.note_moyenne),
                'nombre_avis': profile.nombre_avis,
            }
        elif user.user_type == 'OUVRIER' and hasattr(user, 'ouvrier_profile'):
            profile = user.ouvrier_profile
            profile_data = {
                'type': 'Ouvrier',
                'competences': profile.competences,
                'note_moyenne': str(profile.note_moyenne),
                'nombre_avis': profile.nombre_avis,
                'disponible': profile.disponible,
            }
        elif user.user_type == 'ACHETEUR' and hasattr(user, 'acheteur_profile'):
            profile = user.acheteur_profile
            profile_data = {
                'type': 'Acheteur',
                'type_acheteur': profile.type_acheteur,
                'volume_achats_annuel': str(profile.volume_achats_annuel) if profile.volume_achats_annuel else None,
            }
        elif user.user_type == 'INSTITUTION' and hasattr(user, 'institution_profile'):
            profile = user.institution_profile
            profile_data = {
                'type': 'Institution',
                'nom_organisme': profile.nom_organisme,
                'niveau_acces': profile.niveau_acces,
            }
        
        return profile_data
    
    @staticmethod
    def _get_transactions_data(user):
        """Récupère l'historique des transactions"""
        from apps.payments.models import Transaction
        
        transactions = Transaction.objects.filter(utilisateur=user)
        return [
            {
                'id': str(t.id),
                'type': t.type_transaction,
                'montant': str(t.montant),
                'statut': t.statut,
                'date': t.created_at.isoformat(),
            }
            for t in transactions
        ]
    
    @staticmethod
    def _get_cgu_data(user):
        """Récupère l'historique des acceptations CGU"""
        acceptances = CGUAcceptance.objects.filter(user=user)
        return [
            {
                'version': a.version_cgu,
                'date': a.accepted_at.isoformat(),
                'ip_address': a.ip_address,
            }
            for a in acceptances
        ]


class AccountDeletionService:
    """
    Service pour la suppression de compte
    Exigence: 45.4
    """
    
    @staticmethod
    @transaction.atomic
    def request_deletion(user, reason=''):
        """
        Crée une demande de suppression de compte
        Exigence: 45.4
        """
        # Vérifier s'il existe déjà une demande en attente
        existing_request = AccountDeletionRequest.objects.filter(
            user=user,
            status__in=['PENDING', 'PROCESSING']
        ).first()
        
        if existing_request:
            return existing_request
        
        # Créer la demande
        deletion_request = AccountDeletionRequest.objects.create(
            user=user,
            reason=reason,
            status='PENDING'
        )
        
        # Générer l'export des données
        data_json = DataExportService.export_user_data(user)
        deletion_request.data_export_file.save(
            f'user_{user.id}_data_export.json',
            ContentFile(data_json.encode('utf-8')),
            save=True
        )
        
        return deletion_request
    
    @staticmethod
    @transaction.atomic
    def process_deletion(deletion_request, admin_user):
        """
        Traite une demande de suppression de compte
        Exigence: 45.4
        """
        if deletion_request.status != 'PENDING':
            raise ValueError("Cette demande a déjà été traitée")
        
        deletion_request.status = 'PROCESSING'
        deletion_request.save()
        
        user = deletion_request.user
        
        # Anonymiser les données au lieu de les supprimer complètement
        # (pour respecter la rétention des transactions)
        user.username = f'deleted_user_{user.id}'
        user.email = f'deleted_{user.id}@deleted.local'
        user.first_name = 'Utilisateur'
        user.last_name = 'Supprimé'
        user.phone_number = f'+00000000{user.id}'
        user.is_active = False
        user.save()
        
        # Marquer la demande comme terminée
        deletion_request.status = 'COMPLETED'
        deletion_request.processed_at = timezone.now()
        deletion_request.processed_by = admin_user
        deletion_request.save()
        
        return deletion_request


class DataRetentionService:
    """
    Service pour la gestion de la rétention des données
    Exigence: 45.6
    """
    
    @staticmethod
    def initialize_policies():
        """
        Initialise les politiques de rétention par défaut
        Exigence: 45.6
        """
        policies = [
            {
                'data_type': 'TRANSACTION',
                'retention_period_days': 3650,  # 10 ans
                'description': 'Données de transaction conservées pendant 10 ans pour conformité fiscale togolaise'
            },
            {
                'data_type': 'USER_DATA',
                'retention_period_days': 1825,  # 5 ans
                'description': 'Données utilisateur conservées pendant 5 ans après suppression du compte'
            },
            {
                'data_type': 'LOGS',
                'retention_period_days': 90,  # 90 jours
                'description': 'Logs système conservés pendant 90 jours'
            },
            {
                'data_type': 'DOCUMENTS',
                'retention_period_days': 1825,  # 5 ans
                'description': 'Documents uploadés conservés pendant 5 ans'
            },
        ]
        
        for policy_data in policies:
            DataRetentionPolicy.objects.get_or_create(
                data_type=policy_data['data_type'],
                defaults={
                    'retention_period_days': policy_data['retention_period_days'],
                    'description': policy_data['description'],
                    'is_active': True
                }
            )
    
    @staticmethod
    def get_retention_period(data_type):
        """
        Récupère la période de rétention pour un type de données
        """
        try:
            policy = DataRetentionPolicy.objects.get(
                data_type=data_type,
                is_active=True
            )
            return policy.retention_period_days
        except DataRetentionPolicy.DoesNotExist:
            return None
    
    @staticmethod
    def should_retain_transaction(transaction_date):
        """
        Vérifie si une transaction doit être conservée
        Exigence: 45.6 - Conservation 10 ans
        """
        retention_days = DataRetentionService.get_retention_period('TRANSACTION')
        if retention_days is None:
            retention_days = 3650  # 10 ans par défaut
        
        cutoff_date = timezone.now() - timedelta(days=retention_days)
        return transaction_date >= cutoff_date
