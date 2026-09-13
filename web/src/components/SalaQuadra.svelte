<script>
  import { fade, slide } from 'svelte/transition';
  import ListaPresentes from './ListaPresentes.svelte';

  let { quadra, eu, participantes = [], wsConectado = false, onVoltar } = $props();
</script>

<div class="sala-container" in:fade={{ duration: 200 }}>
  <!-- Top Bar -->
  <header class="sala-header">
    <button class="btn-voltar" onclick={onVoltar}>
      <span class="seta">←</span>
      <span>Quadras</span>
    </button>

    <div class="ws-status">
      <span
        class="status-dot {wsConectado ? 'status-online' : 'status-offline'}"
      ></span>
      <span class="ws-text">{wsConectado ? 'Ao vivo' : 'Conectando...'}</span>
    </div>
  </header>

  <!-- Quadra Title & My Role -->
  <section class="quadra-hero">
    <div class="quadra-title-row">
      <span class="quadra-tag">
        🏟️ {quadra.arena_nome ? quadra.arena_nome + ' • ' : ''}Quadra Ativa
      </span>
      <h2 class="quadra-title">{quadra.nome}</h2>
    </div>

    <div class="meu-perfil-card">
      <div class="meu-perfil-info">
        <span class="label-voce">Você está conectado como:</span>
        <span class="meu-apelido">{eu?.apelido || 'Participante'}</span>
      </div>
      <span class="badge {eu?.papel === 'ADMIN' ? 'badge-admin' : 'badge-espectador'}">
        {eu?.papel || 'ESPECTADOR'}
      </span>
    </div>
  </section>

  <!-- Partida Status Placeholder (US1 foundation, US2 adds interactive scoring) -->
  <section class="partida-card" in:slide>
    <div class="partida-header">
      <span class="partida-badge">Set Único</span>
      <span class="partida-regra">Alvo: 12 pts (Vantagem de 2)</span>
    </div>

    <div class="placar-preview">
      <div class="time-col">
        <span class="time-nome">Equipe A</span>
        <span class="pontos-display">0</span>
      </div>
      <span class="vs-divider">×</span>
      <div class="time-col">
        <span class="time-nome">Equipe B</span>
        <span class="pontos-display">0</span>
      </div>
    </div>

    <div class="partida-status-aviso">
      {#if eu?.papel === 'ADMIN'}
        <p>👑 Você é o <strong>Admin</strong> desta quadra. A marcação de pontos em tempo real será liberada na próxima entrega (US2).</p>
      {:else}
        <p>👀 Você é <strong>Espectador</strong>. O placar sincronizará em tempo real no seu celular assim que os pontos forem marcados.</p>
      {/if}
    </div>
  </section>

  <!-- Lista de Participantes em Tempo Real -->
  <ListaPresentes {participantes} euId={eu?.id} />
</div>

<style>
  .sala-container {
    padding: 18px 20px 32px 20px;
    display: flex;
    flex-direction: column;
    gap: 22px;
  }

  .sala-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .btn-voltar {
    background: transparent;
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.95rem;
    padding: 8px 10px;
    border-radius: var(--radius-sm);
  }

  .btn-voltar:hover {
    color: var(--text-primary);
    background: var(--bg-surface);
  }

  .seta {
    font-size: 1.1rem;
  }

  .ws-status {
    display: flex;
    align-items: center;
    gap: 6px;
    background: var(--bg-surface);
    padding: 6px 12px;
    border-radius: 999px;
    border: 1px solid var(--border-color);
  }

  .ws-text {
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--text-secondary);
  }

  .quadra-hero {
    display: flex;
    flex-direction: column;
    gap: 14px;
  }

  .quadra-tag {
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--accent-orange);
    letter-spacing: 0.05em;
  }

  .quadra-title {
    font-size: 1.7rem;
    font-weight: 800;
    color: #ffffff;
    line-height: 1.2;
  }

  .meu-perfil-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 14px 18px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .meu-perfil-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .label-voce {
    font-size: 0.78rem;
    color: var(--text-muted);
  }

  .meu-apelido {
    font-size: 1.15rem;
    font-weight: 700;
    color: #ffffff;
  }

  /* Partida card */
  .partida-card {
    background: linear-gradient(180deg, var(--bg-card) 0%, var(--bg-surface) 100%);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: 22px 20px;
    display: flex;
    flex-direction: column;
    gap: 18px;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.25);
  }

  .partida-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .partida-badge {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--accent-cyan);
    letter-spacing: 0.05em;
  }

  .partida-regra {
    font-size: 0.8rem;
    color: var(--text-muted);
    font-weight: 500;
  }

  .placar-preview {
    display: flex;
    align-items: center;
    justify-content: space-around;
    padding: 10px 0;
  }

  .time-col {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
  }

  .time-nome {
    font-size: 0.92rem;
    font-weight: 600;
    color: var(--text-secondary);
  }

  .pontos-display {
    font-family: var(--font-display);
    font-size: 4.5rem;
    font-weight: 700;
    line-height: 1;
    color: #ffffff;
  }

  .vs-divider {
    font-size: 1.5rem;
    color: var(--text-muted);
    font-weight: 600;
  }

  .partida-status-aviso {
    background: rgba(0, 0, 0, 0.2);
    border-radius: var(--radius-sm);
    padding: 10px 14px;
    font-size: 0.85rem;
    color: var(--text-secondary);
    line-height: 1.4;
  }

  .partida-status-aviso strong {
    color: #ffffff;
  }
</style>
