import axios from 'axios';

const publicApi = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

export interface Region {
  id: number;
  nom: string;
  code: string;
}

export interface Prefecture {
  id: number;
  nom: string;
  code: string;
  region: number;
  region_nom?: string;
}

export interface Canton {
  id: number;
  nom: string;
  code: string;
  prefecture: number;
  prefecture_nom?: string;
  region_nom?: string;
}

export const getRegions = async (): Promise<Region[]> => {
  try {
    const response = await publicApi.get('/regions/');
    console.log('Régions chargées:', response.data);
    // Gérer la pagination si présente
    const data = response.data.results || response.data;
    return Array.isArray(data) ? data : [];
  } catch (error) {
    console.error('Erreur chargement régions:', error);
    return [];
  }
};

export const getPrefectures = async (regionId: number): Promise<Prefecture[]> => {
  try {
    const url = `/prefectures/?region=${regionId}`;
    const response = await publicApi.get(url);
    console.log('Préfectures chargées:', response.data);
    // Gérer la pagination si présente
    const data = response.data.results || response.data;
    return Array.isArray(data) ? data : [];
  } catch (error) {
    console.error('Erreur chargement préfectures:', error);
    return [];
  }
};

export const getCantons = async (prefectureId: number): Promise<Canton[]> => {
  try {
    const url = `/cantons/?prefecture=${prefectureId}`;
    const response = await publicApi.get(url);
    console.log('Cantons chargés:', response.data);
    // Gérer la pagination si présente
    const data = response.data.results || response.data;
    return Array.isArray(data) ? data : [];
  } catch (error) {
    console.error('Erreur chargement cantons:', error);
    return [];
  }
};
