<script lang="ts">
  import { onMount } from 'svelte';
  import { apiClient } from '$lib/api/client';

  export let line: string = '';
  export let lineNumber: number = 1;
  export let onSyllableChange: (count: number) => void = () => {};

  let syllableCount = 0;
  let checking = false;
  let targetSyllables = [5, 7, 5];

  const japaneseNumerals = ['一', '二', '三'];
  const target = targetSyllables[lineNumber - 1];

  async function checkSyllables() {
    if (!line.trim()) {
      syllableCount = 0;
      onSyllableChange(0);
      return;
    }

    checking = true;
    try {
      const response = await apiClient.checkSyllables(line);
      syllableCount = response.syllable_count;
      onSyllableChange(syllableCount);
    } catch (error) {
      console.error('Syllable check failed:', error);
    } finally {
      checking = false;
    }
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter' && event.shiftKey === false) {
      event.preventDefault();
      // Dispatch custom event for parent to handle focus
      dispatchEvent(new CustomEvent('next-line', { detail: lineNumber }));
    }
  }

  // Debounce syllable check
  let checkTimeout: NodeJS.Timeout;
  function scheduleCheck() {
    clearTimeout(checkTimeout);
    checkTimeout = setTimeout(checkSyllables, 300);
  }

  onMount(() => {
    return () => clearTimeout(checkTimeout);
  });
</script>

<div class="haiku-line">
  <div class="line-header">
    <span class="line-number">{japaneseNumerals[lineNumber - 1]}</span>
    <span class="line-label">Line {lineNumber}</span>
  </div>

  <textarea
    bind:value={line}
    on:input={scheduleCheck}
    on:keydown={handleKeydown}
    placeholder="Write {lineNumber === 2 ? '7' : '5'} syllables..."
    maxlength="100"
    rows="1"
  />

  <div class="syllable-indicator">
    <span
      class="syllable-badge"
      class:valid={syllableCount === target && syllableCount > 0}
      class:invalid={syllableCount > target}
      class:under={syllableCount < target && syllableCount > 0}
    >
      {syllableCount}/{target}
    </span>
    {#if checking}
      <span class="text-muted">checking...</span>
    {/if}
  </div>
</div>

<style>
  .haiku-line {
    margin-bottom: var(--spacing-lg);
  }

  .line-header {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-sm);
  }

  .line-number {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--hyphen-resonance);
  }

  .line-label {
    font-size: 0.875rem;
    color: var(--hyphen-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  textarea {
    width: 100%;
    min-height: 60px;
    font-family: var(--font-haiku);
    font-size: 1.1rem;
    line-height: 1.6;
    padding: var(--spacing-md);
    border: 2px solid var(--hyphen-border);
    border-radius: var(--radius-md);
    background-color: white;
    transition: border-color var(--transition-base), box-shadow var(--transition-base);
    resize: none;
  }

  textarea:focus {
    outline: none;
    border-color: var(--hyphen-resonance);
    box-shadow: 0 0 0 3px rgba(74, 63, 140, 0.1);
  }

  .syllable-indicator {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    margin-top: var(--spacing-sm);
  }

  .syllable-badge {
    display: inline-block;
    padding: var(--spacing-xs) var(--spacing-sm);
    background-color: var(--hyphen-border);
    color: var(--hyphen-ink);
    border-radius: var(--radius-md);
    font-size: 0.75rem;
    font-weight: 600;
    transition: all var(--transition-fast);
  }

  .syllable-badge.valid {
    background-color: #4CAF50;
    color: white;
  }

  .syllable-badge.invalid {
    background-color: #f44336;
    color: white;
  }

  .syllable-badge.under {
    background-color: var(--hyphen-muted);
    color: white;
  }
</style>
