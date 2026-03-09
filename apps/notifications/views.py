from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification, PreferenceNotification
from .serializers import NotificationSerializer, PreferenceSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # On retourne les notifications non lues + les 20 plus récentes
        return Notification.objects.filter(utilisateur=self.request.user).order_by('-lue', '-created_at')[:20]

    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.lue = True
        notification.save()
        return Response({'status': 'notification marquée comme lue'})

    @action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request):
        Notification.objects.filter(utilisateur=self.request.user, lue=False).update(lue=True)
        return Response({'status': 'toutes les notifications ont été marquées comme lues'})

    @action(detail=False, methods=['get'])
    def count(self, request):
        unread_count = Notification.objects.filter(utilisateur=self.request.user, lue=False).count()
        return Response({'unread_count': unread_count})

class PreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = PreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PreferenceNotification.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
