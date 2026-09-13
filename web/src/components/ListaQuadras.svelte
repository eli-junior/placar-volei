<script>
  import { slide, fade } from 'svelte/transition';

  let {
    arena,
    quadras = [],
    onSelectQuadra,
    onAbrirCriar,
    onVoltarArenas,
    loading = false,
  } = $props();
</script>

<div class="container" in:fade={{ duration: 200 }}>
  <!-- Top Navigation -->
  <div class="top-nav">
    <button class="btn-voltar" onclick={onVoltarArenas}>
      <span class="seta">←</span>
      <span>Outras Arenas</span>
    </button>
  </div>

  <!-- Arena Header -->
  <header class="header">
    <div class="arena-tag">
      <span>🏟️ Arena Selecionada</span>
    </div>
    <h1 class="arena-title">{arena?.nome || 'Arena'}</h1>
    <p class="brand-subtitle">Escolha uma quadra para acompanhar ou marcar os pontos</p>
  </header>

  <div class="actions">
    <button class="btn-primary" onclick={onAbrirCriar}>
      <span class="btn-icon">+</span>
      <span>Criar Nova Quadra</span>
    </button>
  </div>

  <section class="quadras-section">
    <div class="section-header">
      <h2>Quadras em Andamento</h2>
      <span class="count-badge">{quadras.length}</span>
    </div>

    {#if loading}
      <div class="empty-state" in:fade>
        <p>Carregando quadras...</p>
      </div>
    {:else if quadras.length === 0}
      <div class="empty-state" in:fade>
        <p>Nenhuma quadra ativa nesta arena.</p>
        <p class="empty-sub">Clique em "+ Criar Nova Quadra" para abrir a primeira partida aqui!</p>
      </div>
    {:else}
      <div class="quadras-list">
        {#each quadras as quadra (quadra.id)}
          <button
            class="quadra-card"
            onclick={() => onSelectQuadra(quadra)}
            in:slide={{ duration: 250 }}
          >
            <div class="quadra-info">
              <h3 class="quadra-nome">{quadra.nome}</h3>
              <span class="quadra-participantes">
                👥 {quadra.participantes_count} {quadra.participantes_count === 1 ? 'presente' : 'presentes'}
              </span>
            </div>
            <div class="quadra-action">
              <span class="btn-entrar-label">Entrar</span>
              <span class="arrow">→</span>
            </div>
          </button>
        {/each}
      </div>
    {/if}
  </section>
</div>

<style>
  .container {
    padding: 18px 20px 32px 20px;
    display: flex;
    flex-direction: column;
    gap: 22px;
  }

  .top-nav {
    display: flex;
    align-items: center;
  }

  .btn-voltar {
    background: transparent;
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.92rem;
    padding: 6px 8px;
    border-radius: var(--radius-sm);
  }

  .btn-voltar:hover {
    color: var(--text-primary);
    background: var(--bg-surface);
  }

  .seta {
    font-size: 1.1rem;
  }

  .header {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .arena-tag {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--accent-orange);
    letter-spacing: 0.05em;
  }

  .arena-title {
    font-size: 2.1rem;
    font-weight: 800;
    line-height: 1.15;
    color: #ffffff;
  }

  .brand-subtitle {
    color: var(--text-secondary);
    font-size: 0.92rem;
  }

  .actions {
    display: flex;
    flex-direction: column;
  }

  .btn-primary {
    background: linear-gradient(135deg, var(--accent-orange), #ea580c);
    color: #ffffff;
    font-size: 1.1rem;
    padding: 16px 20px;
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    box-shadow: 0 4px 20px rgba(249, 115, 22, 0.35);
  }

  .btn-icon {
    font-size: 1.4rem;
    line-height: 1;
  }

  .quadras-section {
    display: flex;
    flex-direction: column;
    gap: 14px;
  }

  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .section-header h2 {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-primary);
  }

  .count-badge {
    background: var(--bg-surface);
    color: var(--text-secondary);
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 700;
  }

  .quadras-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .quadra-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 18px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    text-align: left;
    color: var(--text-primary);
    transition: transform 0.15s ease, border-color 0.2s ease, background-color 0.2s ease;
  }

  .quadra-card:hover {
    background: var(--bg-card-hover);
    border-color: var(--border-active);
  }

  .quadra-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .quadra-nome {
    font-size: 1.15rem;
    font-weight: 700;
    color: #ffffff;
  }

  .quadra-participantes {
    font-size: 0.85rem;
    color: var(--text-secondary);
  }

  .quadra-action {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--accent-orange);
    font-weight: 600;
    font-size: 0.95rem;
  }

  .arrow {
    font-size: 1.2rem;
    transition: transform 0.15s ease;
  }

  .quadra-card:hover .arrow {
    transform: translateX(3px);
  }

  .empty-state {
    background: var(--bg-surface);
    border: 1px dashed var(--border-color);
    border-radius: var(--radius-md);
    padding: 36px 20px;
    text-align: center;
    color: var(--text-secondary);
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .empty-sub {
    font-size: 0.85rem;
    color: var(--text-muted);
  }
</style>
