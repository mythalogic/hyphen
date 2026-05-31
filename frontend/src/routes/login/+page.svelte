<script lang="ts">
  import { goto } from '$app/navigation';
  import { user, isAuthenticated } from '$lib/stores/auth';
  import { onMount } from 'svelte';

  onMount(() => {
    // Redirect if already authenticated
    if ($isAuthenticated) {
      goto('/home');
    }
  });

  let email = '';
  let password = '';
  let errorMessage = '';
  let isLoading = false;

  async function handleLogin() {
    if (!email || !password) {
      errorMessage = 'Please fill in all fields';
      return;
    }

    isLoading = true;
    errorMessage = '';

    try {
      const { signIn } = await import('$lib/supabaseClient');
      await signIn(email, password);
      await goto('/home');
    } catch (error: any) {
      errorMessage = error.message || 'Login failed';
    } finally {
      isLoading = false;
    }
  }

  function goToSignup() {
    goto('/register');
  }
</script>

<div class="auth-container">
  <div class="auth-card">
    <h1>Login to Hyphen</h1>

    <form on:submit|preventDefault={handleLogin}>
      <div class="form-group">
        <label for="email">Email</label>
        <input
          id="email"
          type="email"
          bind:value={email}
          placeholder="your@email.com"
          disabled={isLoading}
        />
      </div>

      <div class="form-group">
        <label for="password">Password</label>
        <input
          id="password"
          type="password"
          bind:value={password}
          placeholder="••••••••"
          disabled={isLoading}
        />
      </div>

      {#if errorMessage}
        <p class="error">{errorMessage}</p>
      {/if}

      <button
        type="submit"
        class="btn btn-primary"
        disabled={isLoading}
      >
        {isLoading ? 'Logging in...' : 'Login'}
      </button>
    </form>

    <p class="auth-link">
      Don't have an account? <button class="link-button" on:click={goToSignup}>Sign up</button>
    </p>
  </div>
</div>

<style>
  .auth-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, var(--hyphen-paper) 0%, #ede8e0 100%);
    padding: var(--spacing-lg);
  }

  .auth-card {
    background: white;
    border-radius: var(--radius-lg);
    padding: var(--spacing-2xl);
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 400px;
  }

  h1 {
    text-align: center;
    margin-bottom: var(--spacing-2xl);
  }

  form {
    margin-bottom: var(--spacing-lg);
  }

  .form-group {
    margin-bottom: var(--spacing-lg);
  }

  .form-group label {
    display: block;
    margin-bottom: var(--spacing-sm);
    font-weight: 500;
  }

  .form-group input {
    width: 100%;
    padding: var(--spacing-md);
    font-size: 1rem;
  }

  .error {
    color: #f44336;
    margin-bottom: var(--spacing-md);
    text-align: center;
  }

  .btn {
    width: 100%;
    padding: var(--spacing-md);
    border-radius: var(--radius-md);
    font-weight: 600;
    font-size: 1rem;
    border: none;
    cursor: pointer;
    transition: all var(--transition-base);
  }

  .btn-primary {
    background-color: var(--hyphen-resonance);
    color: white;
  }

  .btn-primary:hover:not(:disabled) {
    background-color: var(--hyphen-tone);
  }

  .btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .auth-link {
    text-align: center;
    color: var(--hyphen-muted);
  }

  .link-button {
    background: none;
    border: none;
    color: var(--hyphen-resonance);
    cursor: pointer;
    font-weight: 600;
    text-decoration: underline;
  }

  .link-button:hover {
    color: var(--hyphen-tone);
  }
</style>
