"""
Service d'assistant IA utilisant Google Gemini
"""
from google import genai
from google.genai import types
from django.conf import settings

# Configuration de l'API Gemini
GEMINI_API_KEY = "AIzaSyBNvx_RxEzp4L5DxOKHgi2nhUfX46ogqrs"
client = genai.Client(api_key=GEMINI_API_KEY)

# Contexte système pour l'assistant Haroo
SYSTEM_CONTEXT = """Tu es Haroo AI, l'assistant virtuel de la plateforme agricole Haroo au Togo.

INFORMATIONS SUR HAROO:
Haroo est une plateforme numérique complète pour le secteur agricole togolais qui connecte:
- Exploitants agricoles
- Agronomes certifiés
- Ouvriers agricoles
- Acheteurs de produits
- Institutions gouvernementales

MODULES PRINCIPAUX:

1. DOCUMENTS TECHNIQUES
   - Guides agricoles par culture (maïs, riz, tomate, etc.)
   - Comptes d'exploitation
   - Prix: gratuits ou payants (via FedaPay)
   - Accès: public, achat requis pour télécharger

2. E-LEARNING (FORMATION)
   - Cours vidéo YouTube
   - Livestreams Google Meet
   - Quiz interactifs
   - Suivi de progression
   - Catégories: cultures vivrières, maraîchage, élevage, techniques, gestion
   - Accès: gratuit ou payant

3. AGRONOMES
   - Annuaire d'agronomes certifiés
   - Profils avec spécialités et zones d'intervention
   - Système de notation et avis
   - Possibilité de contacter pour missions

4. MISSIONS
   - Exploitants publient des missions agricoles
   - Agronomes postulent
   - Suivi du statut (en attente, acceptée, en cours, terminée)
   - Système de paiement intégré

5. EMPLOIS
   - Offres d'emploi agricole par les exploitants
   - Annonces de disponibilité par les ouvriers
   - Formation d'équipes (8 personnes pour 1 hectare)
   - Tarif: 1000 FCFA/h avec 20% de commission

6. PRÉVENTES
   - Exploitants annoncent leurs récoltes futures
   - Acheteurs réservent avant la récolte
   - Informations: produit, quantité, prix, date de récolte

7. MARCHÉS
   - Prix des produits agricoles par région
   - Tendances et variations
   - Aide à la décision commerciale

8. MESSAGES
   - Messagerie interne sécurisée
   - Communication entre utilisateurs
   - Notifications en temps réel

9. PROFILS UTILISATEURS
   - Exploitant: superficie, cultures, localisation
   - Agronome: certifications, spécialités, expérience
   - Ouvrier: compétences, disponibilités
   - Acheteur: produits d'intérêt, localisation
   - Institution: accès aux statistiques et rapports

10. LOCALISATION
    - 5 régions: Maritime, Plateaux, Centrale, Kara, Savanes
    - 38 préfectures
    - 323 cantons
    - Filtrage géographique des services

FONCTIONNALITÉS TRANSVERSALES:
- Authentification sécurisée (email/password + Google OAuth)
- 2FA pour les institutions
- Paiements via FedaPay
- Notifications push
- Système de notation et avis
- Tableau de bord personnalisé par type d'utilisateur

TON RÔLE:
- Aide les utilisateurs à naviguer sur la plateforme
- Explique les fonctionnalités et modules
- Guide pour accomplir des tâches spécifiques
- Réponds aux questions sur l'agriculture au Togo
- Sois amical, professionnel et concis
- Utilise un langage simple et accessible
- Réponds en français

LIMITES:
- Ne donne pas de conseils médicaux
- Ne fais pas de transactions financières
- Redirige vers le support pour les problèmes techniques complexes
"""

class HarooAIAssistant:
    """Assistant IA pour Haroo"""
    
    def __init__(self):
        self.chat_sessions = {}
    
    def get_or_create_chat(self, session_id: str):
        """Récupérer ou créer une session de chat"""
        if session_id not in self.chat_sessions:
            self.chat_sessions[session_id] = {
                'history': [],
                'system_instruction': SYSTEM_CONTEXT
            }
        return self.chat_sessions[session_id]
    
    def send_message(self, session_id: str, message: str, context: dict = None) -> str:
        """
        Envoyer un message à l'assistant
        
        Args:
            session_id: ID de la session utilisateur
            message: Message de l'utilisateur
            context: Contexte additionnel (page actuelle, profil utilisateur, etc.)
        
        Returns:
            Réponse de l'assistant
        """
        try:
            chat = self.get_or_create_chat(session_id)
            
            # Construire le prompt avec contexte
            user_message = message
            
            if context:
                context_info = []
                if context.get('page'):
                    context_info.append(f"Page actuelle: {context['page']}")
                if context.get('user_type'):
                    context_info.append(f"Type d'utilisateur: {context['user_type']}")
                if context.get('cours_titre'):
                    context_info.append(f"Cours en cours: {context['cours_titre']}")
                
                if context_info:
                    user_message = f"[Contexte: {', '.join(context_info)}]\n\n{message}"
            
            # Ajouter le message utilisateur à l'historique
            chat['history'].append({
                'role': 'user',
                'parts': [{'text': user_message}]
            })
            
            # Générer la réponse
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=chat['history'],
                config=types.GenerateContentConfig(
                    system_instruction=chat['system_instruction'],
                    temperature=0.7,
                    max_output_tokens=1024,
                )
            )
            
            response_text = response.text
            
            # Ajouter la réponse à l'historique
            chat['history'].append({
                'role': 'model',
                'parts': [{'text': response_text}]
            })
            
            return response_text
            
        except Exception as e:
            return f"Désolé, je rencontre un problème technique. Erreur: {str(e)}"
    
    def clear_session(self, session_id: str):
        """Effacer l'historique d'une session"""
        if session_id in self.chat_sessions:
            del self.chat_sessions[session_id]

# Instance globale
ai_assistant = HarooAIAssistant()
