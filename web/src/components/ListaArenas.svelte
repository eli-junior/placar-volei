<script>
  import { slide, fade } from 'svelte/transition';

  let { arenas = [], onSelectArena, onAbrirCriar, loading = false } = $props();
</script>

<div class="container" in:fade={{ duration: 200 }}>
  <header class="header">
    <div class="brand">
      <span class="brand-icon">🏐</span>
      <h1 class="brand-title">Placar Vôlei</h1>
    </div>
    <p class="brand-subtitle">Escolha a arena ou clube onde você está jogando</p>
  </header>

  <div class="actions">
    <button class="btn-primary" onclick={onAbrirCriar}>
      <span class="btn-icon">+</span>
      <span>Criar Nova Arena</span>
    </button>
  </div>

  <section class="arenas-section">
    <div class="section-header">
      <h2>Arenas Disponíveis</h2>
      <span class="count-badge">{arenas.length}</span>
    </div>

    {#if loading}
      <div class="empty-state" in:fade>
        <p>Carregando arenas...</p>
      </div>
    {:else if arenas.length === 0}
      <div class="empty-state" in:fade>
        <p>Nenhuma arena cadastrada ainda.</p>
        <p class="empty-sub">Crie a primeira arena (ex: T9 Beach Club) para adicionar suas quadras!</p>
      </div>
    {:else}
      <div class="arenas-list">
        {#each arenas as arena (arena.id)}
          <button
            class="arena-card"
            onclick={() => onSelectArena(arena)}
            in:slide={{ duration: 250 }}
          >
            <div class="arena-left">
              <span class="arena-icon">🏟️</span>
              <div class="arena-info">
                <h3 class="arena-nome">{arena.nome}</h3>
                <span class="arena-detalhes">
                  {arena.quadras_count} {arena.quadras_count === 1 ? 'quadra ativa' : 'quadras ativas'}
                </span>
              </div>
            </div>

            <div class="arena-action">
              <span class="btn-label">Ver Quadras</span>
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
    padding: 24px 20px;
    display: flex;
    flex-direction: column;
    gap: 28px;
  }

  .header {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding-top: 12px;
  }

  .brand {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .brand-icon {
    font-size: 2rem;
  }

  .brand-title {
    font-family: var(--font-display);
    font-size: 2.75rem;
    font-weight: 700;
    line-height: 1;
    letter-spacing: 0.03em;
    background: linear-gradient(135deg, #ffffff 40%, #f97316 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
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

  .arenas-section {
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

  .arenas-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .arena-card {
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

  .arena-card:hover {
    background: var(--bg-card-hover);
    border-color: var(--border-active);
  }

  .arena-left {
    display: flex;
    align-items: center;
    gap: 14px;
  }

  .arena-icon {
    font-size: 1.8rem;
  }

  .arena-info {
    display: flex;
    flex-direction: column;
    gap: 3px;
  }

  .arena-nome {
    font-size: 1.15rem;
    font-weight: 700;
    color: #ffffff;
  }

  .arena-detalhes {
    font-size: 0.85rem;
    color: var(--text-secondary);
  }

  .arena-action {
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

  .arena-card:hover .arrow {
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
