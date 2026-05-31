<script lang="ts">
  import HaikuComposer from '$lib/components/HaikuComposer.svelte';
  import { feedItems, feedLoading, loadFeed, currentTab } from '$lib/stores/feed';
  import { isAuthenticated } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';

  onMount(() => {
    if (!$isAuthenticated) {
      goto('/');
    }
    loadFeed('for-you');
  });

  let showComposer = false;
  let selectedWord = '';

  async function handleReaction(feed_haiku_id: string, word: string) {
    const { apiClient } = await import('$lib/api/client');
    try {
      await apiClient.reactToHaiku(feed_haiku_id, word);
      // Reload feed to show updated reactions
      await loadFeed($currentTab);
    } catch (error) {
      console.error('Failed to react:', error);
    }
  }

  function switchTab(tab: 'for-you' | 'new') {
    currentTab.set(tab);
    loadFeed(tab);
  }
</script>

<div class="home-container">
  {#if showComposer}
    <div class="composer-modal">
      <button class="close-button" on:click={() => (showComposer = false)}>✕</button>
      <HaikuComposer on:reset={() => (showComposer = false)} />
    </div>
  {:else}
    <header class="home-header">
      <h1>Hyphen</h1>
      <div class="header-actions">
        <button class="btn-new-haiku" on:click={() => (showComposer = true)}>
          + Write
        </button>
        <a href="/profile/me" class="btn-profile">Profile</a>
      </div>
    </header>

    <div class="feed-container">
      <div class="feed-tabs">
        <button
          class="tab"
          class:active={$currentTab === 'for-you'}
          on:click={() => switchTab('for-you')}
        >
          For You
        </button>
        <button
          class="tab"
          class:active={$currentTab === 'new'}
          on:click={() => switchTab('new')}
        >
          New
        </button>
        <a href="/discover" class="tab-link">Discover</a>
      </div>

      {#if $feedLoading}
        <p class="loading">Loading feed...</p>
      {:else if $feedItems.length === 0}
        <p class="empty">No haikus yet. Start following poets!</p>
      {:else}
        <div class="feed">
          {#each $feedItems as item}
            <div class="haiku-card">
              <div class="card-header">
                <div class="author-info">
                  <p class="author-name">{item.profiles.display_name || item.profiles.username}</p>
                  <p class="author-handle">@{item.profiles.username}</p>
                </div>
              </div>

              <div class="haiku-text">
                <p>{item.haikus.line1}</p>
                <p>{item.haikus.line2}</p>
                <p>{item.haikus.line3}</p>
              </div>

              <div class="emotional-badge">
                <span class="emotion">{item.emotional_profiles.primary_emotion}</span>
                <span class="intensity">
                  {(item.emotional_profiles.intensity_score * 100).toFixed(0)}%
                </span>
              </div>

              <div class="card-footer">
                <button
                  class="reaction-button"
                  on:click={() => handleReaction(item.id, 'resonant')}
                >
                  ✨ {item.reaction_count}
                </button>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .home-container {
    max-width: 800px;
    margin: 0 auto;
    padding: var(--spacing-lg);
  }

  .composer-modal {
    position: fixed;
    inset: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: var(--spacing-lg);
  }

  .close-button {
    position: absolute;
    top: var(--spacing-md);
    right: var(--spacing-md);
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: white;
  }

  .home-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-2xl);
    padding-bottom: var(--spacing-lg);
    border-bottom: 1px solid var(--hyphen-border);
  }

  .home-header h1 {
    margin: 0;
  }

  .header-actions {
    display: flex;
    gap: var(--spacing-md);
  }

  .btn-new-haiku,
  .btn-profile {
    padding: var(--spacing-sm) var(--spacing-md);
    background-color: var(--hyphen-resonance);
    color: white;
    border: none;
    border-radius: var(--radius-md);
    cursor: pointer;
    font-weight: 600;
    text-decoration: none;
    transition: all var(--transition-fast);
  }

  .btn-new-haiku:hover,
  .btn-profile:hover {
    background-color: var(--hyphen-tone);
  }

  .feed-container {
    margin-bottom: var(--spacing-2xl);
  }

  .feed-tabs {
    display: flex;
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-lg);
    border-bottom: 1px solid var(--hyphen-border);
  }

  .tab {
    padding: var(--spacing-md) 0;
    background: none;
    border: none;
    border-bottom: 3px solid transparent;
    color: var(--hyphen-muted);
    font-weight: 600;
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .tab.active {
    color: var(--hyphen-ink);
    border-bottom-color: var(--hyphen-resonance);
  }

  .tab:hover {
    color: var(--hyphen-ink);
  }

  .tab-link {
    padding: var(--spacing-md) 0;
    color: var(--hyphen-muted);
    text-decoration: none;
    font-weight: 600;
    transition: color var(--transition-fast);
  }

  .tab-link:hover {
    color: var(--hyphen-resonance);
  }

  .loading,
  .empty {
    text-align: center;
    color: var(--hyphen-muted);
    padding: var(--spacing-2xl);
  }

  .feed {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
  }

  .haiku-card {
    background: white;
    border: 1px solid var(--hyphen-border);
    border-radius: var(--radius-md);
    padding: var(--spacing-lg);
    transition: box-shadow var(--transition-fast);
  }

  .haiku-card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .card-header {
    margin-bottom: var(--spacing-md);
  }

  .author-info {
    display: flex;
    flex-direction: column;
  }

  .author-name {
    margin: 0;
    font-weight: 600;
    color: var(--hyphen-ink);
  }

  .author-handle {
    margin: 0;
    font-size: 0.875rem;
    color: var(--hyphen-muted);
  }

  .haiku-text {
    font-family: var(--font-haiku);
    font-size: 1.1rem;
    line-height: 1.8;
    text-align: center;
    padding: var(--spacing-lg) 0;
    border-top: 1px solid var(--hyphen-border);
    border-bottom: 1px solid var(--hyphen-border);
    margin-bottom: var(--spacing-lg);
  }

  .haiku-text p {
    margin: 0;
  }

  .emotional-badge {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-md);
  }

  .emotion {
    display: inline-block;
    padding: var(--spacing-xs) var(--spacing-md);
    background-color: var(--hyphen-resonance);
    color: white;
    border-radius: var(--radius-md);
    font-size: 0.875rem;
    font-weight: 600;
  }

  .intensity {
    font-size: 0.875rem;
    color: var(--hyphen-muted);
  }

  .card-footer {
    display: flex;
    gap: var(--spacing-md);
  }

  .reaction-button {
    padding: var(--spacing-xs) var(--spacing-md);
    background-color: var(--hyphen-border);
    border: none;
    border-radius: var(--radius-md);
    cursor: pointer;
    font-weight: 500;
    transition: all var(--transition-fast);
  }

  .reaction-button:hover {
    background-color: var(--hyphen-resonance);
    color: white;
  }
</style>
