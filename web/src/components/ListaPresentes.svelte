<script>
  import { slide, fade } from 'svelte/transition';

  let {
    participantes = [],
    euId = null,
    prefersReducedMotion = false,
    podeAutorizar = false,
    desabilitado = false,
    onPromoverControlador = (id) => {},
    onRevogarControlador = (id) => {},
    onAutorizarAdmin = (id) => {},
  } = $props();
</script>

<div class="presentes-card" in:fade={{ duration: prefersReducedMotion ? 0 : 200 }}>
  <div class="card-header">
    <div class="header-left">
      <span class="icon">👥</span>
      <h4>Presentes na Quadra</h4>
    </div>
    <span class="badge-total">{participantes.length}</span>
  </div>

  <div class="participantes-list">
    {#if participantes.length === 0}
      <p class="empty-text">Nenhum participante conectado ainda.</p>
    {:else}
      {#each participantes as p (p.id)}
        <div class="participante-row" in:slide={{ duration: prefersReducedMotion ? 0 : 200 }}>
          <div class="participante-info">
            <span
              class="status-dot {p.online ? 'status-online' : 'status-offline'}"
              title={p.online ? 'Online agora' : 'Offline'}
            ></span>
            <span class="apelido {p.id === euId ? 'apelido-eu' : ''}">
              {p.apelido}
              {#if p.id === euId}
                <span class="eu-tag">(você)</span>
              {/if}
            </span>
          </div>

          {#if podeAutorizar && p.id !== euId}
            {#if p.papel === 'ESPECTADOR'}
              <button
                type="button"
                class="btn-papel btn-promover"
                disabled={desabilitado}
                onclick={() => onPromoverControlador(p.id)}
                aria-label={`Promover ${p.apelido} a controlador`}
              >
                Tornar controlador
              </button>
            {:else if p.papel === 'CONTROLADOR'}
              <button
                type="button"
                class="btn-papel btn-revogar"
                disabled={desabilitado}
                onclick={() => onRevogarControlador(p.id)}
                aria-label={`Revogar controlador de ${p.apelido}`}
              >
                Revogar controlador
              </button>
            {/if}
          {/if}
          <span class="badge {p.papel === 'ADMIN' ? 'badge-admin' : p.papel === 'CONTROLADOR' ? 'badge-controlador' : 'badge-espectador'}">
            {p.papel}
          </span>
        </div>
      {/each}
    {/if}
  </div>
</div>

<style>
  .btn-papel {
    min-height: 40px;
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 0.82rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s ease;
  }
  .btn-promover {
    border: 1px solid rgba(56, 189, 248, 0.4);
    background: rgba(56, 189, 248, 0.1);
    color: var(--acento-info);
  }
  .btn-promover:hover:not(:disabled) {
    background: rgba(56, 189, 248, 0.2);
    border-color: var(--acento-info);
  }
  .btn-revogar {
    border: 1px solid rgba(248, 113, 113, 0.4);
    background: rgba(248, 113, 113, 0.1);
    color: var(--estado-erro);
  }
  .btn-revogar:hover:not(:disabled) {
    background: rgba(248, 113, 113, 0.2);
    border-color: var(--estado-erro);
  }
  .btn-papel:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  .participante-row { flex-wrap: wrap; gap: 10px; }
  .presentes-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 18px 20px;
    display: flex;
    flex-direction: column;
    gap: 14px;
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .icon {
    font-size: 1.1rem;
  }

  .card-header h4 {
    font-size: 1rem;
    font-weight: 700;
    color: var(--text-primary);
  }

  .badge-total {
    background: var(--bg-card);
    color: var(--text-secondary);
    padding: 2px 8px;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 700;
  }

  .participantes-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .participante-row {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-sm);
    padding: 10px 14px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .participante-info {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .apelido {
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text-primary);
  }

  .apelido-eu {
    color: var(--texto-contraste);
    font-weight: 700;
  }

  .eu-tag {
    font-size: 0.8rem;
    color: var(--accent-orange);
    font-weight: 600;
    margin-left: 4px;
  }

  .empty-text {
    font-size: 0.88rem;
    color: var(--text-muted);
    text-align: center;
    padding: 12px 0;
  }
</style>
