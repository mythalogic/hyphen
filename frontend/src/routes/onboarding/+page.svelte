<script lang="ts">
  import { goto } from '$app/navigation';
  import { isAuthenticated } from '$lib/stores/auth';
  import { currentProfile, loadCurrentProfile, updateCurrentProfile } from '$lib/stores/profile';

  let step = 1;
  let username = '';
  let errorMessage = '';
  let isChecking = false;
  let isAvailable = false;

  async function checkUsername() {
    if (!username || username.length < 3) {
      errorMessage = 'Username must be at least 3 characters';
      return;
    }

    isChecking = true;
    errorMessage = '';

    try {
      const { apiClient } = await import('$lib/api/client');
      // Check if username is available (try to get profile)
      try {
        await apiClient.getProfile(username);
        errorMessage = 'Username already taken';
        isAvailable = false;
      } catch (error) {
        // 404 means username is available
        isAvailable = true;
      }
    } catch (error) {
      console.error('Error checking username:', error);
      errorMessage = 'Failed to check username availability';
    } finally {
      isChecking = false;
    }
  }

  async function proceedToHaiku() {
    if (!isAvailable) return;

    // TODO: Create user and profile in database
    // For now, just move to next step
    step = 2;
  }

  async function completeOnboarding() {
    // TODO: Redirect to home
    await goto('/home');
  }
</script>

<div class="onboarding-container">
  {#if step === 1}
    <!-- Step 1: Username -->
    <div class="onboarding-step">
      <div class="step-content">
        <h1>Welcome to Hyphen</h1>
        <p class="subtitle">Choose your identity on the network</p>

        <div class="username-input">
          <label for="username">Username</label>
          <input
            id="username"
            bind:value={username}
            type="text"
            placeholder="Your unique username"
            minlength="3"
            maxlength="30"
            on:blur={checkUsername}
          />

          {#if username}
            {#if isChecking}
              <p class="text-muted">Checking availability...</p>
            {:else if isAvailable}
              <p class="success">✓ Available</p>
            {:else if errorMessage}
              <p class="error">{errorMessage}</p>
            {/if}
          {/if}
        </div>

        <button
          class="btn btn-primary"
          on:click={proceedToHaiku}
          disabled={!isAvailable || isChecking}
        >
          Next: Write Your Haiku
        </button>
      </div>
    </div>
  {/if}

  {#if step === 2}
    <!-- Step 2: Haiku (handled by HaikuComposer) -->
    <div class="onboarding-step">
      <!-- HaikuComposer will be imported here -->
      <p>Write your identity haiku here</p>
      <!-- Component will trigger step 3 when complete -->
    </div>
  {/if}

  {#if step === 3}
    <!-- Step 3: Review & Complete -->
    <div class="onboarding-step">
      <div class="step-content">
        <h1>Welcome to Hyphen!</h1>
        <p class="subtitle">Your identity is complete</p>

        <button
          class="btn btn-primary"
          on:click={completeOnboarding}
        >
          Go to Home
        </button>
      </div>
    </div>
  {/if}

  <!-- Progress indicator -->
  <div class="step-indicator">
    <div class="steps">
      {#each [1, 2, 3] as s}
        <div
          class="step-dot"
          class:active={step === s}
          class:completed={step > s}
        >
          {s}
        </div>
      {/each}
    </div>
  </div>
</div>

<style>
  .onboarding-container {
    min-height: 100vh;
    background: linear-gradient(135deg, var(--hyphen-paper) 0%, #ede8e0 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-lg);
    position: relative;
  }

  .onboarding-step {
    width: 100%;
    max-width: 500px;
    animation: slideUp 500ms ease-out;
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

  .step-content {
    background: white;
    border-radius: var(--radius-lg);
    padding: var(--spacing-2xl);
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  }

  h1 {
    text-align: center;
    margin-bottom: var(--spacing-sm);
    color: var(--hyphen-ink);
  }

  .subtitle {
    text-align: center;
    color: var(--hyphen-muted);
    margin-bottom: var(--spacing-2xl);
  }

  .username-input {
    margin-bottom: var(--spacing-lg);
  }

  .username-input label {
    display: block;
    margin-bottom: var(--spacing-sm);
    font-weight: 500;
  }

  .username-input input {
    width: 100%;
    padding: var(--spacing-md);
    font-size: 1rem;
  }

  .btn {
    width: 100%;
    padding: var(--spacing-md) var(--spacing-lg);
    border-radius: var(--radius-md);
    font-weight: 600;
    font-size: 1rem;
    transition: all var(--transition-base);
  }

  .btn-primary {
    background-color: var(--hyphen-resonance);
    color: white;
  }

  .btn-primary:hover:not(:disabled) {
    background-color: var(--hyphen-tone);
    transform: translateY(-2px);
  }

  .btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .success {
    color: #4CAF50;
    font-size: 0.875rem;
    margin-top: var(--spacing-xs);
  }

  .error {
    color: #f44336;
    font-size: 0.875rem;
    margin-top: var(--spacing-xs);
  }

  .step-indicator {
    position: fixed;
    bottom: var(--spacing-2xl);
    left: 50%;
    transform: translateX(-50%);
  }

  .steps {
    display: flex;
    gap: var(--spacing-md);
  }

  .step-dot {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background-color: var(--hyphen-border);
    color: var(--hyphen-ink);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    transition: all var(--transition-base);
  }

  .step-dot.active {
    background-color: var(--hyphen-resonance);
    color: white;
    transform: scale(1.1);
  }

  .step-dot.completed {
    background-color: #4CAF50;
    color: white;
  }
</style>
