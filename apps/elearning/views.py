from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q
from .models import (
    Categorie, Cours, Quiz, Question, Inscription,
    TentativeQuiz, ReponseUtilisateur, Commentaire
)
from .serializers import (
    CategorieSerializer, CoursListSerializer, CoursDetailSerializer,
    QuizSerializer, InscriptionSerializer, TentativeQuizSerializer,
    CommentaireSerializer
)

class CategorieViewSet(viewsets.ReadOnlyModelViewSet):
    """API pour les catégories de cours"""
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

class CoursViewSet(viewsets.ReadOnlyModelViewSet):
    """API pour les cours"""
    queryset = Cours.objects.filter(est_publie=True)
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['titre', 'description']
    ordering_fields = ['date_creation', 'vues', 'titre']
    ordering = ['-date_creation']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CoursDetailSerializer
        return CoursListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrer par catégorie
        categorie = self.request.query_params.get('categorie')
        if categorie:
            queryset = queryset.filter(categorie__slug=categorie)
        
        # Filtrer par type
        type_cours = self.request.query_params.get('type')
        if type_cours:
            queryset = queryset.filter(type_cours=type_cours)
        
        # Filtrer par niveau
        niveau = self.request.query_params.get('niveau')
        if niveau:
            queryset = queryset.filter(niveau=niveau)
        
        # Cours gratuits uniquement
        gratuit = self.request.query_params.get('gratuit')
        if gratuit == 'true':
            queryset = queryset.filter(est_gratuit=True)
        
        # Livestreams actifs
        livestream_actif = self.request.query_params.get('livestream_actif')
        if livestream_actif == 'true':
            now = timezone.now()
            queryset = queryset.filter(
                type_cours='LIVESTREAM',
                date_livestream__lte=now
            )
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Incrémenter les vues
        instance.vues += 1
        instance.save(update_fields=['vues'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def inscrire(self, request, slug=None):
        """Inscrire un utilisateur à un cours"""
        cours = self.get_object()
        
        # Vérifier si déjà inscrit
        if Inscription.objects.filter(utilisateur=request.user, cours=cours).exists():
            return Response(
                {'detail': 'Vous êtes déjà inscrit à ce cours'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Créer l'inscription
        inscription = Inscription.objects.create(
            utilisateur=request.user,
            cours=cours
        )
        
        serializer = InscriptionSerializer(inscription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def marquer_complete(self, request, slug=None):
        """Marquer un cours comme complété"""
        cours = self.get_object()
        inscription = get_object_or_404(Inscription, utilisateur=request.user, cours=cours)
        
        inscription.progression = 100
        inscription.est_complete = True
        inscription.date_completion = timezone.now()
        inscription.save()
        
        serializer = InscriptionSerializer(inscription)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def assister_livestream(self, request, slug=None):
        """Marquer la présence à un livestream"""
        cours = self.get_object()
        
        if cours.type_cours != 'LIVESTREAM':
            return Response(
                {'detail': 'Ce cours n\'est pas un livestream'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        inscription = get_object_or_404(Inscription, utilisateur=request.user, cours=cours)
        inscription.a_assiste_livestream = True
        inscription.save()
        
        return Response({'detail': 'Présence enregistrée'})
    
    @action(detail=True, methods=['get'])
    def quiz(self, request, slug=None):
        """Récupérer les quiz d'un cours"""
        cours = self.get_object()
        quiz = cours.quiz.filter(est_actif=True)
        serializer = QuizSerializer(quiz, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get', 'post'], permission_classes=[IsAuthenticated])
    def commentaires(self, request, slug=None):
        """Gérer les commentaires d'un cours"""
        cours = self.get_object()
        
        if request.method == 'GET':
            commentaires = cours.commentaires.all()
            serializer = CommentaireSerializer(commentaires, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = CommentaireSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(utilisateur=request.user, cours=cours)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """API pour les inscriptions de l'utilisateur"""
    serializer_class = InscriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Inscription.objects.filter(utilisateur=self.request.user)
    
    @action(detail=False, methods=['get'])
    def mes_cours(self, request):
        """Récupérer tous les cours de l'utilisateur"""
        inscriptions = self.get_queryset()
        serializer = self.get_serializer(inscriptions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def en_cours(self, request):
        """Cours en cours (non complétés)"""
        inscriptions = self.get_queryset().filter(est_complete=False)
        serializer = self.get_serializer(inscriptions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def completes(self, request):
        """Cours complétés"""
        inscriptions = self.get_queryset().filter(est_complete=True)
        serializer = self.get_serializer(inscriptions, many=True)
        return Response(serializer.data)

class QuizViewSet(viewsets.ReadOnlyModelViewSet):
    """API pour les quiz"""
    queryset = Quiz.objects.filter(est_actif=True)
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def commencer(self, request, pk=None):
        """Commencer une tentative de quiz"""
        quiz = self.get_object()
        
        # Créer une nouvelle tentative
        tentative = TentativeQuiz.objects.create(
            utilisateur=request.user,
            quiz=quiz
        )
        
        serializer = TentativeQuizSerializer(tentative)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def soumettre(self, request, pk=None):
        """Soumettre les réponses du quiz"""
        quiz = self.get_object()
        tentative_id = request.data.get('tentative_id')
        reponses = request.data.get('reponses', [])
        
        tentative = get_object_or_404(
            TentativeQuiz,
            id=tentative_id,
            utilisateur=request.user,
            quiz=quiz
        )
        
        # Calculer le score
        score_total = 0
        points_max = 0
        
        for reponse_data in reponses:
            question_id = reponse_data.get('question_id')
            choix_id = reponse_data.get('choix_id')
            
            question = get_object_or_404(Question, id=question_id, quiz=quiz)
            points_max += question.points
            
            if choix_id:
                choix = get_object_or_404(question.choix, id=choix_id)
                est_correct = choix.est_correct
                points = question.points if est_correct else 0
                
                ReponseUtilisateur.objects.create(
                    tentative=tentative,
                    question=question,
                    choix_selectionne=choix,
                    est_correct=est_correct,
                    points_obtenus=points
                )
                
                score_total += points
        
        # Mettre à jour la tentative
        tentative.score = score_total
        tentative.score_pourcentage = int((score_total / points_max) * 100) if points_max > 0 else 0
        tentative.est_reussi = tentative.score_pourcentage >= quiz.note_passage
        tentative.date_fin = timezone.now()
        tentative.save()
        
        serializer = TentativeQuizSerializer(tentative)
        return Response(serializer.data)
