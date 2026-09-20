<script>
  import { fade, slide } from 'svelte/transition';

  let { onCriar, onFechar, submetendo = false } = $props();
  let nome = $state('');
  let erro = $state('');

  function handleSubmit(e) {
    e.preventDefault();
    const nomeLimpo = nome.trim();
    if (!nomeLimpo) {
      erro = 'Informe um nome para a quadra.';
      return;
    }
    erro = '';
    onCriar(nomeLimpo);
  }
</script>

<div
  class="modal-backdrop"
  role="presentation"
  onclick={onFechar}
  onkeydown={(e) => { if (e.key === 'Escape') onFechar(); }}
  in:fade={{ duration: 150 }}
>
  <div
    class="modal-card"
    role="dialog"
    aria-modal="true"
    tabindex="-1"
    onclick={(e) => e.stopPropagation()}
    onkeydown={(e) => e.stopPropagation()}
    in:slide={{ duration: 200 }}
  >
    <header class="modal-header">
      <h3>Criar Nova Quadra</h3>
      <button class="btn-close" onclick={onFechar}>✕</button>
    </header>

    <form onsubmit={handleSubmit}>
      <label for="nome-quadra">Nome da Quadra ou Pelada</label>
      <input
        id="nome-quadra"
        type="text"
        placeholder="Ex: Vôlei das 19h, Praia Quadra 2..."
        bind:value={nome}
        maxlength="50"
      />

      {#if erro}
        <p class="erro-msg" in:slide>{erro}</p>
      {/if}

      <div class="modal-actions">
        <button type="button" class="btn-secondary" onclick={onFechar} disabled={submetendo}>
          Cancelar
        </button>
        <button type="submit" class="btn-confirm" disabled={submetendo}>
          {submetendo ? 'Criando...' : 'Criar e Entrar'}
        </button>
      </div>
    </form>
  </div>
</div>

<style>
  .modal-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, 0.85);
    backdrop-filter: blur(4px);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    z-index: 50;
  }

  .modal-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    width: 100%;
    max-width: 440px;
    padding: 24px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
    display: flex;
    flex-direction: column;
    gap: 18px;
  }

  .modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .modal-header h3 {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--texto-contraste);
  }

  .btn-close {
    background: transparent;
    color: var(--text-muted);
    font-size: 1.2rem;
    padding: 6px;
    border-radius: var(--radius-sm);
  }

  .btn-close:hover {
    color: var(--text-primary);
  }

  form {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  label {
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--text-secondary);
  }

  .erro-msg {
    color: var(--acao-destrutiva);
    font-size: 0.85rem;
    font-weight: 500;
  }

  .modal-actions {
    display: flex;
    gap: 12px;
    margin-top: 8px;
  }

  .btn-secondary {
    flex: 1;
    background: var(--bg-card);
    color: var(--text-secondary);
    padding: 14px;
    border-radius: var(--radius-md);
    font-size: 1rem;
  }

  .btn-secondary:hover {
    background: var(--bg-card-hover);
    color: var(--text-primary);
  }

  .btn-confirm {
    flex: 2;
    background: var(--accent-orange);
    color: #ffffff;
    padding: 14px;
    border-radius: var(--radius-md);
    font-size: 1rem;
    font-weight: 700;
  }

  .btn-confirm:hover {
    background: var(--accent-orange-hover);
  }

  button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
</style>
