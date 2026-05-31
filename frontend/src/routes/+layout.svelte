<script lang="ts">
  import { initAuth, isAuthenticated, loading } from '$lib/stores/auth';
  import { onMount } from 'svelte';
  import '../app.css';

  onMount(() => {
    initAuth();
  });
</script>

{#if $loading}
  <div class="loading-container">
    <p>Loading...</p>
  </div>
{:else}
  <slot />
{/if}

<style>
  .loading-container {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    background-color: var(--hyphen-paper);
  }
</style>
