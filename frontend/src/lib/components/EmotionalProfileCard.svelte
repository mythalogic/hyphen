<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { apiClient } from '$lib/api/client';
  import { currentProfile } from '$lib/stores/profile';

  const dispatch = createEventDispatcher();

  export let profile: any;
  export let haiku_id: string;
  export let line1: string;
  export let line2: string;
  export let line3: string;

  let isSettingIdentity = false;
  let isPosting = false;

  async function setAsIdentity() {
    isSettingIdentity = true;
    try {
      await apiClient.setIdentityHaiku(haiku_id);
      alert('Your identity haiku has been set!');
      dispatch('reset');
    } catch (error: any) {
      alert('Failed to set identity haiku: ' + (error.message || 'Unknown error'));
    } finally {
      isSettingIdentity = false;
    }
  }

  async function postToFeed() {
    isPosting = true;
    try {
      await apiClient.postToFeed(haiku_id);
      alert('Posted to feed!');
      dispatch('reset');
    } catch (error: any) {
      alert('Failed to post to feed: ' + (error.message || 'Unknown error'));
    } finally {
      isPosting = false;
    }
  }

  function handleDismiss() {
    dispatch('reset');
  }

  const fullText = `${line1}\n${line2}\n${line3}`;
</script>

<div class="profile-reveal" in:fade={{ duration: 300 }}>
  <div class="profile-card">
    <button class="close-button" on:click={handleDismiss}>✕</button>

    <div class="haiku-display">
      <p>{line1}</p>
      <p>{line2}</p>
      <p>{line3}</p>
    </div>

    <div class="emotional-content">
      <h2 class="primary-emotion">{profile.primary_emotion}</h2>

      <div class="tone-tags">
        {#each profile.tone_tags as tag}
          <span class="tag">{tag}</span>
        {/each}
      </div>

      <div class="intensity-bar">
        <div class="bar-fill" style="width: {profile.intensity_score * 100}%"></div>
      </div>
      <p class="intensity-label">
        Intensity: {(profile.intensity_score * 100).toFixed(0)}%
      </p>
    </div>

    <div class="action-buttons">
      {#if !$currentProfile?.bio_haiku_id}
        <button
          class="btn btn-primary"
          on:click={setAsIdentity}
          disabled={isSettingIdentity}
        >
          {isSettingIdentity ? 'Setting...' : 'Set as Identity'}
        </button>
      {/if}

      <button
        class="btn btn-secondary"
        on:click={postToFeed}
        disabled={isPosting}
      >
        {isPosting ? 'Posting...' : 'Post to Feed'}
      </button>

      <button
        class="btn btn-tertiary"
        on:click={handleDismiss}
      >
        Dismiss
      </button>
    </div>
  </div>
</div>

<style>
  .profile-reveal {
    position: fixed;
    inset: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-lg);
    z-index: 1000;
    animation: fadeIn 300ms ease-out;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  .profile-card {
    background-color: var(--hyphen-paper);
    border-radius: var(--radius-lg);
    padding: var(--spacing-2xl);
    max-width: 600px;
    width: 100%;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
    position: relative;
    animation: slideUp 300ms ease-out;
  }

  @keyframes slideUp {
    from {
      transform: translateY(20px);
      opacity: 0;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  }

  .close-button {
    position: absolute;
    top: var(--spacing-md);
    right: var(--spacing-md);
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: var(--hyphen-muted);
    transition: color var(--transition-fast);
  }

  .close-button:hover {
    color: var(--hyphen-ink);
  }

  .haiku-display {
    margin-bottom: var(--spacing-2xl);
    text-align: center;
    font-family: var(--font-haiku);
    font-size: 1.25rem;
    line-height: 2;
    color: var(--hyphen-ink);
    padding: var(--spacing-xl) 0;
    border-top: 2px solid var(--hyphen-border);
    border-bottom: 2px solid var(--hyphen-border);
  }

  .haiku-display p {
    margin: 0;
  }

  .emotional-content {
    text-align: center;
    margin-bottom: var(--spacing-2xl);
  }

  .primary-emotion {
    font-size: 2.5rem;
    margin: var(--spacing-lg) 0;
    color: var(--hyphen-resonance);
  }

  .tone-tags {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-sm);
    justify-content: center;
    margin-bottom: var(--spacing-lg);
  }

  .tag {
    display: inline-block;
    padding: var(--spacing-xs) var(--spacing-md);
    background-color: var(--hyphen-resonance);
    color: white;
    border-radius: var(--radius-md);
    font-size: 0.85rem;
    font-weight: 500;
  }

  .intensity-bar {
    width: 100%;
    height: 8px;
    background-color: var(--hyphen-border);
    border-radius: var(--radius-md);
    overflow: hidden;
    margin-bottom: var(--spacing-sm);
  }

  .bar-fill {
    height: 100%;
    background-color: var(--hyphen-tone);
    transition: width 600ms cubic-bezier(0.4, 0, 0.2, 1);
  }

  .intensity-label {
    font-size: 0.875rem;
    color: var(--hyphen-muted);
    margin: 0;
  }

  .action-buttons {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
  }

  .btn {
    padding: var(--spacing-md) var(--spacing-lg);
    border-radius: var(--radius-md);
    font-weight: 600;
    transition: all var(--transition-base);
    font-size: 1rem;
  }

  .btn-primary {
    background-color: var(--hyphen-resonance);
    color: white;
  }

  .btn-primary:hover:not(:disabled) {
    background-color: var(--hyphen-tone);
    transform: translateY(-2px);
  }

  .btn-secondary {
    background-color: var(--hyphen-tone);
    color: white;
  }

  .btn-secondary:hover:not(:disabled) {
    background-color: var(--hyphen-resonance);
    transform: translateY(-2px);
  }

  .btn-tertiary {
    background-color: transparent;
    color: var(--hyphen-muted);
    border: 1px solid var(--hyphen-border);
  }

  .btn-tertiary:hover:not(:disabled) {
    border-color: var(--hyphen-ink);
    color: var(--hyphen-ink);
  }

  .btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
</style>
