"""
Vues pour le dashboard institutionnel
Exigences: 25.1, 25.2, 25.3, 25.4
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .services import InstitutionalDashboardService
from .serializers import (
    DashboardQuerySerializer,
    AggregatedStatisticsSerializer,
    PrefectureStatisticsSerializer,
    TransactionBreakdownSerializer,
    MonthlyTrendSerializer
)
from .permissions import IsInstitutionalUser


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsInstitutionalUser])
def dashboard_view(request):
    """
    GET /api/v1/institutional/dashboard
    
    Retourne les statistiques du dashboard institutionnel avec filtres optionnels
    
    Query Parameters:
        - region (int, optionnel): ID de la région pour filtrer
        - start_date (datetime, optionnel): Date de début de la période
        - end_date (datetime, optionnel): Date de fin de la période
    
    Exigences: 25.3, 25.4
    """
    # Valider les paramètres de requête
    query_serializer = DashboardQuerySerializer(data=request.query_params)
    if not query_serializer.is_valid():
        return Response(
            {'errors': query_serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    validated_data = query_serializer.validated_data
    region_id = validated_data.get('region')
    start_date = validated_data.get('start_date')
    end_date = validated_data.get('end_date')
    
    # Vérifier les permissions d'accès à la région
    user = request.user
    if hasattr(user, 'institution_profile'):
        institution_profile = user.institution_profile
        
        # Si l'institution a un niveau d'accès régional, vérifier l'accès
        if institution_profile.niveau_acces == 'REGIONAL':
            allowed_regions = institution_profile.regions_acces.values_list('id', flat=True)
            if region_id and region_id not in allowed_regions:
                return Response(
                    {'error': 'Vous n\'avez pas accès aux données de cette région'},
                    status=status.HTTP_403_FORBIDDEN
                )
            # Si aucune région spécifiée, limiter aux régions autorisées
            if not region_id and allowed_regions:
                # Pour simplifier, on prend la première région autorisée
                region_id = allowed_regions[0] if allowed_regions else None
    
    # Obtenir les statistiques agrégées
    statistics = InstitutionalDashboardService.get_aggregated_statistics(
        region_id=region_id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Obtenir les statistiques par région
    statistics_by_region = InstitutionalDashboardService.get_statistics_by_region(
        start_date=start_date,
        end_date=end_date
    )
    
    # Obtenir la répartition des transactions
    transaction_breakdown = InstitutionalDashboardService.get_transaction_breakdown(
        region_id=region_id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Sérialiser les données
    response_data = {
        'statistiques_globales': statistics,
        'statistiques_par_region': statistics_by_region,
        'repartition_transactions': transaction_breakdown,
        'filtres_appliques': {
            'region_id': region_id,
            'start_date': start_date.isoformat() if start_date else None,
            'end_date': end_date.isoformat() if end_date else None
        }
    }
    
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsInstitutionalUser])
def aggregated_statistics_view(request):
    """
    GET /api/v1/institutional/statistics/aggregated
    
    Retourne uniquement les statistiques agrégées
    
    Query Parameters:
        - region (int, optionnel): ID de la région pour filtrer
        - start_date (datetime, optionnel): Date de début de la période
        - end_date (datetime, optionnel): Date de fin de la période
    
    Exigences: 25.3
    """
    # Valider les paramètres de requête
    query_serializer = DashboardQuerySerializer(data=request.query_params)
    if not query_serializer.is_valid():
        return Response(
            {'errors': query_serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    validated_data = query_serializer.validated_data
    region_id = validated_data.get('region')
    start_date = validated_data.get('start_date')
    end_date = validated_data.get('end_date')
    
    # Obtenir les statistiques
    statistics = InstitutionalDashboardService.get_aggregated_statistics(
        region_id=region_id,
        start_date=start_date,
        end_date=end_date
    )
    
    serializer = AggregatedStatisticsSerializer(statistics)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsInstitutionalUser])
def statistics_by_prefecture_view(request):
    """
    GET /api/v1/institutional/statistics/by-prefecture
    
    Retourne les statistiques par préfecture
    
    Query Parameters:
        - region (int, optionnel): ID de la région pour filtrer
        - start_date (datetime, optionnel): Date de début de la période
        - end_date (datetime, optionnel): Date de fin de la période
    
    Exigences: 25.4
    """
    # Valider les paramètres de requête
    query_serializer = DashboardQuerySerializer(data=request.query_params)
    if not query_serializer.is_valid():
        return Response(
            {'errors': query_serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    validated_data = query_serializer.validated_data
    region_id = validated_data.get('region')
    start_date = validated_data.get('start_date')
    end_date = validated_data.get('end_date')
    
    # Obtenir les statistiques par préfecture
    statistics = InstitutionalDashboardService.get_statistics_by_prefecture(
        region_id=region_id,
        start_date=start_date,
        end_date=end_date
    )
    
    serializer = PrefectureStatisticsSerializer(statistics, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsInstitutionalUser])
def transaction_breakdown_view(request):
    """
    GET /api/v1/institutional/statistics/transactions
    
    Retourne la répartition des transactions par type
    
    Query Parameters:
        - region (int, optionnel): ID de la région pour filtrer
        - start_date (datetime, optionnel): Date de début de la période
        - end_date (datetime, optionnel): Date de fin de la période
    
    Exigences: 25.3
    """
    # Valider les paramètres de requête
    query_serializer = DashboardQuerySerializer(data=request.query_params)
    if not query_serializer.is_valid():
        return Response(
            {'errors': query_serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    validated_data = query_serializer.validated_data
    region_id = validated_data.get('region')
    start_date = validated_data.get('start_date')
    end_date = validated_data.get('end_date')
    
    # Obtenir la répartition des transactions
    breakdown = InstitutionalDashboardService.get_transaction_breakdown(
        region_id=region_id,
        start_date=start_date,
        end_date=end_date
    )
    
    serializer = TransactionBreakdownSerializer(breakdown, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsInstitutionalUser])
def monthly_trends_view(request):
    """
    GET /api/v1/institutional/statistics/trends
    
    Retourne les tendances mensuelles
    
    Query Parameters:
        - region (int, optionnel): ID de la région pour filtrer
        - months (int, optionnel): Nombre de mois à inclure (défaut: 12, max: 24)
    
    Exigences: 25.3
    """
    # Valider les paramètres de requête
    query_serializer = DashboardQuerySerializer(data=request.query_params)
    if not query_serializer.is_valid():
        return Response(
            {'errors': query_serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    validated_data = query_serializer.validated_data
    region_id = validated_data.get('region')
    months = validated_data.get('months', 12)
    
    # Obtenir les tendances mensuelles
    trends = InstitutionalDashboardService.get_monthly_trends(
        region_id=region_id,
        months=months
    )
    
    serializer = MonthlyTrendSerializer(trends, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated, IsInstitutionalUser])
def export_report_view(request):
    """
    POST /api/v1/institutional/reports/export
    
    Génère et exporte un rapport statistique anonymisé au format Excel ou PDF
    
    Body Parameters:
        - format (str, requis): Format d'export ('excel' ou 'pdf')
        - region (int, optionnel): ID de la région pour filtrer
        - start_date (datetime, optionnel): Date de début de la période
        - end_date (datetime, optionnel): Date de fin de la période
        - include_regions (bool, optionnel): Inclure les statistiques par région (défaut: true)
        - include_transactions (bool, optionnel): Inclure la répartition des transactions (défaut: true)
    
    Exigences: 25.5, 25.6
    """
    from django.http import HttpResponse
    from .services import DataAnonymizationService, ReportGenerationService
    
    # Valider le format d'export
    export_format = request.data.get('format', 'excel').lower()
    if export_format not in ['excel', 'pdf']:
        return Response(
            {'error': 'Format d\'export invalide. Utilisez "excel" ou "pdf".'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Valider les paramètres de requête
    query_serializer = DashboardQuerySerializer(data=request.data)
    if not query_serializer.is_valid():
        return Response(
            {'errors': query_serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    validated_data = query_serializer.validated_data
    region_id = validated_data.get('region')
    start_date = validated_data.get('start_date')
    end_date = validated_data.get('end_date')
    
    # Options d'export
    include_regions = request.data.get('include_regions', True)
    include_transactions = request.data.get('include_transactions', True)
    
    # Vérifier les permissions d'accès à la région
    user = request.user
    if hasattr(user, 'institution_profile'):
        institution_profile = user.institution_profile
        
        if institution_profile.niveau_acces == 'REGIONAL':
            allowed_regions = institution_profile.regions_acces.values_list('id', flat=True)
            if region_id and region_id not in allowed_regions:
                return Response(
                    {'error': 'Vous n\'avez pas accès aux données de cette région'},
                    status=status.HTTP_403_FORBIDDEN
                )
    
    # Collecter les données statistiques
    statistics_data = {}
    
    # Statistiques globales
    statistics_data['statistiques_globales'] = InstitutionalDashboardService.get_aggregated_statistics(
        region_id=region_id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Statistiques par région (si demandé)
    if include_regions:
        statistics_data['statistiques_par_region'] = InstitutionalDashboardService.get_statistics_by_region(
            start_date=start_date,
            end_date=end_date
        )
    
    # Répartition des transactions (si demandé)
    if include_transactions:
        statistics_data['repartition_transactions'] = InstitutionalDashboardService.get_transaction_breakdown(
            region_id=region_id,
            start_date=start_date,
            end_date=end_date
        )
    
    # Filtres appliqués
    statistics_data['filtres_appliques'] = {
        'region_id': region_id,
        'start_date': start_date.isoformat() if start_date else None,
        'end_date': end_date.isoformat() if end_date else None
    }
    
    # Anonymiser les données
    anonymized_data = DataAnonymizationService.prepare_export_data(statistics_data)
    
    # Générer le rapport selon le format
    try:
        if export_format == 'excel':
            file_buffer = ReportGenerationService.generate_excel_report(anonymized_data)
            filename = f'rapport_statistiques_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        else:  # pdf
            file_buffer = ReportGenerationService.generate_pdf_report(anonymized_data)
            filename = f'rapport_statistiques_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            content_type = 'application/pdf'
        
        # Créer la réponse HTTP avec le fichier
        response = HttpResponse(
            file_buffer.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de la génération du rapport: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
