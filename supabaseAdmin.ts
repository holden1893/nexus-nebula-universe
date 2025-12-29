import { createClient } from '@supabase/supabase-js';

function mustGet(name: string): string {
  const v = process.env[name];
  if (!v) throw new Error(`Missing env var: ${name}`);
  return v;
}

/**
 * Server-only Supabase client (uses Service Role key).
 * Keep SUPABASE_SERVICE_ROLE_KEY in Vercel env vars (NOT NEXT_PUBLIC).
 */
export function supabaseAdmin() {
  const url = mustGet('SUPABASE_URL');
  const key = mustGet('SUPABASE_SERVICE_ROLE_KEY');
  return createClient(url, key, {
    auth: { persistSession: false, autoRefreshToken: false },
  });
}
