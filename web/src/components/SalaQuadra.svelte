<script>
  import { fade, slide } from 'svelte/transition';
  import ListaPresentes from './ListaPresentes.svelte';
  import Placar from './Placar.svelte';
  import PlacarManual from './PlacarManual.svelte';
  import LinhaDoTempo from './LinhaDoTempo.svelte';

  let {
    quadra,
    eu,
    participantes = [],
    estadoPartida = null,
    linhaDoTempo = [],
    wsConectado = false,
    onMarcarPonto = () => {},
    onDesfazerPonto = () => {},
    onVoltar,
  } = $props();

  let modalLinhaDoTempoAberto = $state(false);
  let prefersReducedMotion = $state(false);

  const podeControlar = $derived(
    eu?.papel === 'ADMIN' || eu?.papel === 'CONTROLADOR'
  );

  // Modo Imersivo ativo por padrão para espectadores (US5)
  let modoImersivo = $state(true);
  let timerInatividade = null;

  $effect(() => {
    if (typeof window !== 'undefined') {
      const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
      prefersReducedMotion = mq.matches;
      const handler = (e) => {
        prefersReducedMotion = e.matches;
      };
      mq.addEventListener('change', handler);
      return () => mq.removeEventListener('change', handler);
    }
  });

  // Atualiza estado imersivo caso o papel mude dinamicamente
  $effect(() => {
    if (podeControlar) {
      modoImersivo = false;
      if (timerInatividade) clearTimeout(timerInatividade);
    }
  });

  // Gerencia a revelação dos controles e retorno ao modo imersivo após 3s (US5)
  function tratarInteracaoUsuario(event) {
    if (podeControlar) return;

    // Se estava em modo imersivo, sai dele
    if (modoImersivo) {
      modoImersivo = false;
    }

    // Reinicia o temporizador de 3 segundos de inatividade
    if (timerInatividade) {
      clearTimeout(timerInatividade);
    }

    timerInatividade = setTimeout(() => {
      // Retorna ao modo imersivo apenas se nenhum modal estiver aberto
      if (!modalLinhaDoTempoAberto) {
        modoImersivo = true;
      }
    }, 3000);
  }

  function handleAbrirLinhaDoTempo() {
    if (timerInatividade) {
      clearTimeout(timerInatividade);
    }
    modalLinhaDoTempoAberto = true;
  }

  function handleFecharLinhaDoTempo() {
    modalLinhaDoTempoAberto = false;
    if (!podeControlar) {
      tratarInteracaoUsuario();
    }
  }

  $effect(() => {
    return () => {
      if (timerInatividade) clearTimeout(timerInatividade);
    };
  });
</script>

<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
<!-- svelte-ignore a11y_click_events_have_key_events -->
<div
  class="sala-container {modoImersivo && !podeControlar ? 'em-modo-imersivo' : ''}"
  in:fade={{ duration: 200 }}
  onclick={tratarInteracaoUsuario}
  onpointerdown={tratarInteracaoUsuario}
  onkeydown={(e) => {
    if (e.key === 'Enter' || e.key === ' ' || e.key === 'Escape') {
      tratarInteracaoUsuario(e);
    }
  }}
  tabindex="-1"
  role="region"
  aria-label="Quadra de Vôlei"
>
  <!-- Top Bar com Botão Voltar e Status de Conexão -->
  {#if podeControlar || !modoImersivo}
    <header class="sala-header" in:slide={{ duration: 200 }} out:slide={{ duration: 200 }}>
      <button
        type="button"
        class="btn-voltar"
        onclick={onVoltar}
        aria-label="Voltar para a lista de quadras"
      >
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

    <!-- Quadra Title & Meu Perfil -->
    <section class="quadra-hero" in:slide={{ duration: 200 }} out:slide={{ duration: 200 }}>
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
  {/if}

  <!-- Exibição do Placar -->
  {#if podeControlar}
    <!-- Placar do Controlador com Botões Grandes de Marcação e Desfazer -->
    <Placar
      {estadoPartida}
      {podeControlar}
      desabilitado={!wsConectado}
      {onMarcarPonto}
      {onDesfazerPonto}
      onAbrirLinhaDoTempo={handleAbrirLinhaDoTempo}
    />
  {:else}
    <!-- Placar Dobrável Manual Retrô do Espectador (US5) -->
    <PlacarManual
      {estadoPartida}
      {quadra}
      {prefersReducedMotion}
      {modoImersivo}
      onAbrirLinhaDoTempo={handleAbrirLinhaDoTempo}
    />
  {/if}

  <!-- Modal/Gaveta da Linha do Tempo (CV1.DS4.US1) -->
  {#if modalLinhaDoTempoAberto}
    <LinhaDoTempo
      itens={linhaDoTempo}
      equipeA={estadoPartida?.equipe_a || 'Equipe A'}
      equipeB={estadoPartida?.equipe_b || 'Equipe B'}
      pontosA={estadoPartida?.pontos_a ?? 0}
      pontosB={estadoPartida?.pontos_b ?? 0}
      onFechar={handleFecharLinhaDoTempo}
    />
  {/if}

  <!-- Lista de Participantes em Tempo Real (oculta em modo imersivo) -->
  {#if podeControlar || !modoImersivo}
    <div in:slide={{ duration: 200 }} out:slide={{ duration: 200 }}>
      <ListaPresentes {participantes} euId={eu?.id} />
    </div>
  {/if}
</div>

<style>
  .sala-container {
    padding: 18px 20px 32px 20px;
    display: flex;
    flex-direction: column;
    gap: 22px;
    min-height: 100vh;
    transition: padding 0.25s ease;
  }

  .sala-container.em-modo-imersivo {
    padding: 12px 16px;
    justify-content: center;
    cursor: pointer;
    gap: 0;
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
