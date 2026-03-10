"""
Dashboard administrateur — API endpoints
GET /api/v1/admin/dashboard — Stats globales
GET /api/v1/admin/users — Liste/recherche utilisateurs
POST /api/v1/admin/users/{id}/suspend — Suspendre un compte
POST /api/v1/admin/users/{id}/activate — Réactiver un compte
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Avg, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


def is_admin(user):
    return user.is_staff or user.user_type == 'ADMIN'


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard(request):
    """Stats globales pour le dashboard admin."""
    if not is_admin(request.user):
        return Response({'detail': 'Accès réservé aux administrateurs.'}, status=status.HTTP_403_FORBIDDEN)

    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    seven_days_ago = now - timedelta(days=7)

    # --- Utilisateurs ---
    total_users = User.objects.count()
    users_by_type = dict(
        User.objects.values_list('user_type').annotate(c=Count('id')).values_list('user_type', 'c')
    )
    new_users_30d = User.objects.filter(date_joined__gte=thirty_days_ago).count()
    new_users_7d = User.objects.filter(date_joined__gte=seven_days_ago).count()

    # Inscriptions par jour (30 derniers jours)
    signups_daily = list(
        User.objects.filter(date_joined__gte=thirty_days_ago)
        .annotate(date=TruncDate('date_joined'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
        .values('date', 'count')
    )

    # --- Missions ---
    missions_stats = {}
    try:
        from apps.missions.models import Mission
        missions_stats = {
            'total': Mission.objects.count(),
            'en_cours': Mission.objects.filter(statut='EN_COURS').count(),
            'terminees': Mission.objects.filter(statut='TERMINEE').count(),
            'en_attente': Mission.objects.filter(statut='DEMANDE').count(),
        }
    except Exception:
        pass

    # --- Jobs ---
    jobs_stats = {}
    try:
        from apps.jobs.models import AnnonceCollective
        jobs_stats = {
            'total': AnnonceCollective.objects.count(),
            'publiees': AnnonceCollective.objects.filter(statut='VALIDEE').count(),
            'en_attente': AnnonceCollective.objects.filter(statut='EN_ATTENTE').count(),
        }
    except Exception:
        pass

    # --- Préventes ---
    presales_stats = {}
    try:
        from apps.presales.models import PreventeAgricole
        presales_stats = {
            'total': PreventeAgricole.objects.count(),
            'actives': PreventeAgricole.objects.filter(statut='DISPONIBLE').count(),
        }
    except Exception:
        pass

    # --- Paiements ---
    payments_stats = {}
    try:
        from apps.payments.models import Transaction
        total_tx = Transaction.objects.count()
        tx_completed = Transaction.objects.filter(statut='SUCCESS')
        payments_stats = {
            'total_transactions': total_tx,
            'completed': tx_completed.count(),
            'volume_total': float(tx_completed.aggregate(s=Sum('montant'))['s'] or 0),
        }
    except Exception:
        pass

    # --- Ratings / Modération ---
    moderation_stats = {}
    try:
        from apps.ratings.models import Notation
        moderation_stats = {
            'total_notations': Notation.objects.count(),
            'signalees': Notation.objects.filter(statut='SIGNALE').count(),
            'note_moyenne_globale': round(float(Notation.objects.filter(statut='PUBLIE').aggregate(a=Avg('note_valeur'))['a'] or 0), 2),
        }
    except Exception:
        pass

    # --- Messages ---
    messaging_stats = {}
    try:
        from apps.messaging.models import Conversation, Message
        messaging_stats = {
            'total_conversations': Conversation.objects.count(),
            'total_messages': Message.objects.count(),
            'messages_signales': Message.objects.filter(signale=True).count(),
        }
    except Exception:
        pass

    # --- Notifications ---
    notif_stats = {}
    try:
        from apps.notifications.models import Notification
        notif_stats = {
            'total': Notification.objects.count(),
            'non_lues': Notification.objects.filter(lue=False).count(),
        }
    except Exception:
        pass

    return Response({
        'utilisateurs': {
            'total': total_users,
            'par_type': users_by_type,
            'nouveaux_30j': new_users_30d,
            'nouveaux_7j': new_users_7d,
            'inscriptions_quotidiennes': [
                {'date': str(d['date']), 'count': d['count']} for d in signups_daily
            ],
        },
        'missions': missions_stats,
        'emplois': jobs_stats,
        'preventes': presales_stats,
        'paiements': payments_stats,
        'moderation': moderation_stats,
        'messagerie': messaging_stats,
        'notifications': notif_stats,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_users(request):
    """Liste des utilisateurs avec recherche et filtres."""
    if not is_admin(request.user):
        return Response({'detail': 'Accès réservé aux administrateurs.'}, status=status.HTTP_403_FORBIDDEN)

    qs = User.objects.all().order_by('-date_joined')

    # Filtres
    search = request.query_params.get('search', '').strip()
    if search:
        qs = qs.filter(
            Q(first_name__icontains=search) | Q(last_name__icontains=search) |
            Q(email__icontains=search) | Q(phone_number__icontains=search) |
            Q(username__icontains=search)
        )

    user_type = request.query_params.get('user_type')
    if user_type:
        qs = qs.filter(user_type=user_type)

    is_active = request.query_params.get('is_active')
    if is_active is not None:
        qs = qs.filter(is_active=is_active.lower() == 'true')

    # Pagination simple
    page = int(request.query_params.get('page', 1))
    per_page = 50
    total = qs.count()
    users = qs[(page - 1) * per_page: page * per_page]

    data = [{
        'id': u.id,
        'username': u.username,
        'first_name': u.first_name,
        'last_name': u.last_name,
        'email': u.email,
        'phone_number': u.phone_number,
        'user_type': u.user_type,
        'is_active': u.is_active,
        'date_joined': u.date_joined.isoformat(),
    } for u in users]

    return Response({'total': total, 'page': page, 'per_page': per_page, 'results': data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_suspend_user(request, user_id):
    """Suspendre un compte utilisateur."""
    if not is_admin(request.user):
        return Response({'detail': 'Accès réservé aux administrateurs.'}, status=status.HTTP_403_FORBIDDEN)

    justification = request.data.get('justification', '').strip()
    if not justification:
        return Response({'detail': 'Une justification est requise.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'detail': 'Utilisateur non trouvé.'}, status=status.HTTP_404_NOT_FOUND)

    if user == request.user:
        return Response({'detail': 'Vous ne pouvez pas vous suspendre vous-même.'}, status=status.HTTP_400_BAD_REQUEST)

    user.is_active = False
    user.save()
    return Response({'status': 'Compte suspendu.', 'user_id': user.id})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_activate_user(request, user_id):
    """Réactiver un compte utilisateur."""
    if not is_admin(request.user):
        return Response({'detail': 'Accès réservé aux administrateurs.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'detail': 'Utilisateur non trouvé.'}, status=status.HTTP_404_NOT_FOUND)

    user.is_active = True
    user.save()
    return Response({'status': 'Compte réactivé.', 'user_id': user.id})
