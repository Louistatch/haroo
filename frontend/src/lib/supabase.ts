import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL || 'https://rvhwbxzquglqvhwklaum.supabase.co';
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

export const BUCKETS = {
  profiles: 'profiles',
  documents: 'documents',
  justificatifs: 'justificatifs',
  messaging: 'messaging',
} as const;

export type BucketName = keyof typeof BUCKETS;
