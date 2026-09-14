<script>
  import { fade } from 'svelte/transition';
  import ListaPresentes from './ListaPresentes.svelte';
  import Placar from './Placar.svelte';

  let {
    quadra,
    eu,
    participantes = [],
    estadoPartida = null,
    wsConectado = false,
    onMarcarPonto = () => {},
    onDesfazerPonto = () => {},
    onVoltar,
  } = $props();

  const podeControlar = $derived(
    eu?.papel === 'ADMIN' || eu?.papel === 'CONTROLADOR'
  );
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

  <!-- Placar Interativo em Tempo Real (US2 & US3) -->
  <Placar
    {estadoPartida}
    {podeControlar}
    desabilitado={!wsConectado}
    {onMarcarPonto}
    {onDesfazerPonto}
  />

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
</style>
