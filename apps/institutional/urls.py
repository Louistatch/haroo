"""
URLs pour le dashboard institutionnel
"""
from django.urls import path
from . import views

app_name = 'institutional'

urlpatterns = [
    # Dashboard principal avec tous les indicateurs
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Statistiques agrégées uniquement
    path('statistics/aggregated/', views.aggregated_statistics_view, name='aggregated-statistics'),
    
    # Statistiques par préfecture
    path('statistics/by-prefecture/', views.statistics_by_prefecture_view, name='statistics-by-prefecture'),
    
    # Répartition des transactions
    path('statistics/transactions/', views.transaction_breakdown_view, name='transaction-breakdown'),
    
    # Tendances mensuelles
    path('statistics/trends/', views.monthly_trends_view, name='monthly-trends'),
    
    # Export de rapports anonymisés (Excel/PDF)
    path('reports/export/', views.export_report_view, name='export-report'),
]
