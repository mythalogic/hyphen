<script lang="ts">
  import { goto } from '$app/navigation';
  import { isAuthenticated } from '$lib/stores/auth';

  onMount(() => {
    if ($isAuthenticated) {
      goto('/home');
    }
  });

  function goToSignup() {
    goto('/register');
  }

  function goToLogin() {
    goto('/login');
  }
</script>

<div class="landing-container">
  <nav class="navbar">
    <div class="logo">
      <h1>Hyphen</h1>
    </div>
    <div class="nav-buttons">
      <button class="btn-text" on:click={goToLogin}>Login</button>
      <button class="btn-primary" on:click={goToSignup}>Sign Up</button>
    </div>
  </nav>

  <main class="hero">
    <div class="hero-content">
      <h1>Identity is Poetry</h1>
      <p class="hero-subtitle">
        A creative social network where haiku defines who you are
      </p>

      <p class="hero-description">
        Write your haiku. Get an emotional fingerprint. Connect with others who resonate.
      </p>

      <div class="cta-buttons">
        <button class="btn btn-large btn-primary" on:click={goToSignup}>
          Start Writing
        </button>
        <button class="btn btn-large btn-secondary" on:click={goToLogin}>
          I Already Write
        </button>
      </div>
    </div>

    <div class="hero-visual">
      <div class="haiku-preview">
        <p>softly falling rain</p>
        <p>reminds me of your silence</p>
        <p>yet somehow you're near</p>
      </div>
    </div>
  </main>

  <section class="features">
    <div class="feature">
      <h3>Write Haiku</h3>
      <p>Express yourself in the timeless 5-7-5 syllable form</p>
    </div>
    <div class="feature">
      <h3>Emotional Resonance</h3>
      <p>AI reads your poetry and generates an emotional profile</p>
    </div>
    <div class="feature">
      <h3>Connect Authentically</h3>
      <p>Find others who resonate with your emotional truth</p>
    </div>
  </section>
</div>

<style>
  .landing-container {
    min-height: 100vh;
    background-color: var(--hyphen-paper);
  }

  .navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-lg) var(--spacing-2xl);
    border-bottom: 1px solid var(--hyphen-border);
  }

  .logo h1 {
    margin: 0;
    font-size: 1.5rem;
  }

  .nav-buttons {
    display: flex;
    gap: var(--spacing-md);
  }

  .btn-text {
    background: none;
    border: none;
    color: var(--hyphen-ink);
    font-weight: 500;
    cursor: pointer;
    transition: color var(--transition-fast);
  }

  .btn-text:hover {
    color: var(--hyphen-resonance);
  }

  .btn-primary {
    padding: var(--spacing-sm) var(--spacing-lg);
    background-color: var(--hyphen-resonance);
    color: white;
    border: none;
    border-radius: var(--radius-md);
    cursor: pointer;
    font-weight: 600;
    transition: all var(--transition-fast);
  }

  .btn-primary:hover {
    background-color: var(--hyphen-tone);
  }

  .hero {
    display: grid;
    grid-template-columns: 1fr 1fr;
    align-items: center;
    gap: var(--spacing-2xl);
    padding: var(--spacing-2xl) var(--spacing-2xl);
    max-width: 1200px;
    margin: 0 auto;
  }

  .hero-content h1 {
    font-size: 3rem;
    margin-bottom: var(--spacing-lg);
    line-height: 1.2;
  }

  .hero-subtitle {
    font-size: 1.5rem;
    color: var(--hyphen-resonance);
    margin-bottom: var(--spacing-lg);
  }

  .hero-description {
    font-size: 1.1rem;
    color: var(--hyphen-muted);
    margin-bottom: var(--spacing-2xl);
  }

  .cta-buttons {
    display: flex;
    gap: var(--spacing-md);
  }

  .btn {
    border: none;
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: all var(--transition-base);
  }

  .btn-large {
    padding: var(--spacing-md) var(--spacing-2xl);
    font-size: 1.1rem;
    font-weight: 600;
  }

  .btn-secondary {
    background-color: transparent;
    color: var(--hyphen-resonance);
    border: 2px solid var(--hyphen-resonance);
  }

  .btn-secondary:hover {
    background-color: var(--hyphen-resonance);
    color: white;
  }

  .hero-visual {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .haiku-preview {
    background: white;
    padding: var(--spacing-2xl);
    border-radius: var(--radius-lg);
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
    font-family: var(--font-haiku);
    font-size: 1.5rem;
    text-align: center;
    line-height: 1.8;
    max-width: 400px;
  }

  .haiku-preview p {
    margin: 0;
    color: var(--hyphen-ink);
  }

  .features {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--spacing-2xl);
    padding: var(--spacing-2xl);
    max-width: 1200px;
    margin: 0 auto;
  }

  .feature {
    text-align: center;
  }

  .feature h3 {
    color: var(--hyphen-resonance);
    margin-bottom: var(--spacing-md);
  }

  .feature p {
    color: var(--hyphen-muted);
  }

  @media (max-width: 768px) {
    .hero {
      grid-template-columns: 1fr;
      padding: var(--spacing-lg);
    }

    .hero-content h1 {
      font-size: 2rem;
    }

    .features {
      grid-template-columns: 1fr;
    }
  }
</style>
