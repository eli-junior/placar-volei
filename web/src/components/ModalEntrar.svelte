<script>
  import { fade, slide } from 'svelte/transition';

  let { quadra, onEntrar, onVoltar, submetendo = false } = $props();
  let apelido = $state('');
  let erro = $state('');

  function handleSubmit(e) {
    e.preventDefault();
    const apelidoLimpo = apelido.trim();
    if (!apelidoLimpo) {
      erro = 'Informe seu apelido para entrar na quadra.';
      return;
    }
    erro = '';
    onEntrar(apelidoLimpo);
  }
</script>

<div
  class="modal-backdrop"
  role="presentation"
  onclick={onVoltar}
  onkeydown={(e) => { if (e.key === 'Escape') onVoltar(); }}
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
      <div>
        <span class="quadra-tag">Entrar na quadra</span>
        <h3>{quadra?.nome || 'Quadra'}</h3>
      </div>
      <button class="btn-close" onclick={onVoltar}>✕</button>
    </header>

    <div class="info-box">
      <span class="info-icon">ℹ️</span>
      <p>
        Sem cadastro e sem senha. Todo participante informa um apelido para aparecer na quadra e acompanhar o placar.
      </p>
    </div>

    <form onsubmit={handleSubmit}>
      <label for="apelido-input">Seu Apelido</label>
      <input
        id="apelido-input"
        type="text"
        placeholder="Ex: Eli, Carlos, Marina..."
        bind:value={apelido}
        maxlength="30"
      />

      {#if erro}
        <p class="erro-msg" in:slide>{erro}</p>
      {/if}

      <div class="modal-actions">
        <button type="button" class="btn-secondary" onclick={onVoltar} disabled={submetendo}>
          Voltar
        </button>
        <button type="submit" class="btn-confirm" disabled={submetendo}>
          {submetendo ? 'Entrando...' : 'Entrar no Jogo'}
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
    align-items: flex-start;
    justify-content: space-between;
  }

  .quadra-tag {
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--accent-orange);
    letter-spacing: 0.05em;
  }

  .modal-header h3 {
    font-size: 1.35rem;
    font-weight: 700;
    color: #ffffff;
    margin-top: 2px;
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

  .info-box {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 12px 14px;
    display: flex;
    gap: 10px;
    align-items: center;
  }

  .info-icon {
    font-size: 1.1rem;
    flex-shrink: 0;
  }

  .info-box p {
    font-size: 0.83rem;
    color: var(--text-secondary);
    line-height: 1.4;
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
    color: #ef4444;
    font-size: 0.85rem;
    font-weight: 500;
  }

  .modal-actions {
    display: flex;
    gap: 12px;
    margin-top: 6px;
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
