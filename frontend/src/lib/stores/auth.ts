import { writable } from 'svelte/store';
import { supabase, getCurrentUser } from '$lib/supabaseClient';
import type { User } from '@supabase/supabase-js';

export const user = writable<User | null>(null);
export const isAuthenticated = writable(false);
export const loading = writable(false);

// Initialize auth state on app load
export async function initAuth() {
  loading.set(true);
  try {
    const currentUser = await getCurrentUser();
    user.set(currentUser || null);
    isAuthenticated.set(!!currentUser);
  } catch (error) {
    console.error('Auth initialization failed:', error);
    user.set(null);
    isAuthenticated.set(false);
  } finally {
    loading.set(false);
  }
}

// Listen for auth changes
supabase.auth.onAuthStateChange((event, session) => {
  user.set(session?.user || null);
  isAuthenticated.set(!!session);
});
