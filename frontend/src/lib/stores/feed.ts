import { writable } from 'svelte/store';
import type { FeedHaiku } from '$lib/types';

export const feedItems = writable<FeedHaiku[]>([]);
export const feedLoading = writable(false);
export const currentTab = writable<'for-you' | 'new'>('for-you');
export const offset = writable(0);

export async function loadFeed(tab: 'for-you' | 'new' = 'for-you', limit: number = 20) {
  feedLoading.set(true);
  try {
    const { apiClient } = await import('$lib/api/client');
    const items = await apiClient.getFeed(tab, limit);
    feedItems.set(items);
  } catch (error) {
    console.error('Failed to load feed:', error);
  } finally {
    feedLoading.set(false);
  }
}
