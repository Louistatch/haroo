from rest_framework import viewsets, status, response, decorators, serializers as drf_serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer, MessageCreateSerializer
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(
            Q(participant_1=user) | Q(participant_2=user)
        ).select_related('participant_1', 'participant_2').prefetch_related('messages')

    def create(self, request, *args, **kwargs):
        participant_id = request.data.get('participant_id')
        type_relation = request.data.get('type_relation', 'GENERAL')
        reference_id = request.data.get('reference_id')

        if not participant_id:
            return response.Response({"detail": "participant_id est requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            participant_2 = User.objects.get(id=participant_id)
        except User.DoesNotExist:
            return response.Response({"detail": "Utilisateur non trouvé."}, status=status.HTTP_404_NOT_FOUND)

        participant_1 = request.user
        if participant_1 == participant_2:
            return response.Response({"detail": "Impossible de créer une conversation avec soi-même."}, status=status.HTTP_400_BAD_REQUEST)

        p1, p2 = (participant_1, participant_2) if participant_1.id < participant_2.id else (participant_2, participant_1)

        conversation, created = Conversation.objects.get_or_create(
            participant_1=p1, participant_2=p2,
            type_relation=type_relation, reference_id=reference_id
        )

        serializer = self.get_serializer(conversation)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        conversation_id = self.request.query_params.get('conversation')
        if not conversation_id:
            return Message.objects.none()
        user = self.request.user
        return Message.objects.filter(
            conversation_id=conversation_id,
            conversation__in=Conversation.objects.filter(Q(participant_1=user) | Q(participant_2=user))
        ).select_related('expediteur')

    def perform_create(self, serializer):
        conversation_id = self.request.data.get('conversation')
        if not conversation_id:
            raise drf_serializers.ValidationError("L'ID de la conversation est requis.")
        try:
            conversation = Conversation.objects.filter(
                Q(participant_1=self.request.user) | Q(participant_2=self.request.user),
                id=conversation_id
            ).get()
        except Conversation.DoesNotExist:
            raise drf_serializers.ValidationError("Conversation inexistante ou accès refusé.")

        fichier = self.request.FILES.get('fichier')
        extra = {}
        if fichier:
            if fichier.size > Message.MAX_FILE_SIZE:
                raise drf_serializers.ValidationError("Le fichier ne doit pas dépasser 5 Mo.")
            extra['fichier'] = fichier
            extra['nom_fichier'] = fichier.name
            extra['taille_fichier'] = fichier.size

        serializer.save(expediteur=self.request.user, conversation=conversation, **extra)
        conversation.derniere_activite = timezone.now()
        conversation.save()

    @decorators.action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        try:
            message = Message.objects.get(
                pk=pk,
                conversation__in=Conversation.objects.filter(Q(participant_1=request.user) | Q(participant_2=request.user))
            )
            if message.expediteur != request.user and not message.lu:
                message.lu = True
                message.date_lecture = timezone.now()
                message.save()
            return response.Response({'status': 'message lu'})
        except Message.DoesNotExist:
            return response.Response(status=status.HTTP_404_NOT_FOUND)

    @decorators.action(detail=False, methods=['post'], url_path='mark-conversation-read')
    def mark_conversation_read(self, request):
        conversation_id = request.data.get('conversation_id')
        if not conversation_id:
            return response.Response({"detail": "conversation_id requis."}, status=status.HTTP_400_BAD_REQUEST)
        messages = Message.objects.filter(
            conversation_id=conversation_id, lu=False,
            conversation__in=Conversation.objects.filter(Q(participant_1=request.user) | Q(participant_2=request.user))
        ).exclude(expediteur=request.user)
        count = messages.update(lu=True, date_lecture=timezone.now())
        return response.Response({'status': f'{count} messages marqués comme lus'})

    @decorators.action(detail=True, methods=['post'], url_path='report')
    def report(self, request, pk=None):
        """Signaler un message comme inapproprié."""
        try:
            message = Message.objects.get(
                pk=pk,
                conversation__in=Conversation.objects.filter(Q(participant_1=request.user) | Q(participant_2=request.user))
            )
        except Message.DoesNotExist:
            return response.Response(status=status.HTTP_404_NOT_FOUND)

        if message.expediteur == request.user:
            return response.Response({"detail": "Vous ne pouvez pas signaler votre propre message."}, status=status.HTTP_400_BAD_REQUEST)

        motif = request.data.get('motif', '')
        message.signale = True
        message.motif_signalement = motif[:255]
        message.save()
        return response.Response({'status': 'Message signalé avec succès.'})
