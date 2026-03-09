import api from './auth';

export interface Categorie {
  id: number;
  nom: string;
  slug: string;
  description: string;
  icone: string;
  ordre: number;
  nombre_cours: number;
}

export interface Cours {
  id: number;
  titre: string;
  slug: string;
  description: string;
  type_cours: 'VIDEO' | 'LIVESTREAM' | 'PLAYLIST';
  categorie: number;
  categorie_nom: string;
  niveau: 'DEBUTANT' | 'INTERMEDIAIRE' | 'AVANCE';
  youtube_url?: string;
  youtube_video_id?: string;
  google_meet_url?: string;
  date_livestream?: string;
  duree_minutes: number;
  duree_livestream_minutes?: number;
  instructeur?: number;
  instructeur_nom: string;
  thumbnail?: string;
  est_gratuit: boolean;
  prix: string;
  transcription?: string;
  resume_ai?: string;
  vues: number;
  nombre_inscrits: number;
  est_inscrit: boolean;
  est_livestream_actif: boolean;
  date_creation: string;
}

export interface Quiz {
  id: number;
  cours: number;
  titre: string;
  description: string;
  duree_minutes: number;
  note_passage: number;
  est_actif: boolean;
  questions: Question[];
  nombre_questions: number;
}

export interface Question {
  id: number;
  texte: string;
  type_question: 'QCM' | 'VRAI_FAUX' | 'TEXTE';
  points: number;
  ordre: number;
  choix: ChoixReponse[];
}

export interface ChoixReponse {
  id: number;
  texte: string;
  ordre: number;
}

export interface Inscription {
  id: number;
  cours: Cours;
  date_inscription: string;
  progression: number;
  est_complete: boolean;
  date_completion?: string;
  a_assiste_livestream: boolean;
}

export interface TentativeQuiz {
  id: number;
  quiz: number;
  quiz_titre: string;
  score: number;
  score_pourcentage: number;
  est_reussi: boolean;
  date_debut: string;
  date_fin?: string;
}

// Catégories
export const fetchCategories = async (): Promise<Categorie[]> => {
  const response = await api.get('/elearning/categories/');
  return response.data.results || response.data;
};

// Cours
export const fetchCours = async (params?: any): Promise<{ results: Cours[]; count: number }> => {
  const response = await api.get('/elearning/cours/', { params });
  return response.data;
};

export const fetchCoursDetail = async (slug: string): Promise<Cours> => {
  const response = await api.get(`/elearning/cours/${slug}/`);
  return response.data;
};

export const inscrireCours = async (slug: string): Promise<Inscription> => {
  const response = await api.post(`/elearning/cours/${slug}/inscrire/`);
  return response.data;
};

export const marquerComplete = async (slug: string): Promise<Inscription> => {
  const response = await api.post(`/elearning/cours/${slug}/marquer_complete/`);
  return response.data;
};

export const assisterLivestream = async (slug: string): Promise<void> => {
  await api.post(`/elearning/cours/${slug}/assister_livestream/`);
};

export const fetchQuizCours = async (slug: string): Promise<Quiz[]> => {
  const response = await api.get(`/elearning/cours/${slug}/quiz/`);
  return response.data;
};

// Inscriptions
export const fetchMesInscriptions = async (): Promise<Inscription[]> => {
  const response = await api.get('/elearning/inscriptions/mes_cours/');
  return response.data;
};

export const fetchCoursEnCours = async (): Promise<Inscription[]> => {
  const response = await api.get('/elearning/inscriptions/en_cours/');
  return response.data;
};

export const fetchCoursCompletes = async (): Promise<Inscription[]> => {
  const response = await api.get('/elearning/inscriptions/completes/');
  return response.data;
};

// Quiz
export const commencerQuiz = async (quizId: number): Promise<TentativeQuiz> => {
  const response = await api.post(`/elearning/quiz/${quizId}/commencer/`);
  return response.data;
};

export const soumettreQuiz = async (
  quizId: number,
  tentativeId: number,
  reponses: Array<{ question_id: number; choix_id: number }>
): Promise<TentativeQuiz> => {
  const response = await api.post(`/elearning/quiz/${quizId}/soumettre/`, {
    tentative_id: tentativeId,
    reponses,
  });
  return response.data;
};

// Commentaires
export const fetchCommentaires = async (slug: string): Promise<any[]> => {
  const response = await api.get(`/elearning/cours/${slug}/commentaires/`);
  return response.data;
};

export const ajouterCommentaire = async (slug: string, data: { contenu: string; note?: number }): Promise<any> => {
  const response = await api.post(`/elearning/cours/${slug}/commentaires/`, data);
  return response.data;
};
