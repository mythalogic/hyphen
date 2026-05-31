import { writable } from 'svelte/store';
import type { Profile } from '$lib/types';

export const currentProfile = writable<Profile | null>(null);
export const profileLoading = writable(false);

export async function loadCurrentProfile() {
  profileLoading.set(true);
  try {
    const { apiClient } = await import('$lib/api/client');
    const profile = await apiClient.getMyProfile();
    currentProfile.set(profile);
  } catch (error) {
    console.error('Failed to load profile:', error);
  } finally {
    profileLoading.set(false);
  }
}

export async function updateCurrentProfile(display_name?: string, avatar_url?: string) {
  try {
    const { apiClient } = await import('$lib/api/client');
    const updated = await apiClient.updateProfile(display_name, avatar_url);
    currentProfile.set(updated);
  } catch (error) {
    console.error('Failed to update profile:', error);
    throw error;
  }
}
