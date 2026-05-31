<script lang="ts">
  import SyllableCounter from './SyllableCounter.svelte';
  import EmotionalProfileCard from './EmotionalProfileCard.svelte';
  import { apiClient } from '$lib/api/client';

  let line1 = '';
  let line2 = '';
  let line3 = '';

  let syllables = [0, 0, 0];
  let isValid = false;
  let isSubmitting = false;
  let emotionalProfile: any = null;
  let showProfile = false;
  let pollInterval: number | null = null;
  let haiku_id = '';

  function handleSyllableChange(event: any) {
    const lineNum = parseInt(event.target.name) || 0;
    syllables[lineNum - 1] = event.detail;
    syllables = syllables; // Trigger reactivity
    updateValidity();
  }

  function updateValidity() {
    isValid = syllables[0] === 5 && syllables[1] === 7 && syllables[2] === 5;
  }

  async function handleSubmit() {
    if (!isValid) return;

    isSubmitting = true;
    try {
      const response = await apiClient.submitHaiku(line1, line2, line3);
      haiku_id = response.id;

      // Start polling for emotional profile
      showProfile = false;
      pollForProfile();
    } catch (error: any) {
      alert('Failed to submit haiku: ' + (error.message || 'Unknown error'));
    } finally {
      isSubmitting = false;
    }
  }

  async function pollForProfile() {
    let attempts = 0;
    const maxAttempts = 30; // 5 minutes with 10s intervals

    const poll = async () => {
      try {
        const profile = await apiClient.getHaikuProfile(haiku_id);
        if (profile && profile.primary_emotion) {
          emotionalProfile = profile;
          showProfile = true;
          if (pollInterval !== null) clearInterval(pollInterval);
        } else {
          attempts++;
          if (attempts >= maxAttempts) {
            if (pollInterval !== null) clearInterval(pollInterval);
            alert('Emotional profile generation timed out. Please refresh the page.');
          }
        }
      } catch (error) {
        attempts++;
        if (attempts >= maxAttempts) {
          if (pollInterval !== null) clearInterval(pollInterval);
        }
      }
    };

    // Initial immediate check, then poll every 5 seconds
    await poll();
    if (attempts < maxAttempts) {
      pollInterval = window.setInterval(poll, 5000);
    }
  }

  function handleNext(event: CustomEvent) {
    const lineNum = event.detail;
    if (lineNum === 1) {
      document.querySelector('[data-line="2"]')?.focus();
    } else if (lineNum === 2) {
      document.querySelector('[data-line="3"]')?.focus();
    }
  }

  function resetForm() {
    line1 = '';
    line2 = '';
    line3 = '';
    syllables = [0, 0, 0];
    showProfile = false;
    emotionalProfile = null;
    haiku_id = '';
  }
</script>

<div class="haiku-composer">
  {#if showProfile && emotionalProfile}
    <EmotionalProfileCard
      profile={emotionalProfile}
      haiku_id={haiku_id}
      line1={line1}
      line2={line2}
      line3={line3}
      on:reset={resetForm}
    />
  {:else}
    <div class="composer-form">
      <h2>Write Your Haiku</h2>
      <p class="subtitle">Not about you. <em>IS you.</em></p>

      <form on:submit|preventDefault={handleSubmit}>
        <SyllableCounter
          bind:line={line1}
          lineNumber={1}
          on:next-line={handleNext}
          onSyllableChange={(count) => {
            syllables[0] = count;
            updateValidity();
          }}
        />

        <SyllableCounter
          bind:line={line2}
          lineNumber={2}
          on:next-line={handleNext}
          onSyllableChange={(count) => {
            syllables[1] = count;
            updateValidity();
          }}
        />

        <SyllableCounter
          bind:line={line3}
          lineNumber={3}
          onSyllableChange={(count) => {
            syllables[2] = count;
            updateValidity();
          }}
        />

        <button
          type="submit"
          disabled={!isValid || isSubmitting}
          class="submit-button"
        >
          {isSubmitting ? 'Reading your haiku...' : 'Submit Haiku'}
        </button>
      </form>

      <div class="validation-info">
        {#if !isValid}
          <p class="text-muted">
            Syllable pattern: {syllables[0]}/{syllables[1]}/{syllables[2]} (need 5/7/5)
          </p>
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  .haiku-composer {
    width: 100%;
  }

  .composer-form {
    max-width: 600px;
    margin: 0 auto;
    padding: var(--spacing-2xl) var(--spacing-lg);
  }

  h2 {
    text-align: center;
    margin-bottom: var(--spacing-sm);
    color: var(--hyphen-ink);
  }

  .subtitle {
    text-align: center;
    color: var(--hyphen-muted);
    margin-bottom: var(--spacing-2xl);
    font-size: 1.1rem;
  }

  .subtitle em {
    font-style: italic;
    color: var(--hyphen-tone);
    font-weight: 500;
  }

  form {
    margin-bottom: var(--spacing-xl);
  }

  .submit-button {
    width: 100%;
    padding: var(--spacing-md) var(--spacing-lg);
    background-color: var(--hyphen-resonance);
    color: white;
    font-size: 1rem;
    font-weight: 600;
    border-radius: var(--radius-md);
    transition: all var(--transition-base);
  }

  .submit-button:hover:not(:disabled) {
    background-color: var(--hyphen-tone);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(196, 87, 58, 0.3);
  }

  .submit-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .validation-info {
    text-align: center;
  }
</style>
