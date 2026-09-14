<script>
  import { fly, fade, slide } from 'svelte/transition';
  import CartaoDobravel from './CartaoDobravel.svelte';

  let {
    estadoPartida = null,
    podeControlar = false,
    desabilitado = false,
    onMarcarPonto = () => {},
    onDesfazerPonto = () => {},
    onIniciarNovaPartida = () => {},
    onAbrirLinhaDoTempo = () => {},
  } = $props();

  let submetendo = $state(false);
  let feedbackEquipe = $state(null);
  let feedbackTimer = null;
  let prefersReducedMotion = $state(false);

  async function handleIniciarNovaPartida() {
    if (submetendo || desabilitado) return;
    try {
      submetendo = true;
      await onIniciarNovaPartida();
    } finally {
      setTimeout(() => {
        submetendo = false;
      }, 250);
    }
  }

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

  const pontosA = $derived(estadoPartida?.pontos_a ?? 0);
  const pontosB = $derived(estadoPartida?.pontos_b ?? 0);
  const totalPontos = $derived(pontosA + pontosB);
  const podeDesfazer = $derived(
    podeControlar && totalPontos > 0 && !desabilitado && !submetendo
  );

  const equipeA = $derived(estadoPartida?.equipe_a || 'Equipe A');
  const equipeB = $derived(estadoPartida?.equipe_b || 'Equipe B');
  const alvo = $derived(estadoPartida?.alvo ?? 12);
  const vantagem = $derived(estadoPartida?.vantagem ?? true);
  const teto = $derived(estadoPartida?.teto ?? null);
  const encerrada = $derived(estadoPartida?.encerrada ?? false);
  const vencedor = $derived(estadoPartida?.vencedor ?? null);

  const vencedorNome = $derived(
    vencedor === 'A' ? equipeA : vencedor === 'B' ? equipeB : null
  );

  async function handleToqueDesfazer() {
    if (!podeDesfazer || submetendo) return;

    if (typeof navigator !== 'undefined' && navigator.vibrate) {
      try {
        navigator.vibrate(30);
      } catch {}
    }

    try {
      submetendo = true;
      await onDesfazerPonto();
    } finally {
      setTimeout(() => {
        submetendo = false;
      }, 250);
    }
  }

  async function handleToquePonto(equipe) {
    if (submetendo || desabilitado || encerrada) return;

    // Feedback háptico tátil leve no celular (se suportado pelo navegador)
    if (typeof navigator !== 'undefined' && navigator.vibrate) {
      try {
        navigator.vibrate(35);
      } catch {}
    }

    // Feedback visual imediato no card da equipe
    feedbackEquipe = equipe;
    if (feedbackTimer) clearTimeout(feedbackTimer);
    feedbackTimer = setTimeout(() => {
      feedbackEquipe = null;
    }, 300);

    try {
      submetendo = true;
      await onMarcarPonto(equipe);
    } finally {
      // Debounce curto para evitar duplo toque acidental
      setTimeout(() => {
        submetendo = false;
      }, 250);
    }
  }
</script>

<section class="placar-card" in:slide={{ duration: prefersReducedMotion ? 0 : 250 }}>
  <!-- Cabeçalho de regras da partida e botão Linha do Tempo -->
  <div class="placar-header">
    <div class="header-left">
      <span class="placar-badge">Set Único</span>
      <span class="placar-regra">
        Alvo: {alvo} pts
        {#if vantagem}• Vantagem{/if}
        {#if teto}• Teto: {teto}{/if}
      </span>
    </div>

    <button
      type="button"
      class="btn-lt-toggle"
      onclick={onAbrirLinhaDoTempo}
      aria-label="Abrir linha do tempo da partida"
    >
      <span class="lt-icon">📜</span>
      <span class="lt-label">Linha do Tempo</span>
    </button>
  </div>

  <!-- Banner de encerramento quando houver vencedor -->
  {#if encerrada && vencedorNome}
    <div class="banner-vitoria" in:slide={{ duration: prefersReducedMotion ? 0 : 250 }}>
      <div class="vitoria-cabecalho">
        <span class="trofeu">🏆</span>
        <div class="vitoria-texto">
          <span class="vitoria-titulo">Fim de Jogo!</span>
          <span class="vitoria-vencedor">Vitória da {vencedorNome}</span>
        </div>
      </div>

      {#if podeControlar}
        <button
          type="button"
          class="btn-nova-partida"
          disabled={desabilitado || submetendo}
          onclick={handleIniciarNovaPartida}
          aria-label="Iniciar Nova Partida"
        >
          <span class="icone-nova-partida">▶</span>
          <span class="texto-nova-partida">Iniciar Nova Partida</span>
        </button>
      {:else}
        <div class="aguardando-container">
          <span class="aguardando-nova-partida">Aguardando início da próxima partida…</span>
        </div>
      {/if}
    </div>
  {/if}

  <!-- Área do Placar com Alvos Grandes para Uma Mão -->
  <div class="placar-grid">
    <!-- Coluna Equipe A -->
    <div
      class="equipe-col {feedbackEquipe === 'A' ? 'flash-a' : ''} {vencedor === 'A' ? 'col-vencedor' : ''}"
    >
      <span class="equipe-nome">{equipeA}</span>

      <CartaoDobravel
        valor={pontosA}
        equipe={equipeA}
        tema="a"
        tamanho="normal"
        {prefersReducedMotion}
      />

      {#if podeControlar}
        <button
          type="button"
          class="btn-marcar btn-marcar-a"
          disabled={desabilitado || encerrada || submetendo}
          onclick={() => handleToquePonto('A')}
          aria-label="Marcar ponto para {equipeA}"
        >
          <span class="btn-plus">+1</span>
          <span class="btn-sub">{equipeA}</span>
        </button>
      {/if}
    </div>

    <!-- Divisor Central -->
    <div class="vs-col {podeControlar ? 'vs-com-botoes' : ''}">
      <span class="vs-simbolo">×</span>
    </div>

    <!-- Coluna Equipe B -->
    <div
      class="equipe-col {feedbackEquipe === 'B' ? 'flash-b' : ''} {vencedor === 'B' ? 'col-vencedor' : ''}"
    >
      <span class="equipe-nome">{equipeB}</span>

      <CartaoDobravel
        valor={pontosB}
        equipe={equipeB}
        tema="b"
        tamanho="normal"
        {prefersReducedMotion}
      />

      {#if podeControlar}
        <button
          type="button"
          class="btn-marcar btn-marcar-b"
          disabled={desabilitado || encerrada || submetendo}
          onclick={() => handleToquePonto('B')}
          aria-label="Marcar ponto para {equipeB}"
        >
          <span class="btn-plus">+1</span>
          <span class="btn-sub">{equipeB}</span>
        </button>
      {/if}
    </div>
  </div>

  {#if podeControlar}
    <!-- Ação de Correção: Desfazer Último Ponto (US3) -->
    <div class="desfazer-container">
      <button
        type="button"
        class="btn-desfazer"
        disabled={!podeDesfazer}
        onclick={handleToqueDesfazer}
        aria-label="Desfazer último ponto marcado"
      >
        <span class="desfazer-icone">↺</span>
        <span class="desfazer-texto">Desfazer Último Ponto</span>
      </button>
    </div>
  {/if}
</section>

<style>
  .placar-card {
    background: linear-gradient(180deg, var(--bg-card) 0%, var(--bg-surface) 100%);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: 20px 16px 24px 16px;
    display: flex;
    flex-direction: column;
    gap: 18px;
    box-shadow: 0 4px 28px rgba(0, 0, 0, 0.35);
  }

  .placar-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 4px;
    gap: 10px;
    flex-wrap: wrap;
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }

  .btn-lt-toggle {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: var(--text-secondary);
    border-radius: 999px;
    padding: 4px 12px;
    font-size: 0.78rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 6px;
    cursor: pointer;
    touch-action: manipulation;
    transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease, transform 0.1s ease;
  }

  .btn-lt-toggle:hover {
    background: rgba(255, 255, 255, 0.1);
    color: #ffffff;
    border-color: rgba(255, 255, 255, 0.25);
  }

  .btn-lt-toggle:active {
    transform: scale(0.96);
  }

  .lt-icon {
    font-size: 0.85rem;
  }

  .lt-label {
    letter-spacing: 0.02em;
  }

  .placar-badge {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--accent-cyan);
    letter-spacing: 0.05em;
  }

  .placar-regra {
    font-size: 0.8rem;
    color: var(--text-muted);
    font-weight: 500;
  }

  /* Banner de Vitória */
  .banner-vitoria {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.25) 0%, rgba(234, 88, 12, 0.25) 100%);
    border: 1.5px solid var(--accent-orange);
    border-radius: var(--radius-md);
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    box-shadow: 0 4px 20px rgba(245, 158, 11, 0.2);
  }

  .vitoria-cabecalho {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .trofeu {
    font-size: 2rem;
    line-height: 1;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
  }

  .vitoria-texto {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .vitoria-titulo {
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--accent-orange);
    letter-spacing: 0.08em;
  }

  .vitoria-vencedor {
    font-size: 1.15rem;
    font-weight: 800;
    color: #ffffff;
  }

  .btn-nova-partida {
    background: linear-gradient(135deg, #f59e0b 0%, #ea580c 100%);
    color: #ffffff;
    border: none;
    border-radius: var(--radius-md);
    padding: 12px 18px;
    font-size: 1rem;
    font-weight: 700;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    box-shadow: 0 4px 14px rgba(234, 88, 12, 0.45);
    transition: transform 0.15s ease, filter 0.15s ease;
    width: 100%;
  }

  .btn-nova-partida:hover:not(:disabled) {
    filter: brightness(1.1);
    transform: translateY(-1px);
  }

  .btn-nova-partida:active:not(:disabled) {
    transform: scale(0.98);
  }

  .btn-nova-partida:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .icone-nova-partida {
    font-size: 0.9rem;
  }

  .texto-nova-partida {
    letter-spacing: 0.02em;
  }

  .aguardando-container {
    padding: 4px 0 0 0;
  }

  .aguardando-nova-partida {
    font-size: 0.85rem;
    color: var(--text-secondary);
    font-style: italic;
  }

  /* Grid Principal do Placar */
  .placar-grid {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: center;
    gap: 12px;
  }

  .equipe-col {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: var(--radius-md);
    padding: 14px 10px;
    transition: background 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
  }

  .equipe-col.flash-a {
    background: rgba(6, 182, 212, 0.12);
    border-color: var(--accent-cyan);
    box-shadow: 0 0 16px rgba(6, 182, 212, 0.3);
  }

  .equipe-col.flash-b {
    background: rgba(249, 115, 22, 0.12);
    border-color: var(--accent-orange);
    box-shadow: 0 0 16px rgba(249, 115, 22, 0.3);
  }

  .equipe-col.col-vencedor {
    border-color: rgba(245, 158, 11, 0.5);
    background: rgba(245, 158, 11, 0.08);
  }

  .equipe-nome {
    font-size: 0.88rem;
    font-weight: 700;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    text-align: center;
    max-width: 120px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }


  .vs-col {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .vs-col.vs-com-botoes {
    padding-bottom: 74px; /* alinha com os números */
  }

  .vs-simbolo {
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--text-muted);
  }

  /* Botões Grandes para Uma Mão */
  .btn-marcar {
    width: 100%;
    height: 86px;
    border-radius: var(--radius-md);
    border: none;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 2px;
    cursor: pointer;
    touch-action: manipulation;
    user-select: none;
    transition: transform 0.12s ease, filter 0.12s ease, box-shadow 0.12s ease;
  }

  .btn-marcar:active:not(:disabled) {
    transform: scale(0.95);
    filter: brightness(1.15);
  }

  .btn-marcar:disabled {
    opacity: 0.35;
    cursor: not-allowed;
    transform: none;
    filter: grayscale(0.6);
  }

  .btn-marcar-a {
    background: linear-gradient(135deg, #0891b2 0%, #06b6d4 100%);
    color: #ffffff;
    box-shadow: 0 4px 14px rgba(6, 182, 212, 0.3);
  }

  .btn-marcar-a:hover:not(:disabled) {
    box-shadow: 0 6px 20px rgba(6, 182, 212, 0.45);
  }

  .btn-marcar-b {
    background: linear-gradient(135deg, #ea580c 0%, #f97316 100%);
    color: #ffffff;
    box-shadow: 0 4px 14px rgba(249, 115, 22, 0.3);
  }

  .btn-marcar-b:hover:not(:disabled) {
    box-shadow: 0 6px 20px rgba(249, 115, 22, 0.45);
  }

  .btn-plus {
    font-size: 2.2rem;
    font-weight: 800;
    line-height: 1;
  }

  .btn-sub {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    opacity: 0.9;
  }

  @media (prefers-reduced-motion: reduce) {
    .btn-marcar,
    .btn-desfazer {
      transition: none !important;
    }
  }

  /* Estilos do Botão Desfazer (US3) */
  .desfazer-container {
    display: flex;
    justify-content: center;
    padding-top: 4px;
  }

  .btn-desfazer {
    width: 100%;
    height: 48px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    font-size: 0.92rem;
    font-weight: 600;
    cursor: pointer;
    touch-action: manipulation;
    user-select: none;
    transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease, transform 0.1s ease;
  }

  .btn-desfazer:hover:not(:disabled) {
    background: rgba(255, 255, 255, 0.08);
    color: #ffffff;
    border-color: rgba(255, 255, 255, 0.2);
  }

  .btn-desfazer:active:not(:disabled) {
    transform: scale(0.98);
    background: rgba(255, 255, 255, 0.1);
  }

  .btn-desfazer:disabled {
    opacity: 0.35;
    cursor: not-allowed;
  }

  .desfazer-icone {
    font-size: 1.15rem;
    font-weight: 700;
    line-height: 1;
  }

  .desfazer-texto {
    letter-spacing: 0.02em;
  }

  /*
   * Celular deitado: a altura é o recurso escasso. Compacta a moldura e os
   * botões para que placar, +1 e desfazer caibam sem rolagem.
   */
  @media (orientation: landscape) and (max-height: 500px) {
    .placar-card {
      padding: 12px 14px 14px 14px;
      gap: 10px;
    }

    .placar-header {
      gap: 8px;
    }

    .placar-grid {
      gap: 10px;
    }

    .equipe-col {
      padding: 8px 10px;
      gap: 6px;
    }

    .btn-marcar {
      height: 60px;
    }

    .btn-plus {
      font-size: 1.7rem;
    }

    .vs-col.vs-com-botoes {
      padding-bottom: 50px;
    }

    .btn-desfazer {
      height: 42px;
      font-size: 0.85rem;
    }

    .banner-vitoria {
      padding: 8px 14px;
    }

    .trofeu {
      font-size: 1.4rem;
    }
  }
</style>
