from rest_framework import serializers
from .models import (
    Categorie, Cours, Quiz, Question, ChoixReponse,
    Inscription, TentativeQuiz, ReponseUtilisateur, Commentaire
)
from django.contrib.auth import get_user_model

User = get_user_model()

class CategorieSerializer(serializers.ModelSerializer):
    nombre_cours = serializers.SerializerMethodField()
    
    class Meta:
        model = Categorie
        fields = ['id', 'nom', 'slug', 'description', 'icone', 'ordre', 'nombre_cours']
    
    def get_nombre_cours(self, obj):
        return obj.cours.filter(est_publie=True).count()

class InstructeurSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class CoursListSerializer(serializers.ModelSerializer):
    categorie_nom = serializers.CharField(source='categorie.nom', read_only=True)
    instructeur_nom = serializers.SerializerMethodField()
    nombre_inscrits = serializers.SerializerMethodField()
    est_inscrit = serializers.SerializerMethodField()
    est_livestream_actif = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Cours
        fields = [
            'id', 'titre', 'slug', 'description', 'type_cours', 'categorie', 'categorie_nom',
            'niveau', 'youtube_url', 'youtube_video_id', 'google_meet_url', 'date_livestream',
            'duree_minutes', 'duree_livestream_minutes', 'instructeur', 'instructeur_nom',
            'thumbnail', 'est_gratuit', 'prix', 'vues', 'nombre_inscrits', 'est_inscrit',
            'est_livestream_actif', 'date_creation'
        ]
    
    def get_instructeur_nom(self, obj):
        if obj.instructeur:
            return f"{obj.instructeur.first_name} {obj.instructeur.last_name}".strip() or obj.instructeur.username
        return "Haroo"
    
    def get_nombre_inscrits(self, obj):
        return obj.inscriptions.count()
    
    def get_est_inscrit(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.inscriptions.filter(utilisateur=request.user).exists()
        return False


class CoursDetailSerializer(serializers.ModelSerializer):
    categorie = CategorieSerializer(read_only=True)
    instructeur = InstructeurSerializer(read_only=True)
    nombre_inscrits = serializers.SerializerMethodField()
    est_inscrit = serializers.SerializerMethodField()
    ma_progression = serializers.SerializerMethodField()
    est_livestream_actif = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Cours
        fields = [
            'id', 'titre', 'slug', 'description', 'type_cours', 'categorie', 'niveau',
            'youtube_url', 'youtube_video_id', 'google_meet_url', 'date_livestream',
            'duree_minutes', 'duree_livestream_minutes', 'instructeur', 'thumbnail',
            'est_gratuit', 'prix', 'transcription', 'resume_ai', 'vues',
            'nombre_inscrits', 'est_inscrit', 'ma_progression', 'est_livestream_actif',
            'date_creation', 'date_modification'
        ]
    
    def get_nombre_inscrits(self, obj):
        return obj.inscriptions.count()
    
    def get_est_inscrit(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.inscriptions.filter(utilisateur=request.user).exists()
        return False
    
    def get_ma_progression(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            inscription = obj.inscriptions.filter(utilisateur=request.user).first()
            if inscription:
                return {
                    'progression': inscription.progression,
                    'est_complete': inscription.est_complete,
                    'date_inscription': inscription.date_inscription
                }
        return None

class ChoixReponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChoixReponse
        fields = ['id', 'texte', 'ordre']

class QuestionSerializer(serializers.ModelSerializer):
    choix = ChoixReponseSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'texte', 'type_question', 'points', 'ordre', 'choix']

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    nombre_questions = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'cours', 'titre', 'description', 'duree_minutes',
            'note_passage', 'est_actif', 'questions', 'nombre_questions'
        ]
    
    def get_nombre_questions(self, obj):
        return obj.questions.count()

class InscriptionSerializer(serializers.ModelSerializer):
    cours = CoursListSerializer(read_only=True)
    cours_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Inscription
        fields = [
            'id', 'cours', 'cours_id', 'date_inscription', 'progression',
            'est_complete', 'date_completion', 'a_assiste_livestream'
        ]
        read_only_fields = ['date_inscription', 'progression', 'est_complete', 'date_completion']

class TentativeQuizSerializer(serializers.ModelSerializer):
    quiz_titre = serializers.CharField(source='quiz.titre', read_only=True)
    
    class Meta:
        model = TentativeQuiz
        fields = [
            'id', 'quiz', 'quiz_titre', 'score', 'score_pourcentage',
            'est_reussi', 'date_debut', 'date_fin'
        ]
        read_only_fields = ['score', 'score_pourcentage', 'est_reussi', 'date_debut', 'date_fin']

class ReponseUtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReponseUtilisateur
        fields = [
            'id', 'tentative', 'question', 'choix_selectionne',
            'reponse_texte', 'est_correct', 'points_obtenus'
        ]

class CommentaireSerializer(serializers.ModelSerializer):
    utilisateur_nom = serializers.SerializerMethodField()
    
    class Meta:
        model = Commentaire
        fields = [
            'id', 'cours', 'utilisateur', 'utilisateur_nom', 'contenu',
            'note', 'date_creation', 'date_modification'
        ]
        read_only_fields = ['utilisateur', 'date_creation', 'date_modification']
    
    def get_utilisateur_nom(self, obj):
        return f"{obj.utilisateur.first_name} {obj.utilisateur.last_name}".strip() or obj.utilisateur.username
