from django.contrib import admin
from .models import (
    Categorie, Cours, Quiz, Question, ChoixReponse,
    Inscription, TentativeQuiz, ReponseUtilisateur, Commentaire
)

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'slug', 'icone', 'ordre']
    prepopulated_fields = {'slug': ('nom',)}
    ordering = ['ordre', 'nom']

class ChoixReponseInline(admin.TabularInline):
    model = ChoixReponse
    extra = 4

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1

@admin.register(Cours)
class CoursAdmin(admin.ModelAdmin):
    list_display = ['titre', 'type_cours', 'categorie', 'niveau', 'est_publie', 'vues', 'date_creation']
    list_filter = ['type_cours', 'categorie', 'niveau', 'est_publie', 'est_gratuit']
    search_fields = ['titre', 'description']
    prepopulated_fields = {'slug': ('titre',)}
    date_hierarchy = 'date_creation'
    ordering = ['-date_creation']

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['titre', 'cours', 'duree_minutes', 'note_passage', 'est_actif']
    list_filter = ['est_actif', 'cours__categorie']
    search_fields = ['titre', 'cours__titre']
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['texte', 'quiz', 'type_question', 'points', 'ordre']
    list_filter = ['type_question', 'quiz']
    search_fields = ['texte']
    inlines = [ChoixReponseInline]

@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'cours', 'progression', 'est_complete', 'date_inscription']
    list_filter = ['est_complete', 'cours__categorie', 'date_inscription']
    search_fields = ['utilisateur__username', 'cours__titre']
    date_hierarchy = 'date_inscription'

@admin.register(TentativeQuiz)
class TentativeQuizAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'quiz', 'score_pourcentage', 'est_reussi', 'date_debut']
    list_filter = ['est_reussi', 'quiz', 'date_debut']
    search_fields = ['utilisateur__username', 'quiz__titre']
    date_hierarchy = 'date_debut'

@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'cours', 'note', 'date_creation']
    list_filter = ['note', 'cours__categorie', 'date_creation']
    search_fields = ['utilisateur__username', 'cours__titre', 'contenu']
    date_hierarchy = 'date_creation'
