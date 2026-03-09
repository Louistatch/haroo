from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import URLValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone

User = get_user_model()

class Categorie(models.Model):
    """Catégories de cours agricoles"""
    nom = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icone = models.CharField(max_length=50, default='📚')
    ordre = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['ordre', 'nom']
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
    
    def __str__(self):
        return self.nom

class Cours(models.Model):
    """Cours en ligne (vidéo YouTube ou livestream Google Meet)"""
    TYPE_CHOICES = [
        ('VIDEO', 'Vidéo YouTube'),
        ('LIVESTREAM', 'Cours en direct'),
        ('PLAYLIST', 'Playlist YouTube'),
    ]
    
    NIVEAU_CHOICES = [
        ('DEBUTANT', 'Débutant'),
        ('INTERMEDIAIRE', 'Intermédiaire'),
        ('AVANCE', 'Avancé'),
    ]
    
    titre = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    type_cours = models.CharField(max_length=20, choices=TYPE_CHOICES, default='VIDEO')
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='cours')
    niveau = models.CharField(max_length=20, choices=NIVEAU_CHOICES, default='DEBUTANT')
    
    # Pour vidéos YouTube
    youtube_url = models.URLField(blank=True, null=True, validators=[URLValidator()])
    youtube_video_id = models.CharField(max_length=50, blank=True)
    duree_minutes = models.IntegerField(default=0, help_text="Durée en minutes")
    
    # Pour livestream
    google_meet_url = models.URLField(blank=True, null=True)
    date_livestream = models.DateTimeField(blank=True, null=True)
    duree_livestream_minutes = models.IntegerField(default=60)
    
    # Métadonnées
    instructeur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='cours_crees')
    thumbnail = models.URLField(blank=True)
    est_gratuit = models.BooleanField(default=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Transcription et contenu AI
    transcription = models.TextField(blank=True, help_text="Transcription de la vidéo")
    resume_ai = models.TextField(blank=True, help_text="Résumé généré par AI")
    
    # Stats
    vues = models.IntegerField(default=0)
    est_publie = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_creation']
        verbose_name = 'Cours'
        verbose_name_plural = 'Cours'
    
    def __str__(self):
        return self.titre
    
    @property
    def est_livestream_actif(self):
        """Vérifie si le livestream est en cours"""
        if self.type_cours != 'LIVESTREAM' or not self.date_livestream:
            return False
        now = timezone.now()
        fin = self.date_livestream + timezone.timedelta(minutes=self.duree_livestream_minutes)
        return self.date_livestream <= now <= fin


class Quiz(models.Model):
    """Quiz généré par AI pour tester les connaissances"""
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name='quiz')
    titre = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duree_minutes = models.IntegerField(default=10)
    note_passage = models.IntegerField(default=60, validators=[MinValueValidator(0), MaxValueValidator(100)])
    est_actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quiz'
    
    def __str__(self):
        return f"Quiz: {self.titre}"

class Question(models.Model):
    """Questions du quiz"""
    TYPE_CHOICES = [
        ('QCM', 'Choix multiple'),
        ('VRAI_FAUX', 'Vrai/Faux'),
        ('TEXTE', 'Réponse courte'),
    ]
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    texte = models.TextField()
    type_question = models.CharField(max_length=20, choices=TYPE_CHOICES, default='QCM')
    points = models.IntegerField(default=1)
    ordre = models.IntegerField(default=0)
    explication = models.TextField(blank=True, help_text="Explication de la réponse correcte")
    
    class Meta:
        ordering = ['ordre']
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
    
    def __str__(self):
        return self.texte[:100]

class ChoixReponse(models.Model):
    """Choix de réponses pour les questions QCM"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choix')
    texte = models.CharField(max_length=500)
    est_correct = models.BooleanField(default=False)
    ordre = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['ordre']
        verbose_name = 'Choix de réponse'
        verbose_name_plural = 'Choix de réponses'
    
    def __str__(self):
        return self.texte

class Inscription(models.Model):
    """Inscription d'un utilisateur à un cours"""
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inscriptions')
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name='inscriptions')
    date_inscription = models.DateTimeField(auto_now_add=True)
    progression = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    est_complete = models.BooleanField(default=False)
    date_completion = models.DateTimeField(blank=True, null=True)
    
    # Pour livestream
    a_assiste_livestream = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['utilisateur', 'cours']
        ordering = ['-date_inscription']
        verbose_name = 'Inscription'
        verbose_name_plural = 'Inscriptions'
    
    def __str__(self):
        return f"{self.utilisateur.username} - {self.cours.titre}"

class TentativeQuiz(models.Model):
    """Tentative de quiz par un utilisateur"""
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tentatives_quiz')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='tentatives')
    score = models.IntegerField(default=0)
    score_pourcentage = models.IntegerField(default=0)
    est_reussi = models.BooleanField(default=False)
    date_debut = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-date_debut']
        verbose_name = 'Tentative de quiz'
        verbose_name_plural = 'Tentatives de quiz'
    
    def __str__(self):
        return f"{self.utilisateur.username} - {self.quiz.titre} ({self.score_pourcentage}%)"

class ReponseUtilisateur(models.Model):
    """Réponse d'un utilisateur à une question"""
    tentative = models.ForeignKey(TentativeQuiz, on_delete=models.CASCADE, related_name='reponses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choix_selectionne = models.ForeignKey(ChoixReponse, on_delete=models.CASCADE, blank=True, null=True)
    reponse_texte = models.TextField(blank=True)
    est_correct = models.BooleanField(default=False)
    points_obtenus = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Réponse utilisateur'
        verbose_name_plural = 'Réponses utilisateurs'
    
    def __str__(self):
        return f"{self.tentative.utilisateur.username} - Q{self.question.id}"

class Commentaire(models.Model):
    """Commentaires sur les cours"""
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name='commentaires')
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commentaires_cours')
    contenu = models.TextField()
    note = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_creation']
        verbose_name = 'Commentaire'
        verbose_name_plural = 'Commentaires'
    
    def __str__(self):
        return f"{self.utilisateur.username} sur {self.cours.titre}"
