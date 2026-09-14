<script>
  import { slide, fade } from 'svelte/transition';

  let { participantes = [], euId = null, prefersReducedMotion = false, podeAutorizar = false, desabilitado = false, onAutorizarAdmin = (id) => {} } = $props();
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

          {#if podeAutorizar && p.papel !== 'ADMIN'}
            <button class="autorizar" disabled={desabilitado} onclick={() => onAutorizarAdmin(p.id)} aria-label={`Autorizar ${p.apelido} como admin`}>Tornar admin</button>
          {/if}
          <span class="badge {p.papel === 'ADMIN' ? 'badge-admin' : 'badge-espectador'}">
            {p.papel}
          </span>
        </div>
      {/each}
    {/if}
  </div>
</div>

<style>
  .autorizar { min-height: 44px; padding: 8px 12px; border-radius: 8px; border: 1px solid #38bdf8; background: transparent; color: #38bdf8; cursor: pointer; }
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
    color: #ffffff;
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
