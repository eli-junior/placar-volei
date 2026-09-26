<script>
  import { fly, fade, slide } from 'svelte/transition';
  import CartaoDobravel from './CartaoDobravel.svelte';
  import PlacarResultado from './PlacarResultado.svelte';

  let {
    estadoPartida = null,
    temaPlacar = 'esportivo',
    podeControlar = false,
    // `desabilitado` = não dá para agir agora (socket caído ou sem controle).
    desabilitado = false,
    // `enviando` = há comando em voo. Não bloqueia o toque seguinte: apenas
    // pinta o botão de "processando" (aria-busy + pulso).
    enviando = false,
    // Quantos toques já aceitos ainda aguardam resposta do servidor.
    pendentes = 0,
    onMarcarPonto = () => {},
    onDesfazerPonto = () => {},
    onIniciarNovaPartida = () => {},
    onAbrirLinhaDoTempo = () => {},
    onAbrirConfiguracao = () => {},
    onAbrirCompartilhar = () => {},
    ladosInvertidos = false,
    onAlternarLados = () => {},
  } = $props();

  let feedbackEquipe = $state(null);
  let feedbackTimer = null;
  let prefersReducedMotion = $state(false);

  function handleIniciarNovaPartida() {
    if (enviando || desabilitado) return;
    onIniciarNovaPartida();
  }

  function vibrar(ms) {
    if (typeof navigator !== 'undefined' && navigator.vibrate) {
      try {
        navigator.vibrate(ms);
      } catch {}
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
  const podeDesfazer = $derived(podeControlar && totalPontos > 0 && !desabilitado);

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

  function handleToqueDesfazer() {
    if (!podeDesfazer) return;
    vibrar(30);
    onDesfazerPonto();
  }

  /*
   * Um toque nunca é engolido por já haver outro em voo: o comando é entregue
   * ao pai, que serializa a fila. Aqui só cuidamos do retorno imediato — vibração,
   * flash no card da equipe e `aria-busy` no botão enquanto o envio acontece.
   */
  function handleToquePonto(equipe) {
    if (desabilitado || encerrada) return;

    vibrar(35);

    feedbackEquipe = equipe;
    if (feedbackTimer) clearTimeout(feedbackTimer);
    feedbackTimer = setTimeout(() => {
      feedbackEquipe = null;
    }, 300);

    onMarcarPonto(equipe);
  }

  let anuncioAcessivel = $state('');
  let pontosAnteriores = { a: 0, b: 0 };
  let partidaIdAnterior = null;

  $effect(() => {
    const pA = pontosA;
    const pB = pontosB;
    const pId = estadoPartida?.id;
    const enc = encerrada;
    const venc = vencedorNome;

    if (partidaIdAnterior !== pId) {
      partidaIdAnterior = pId;
      pontosAnteriores = { a: pA, b: pB };
      return;
    }

    if (enc && venc) {
      anuncioAcessivel = `Fim de jogo! Vitória de ${venc}. Placar final: ${equipeA} ${pA}, ${equipeB} ${pB}.`;
    } else if (pA !== pontosAnteriores.a || pB !== pontosAnteriores.b) {
      if (pA > pontosAnteriores.a) {
        anuncioAcessivel = `Ponto para ${equipeA}! Placar: ${equipeA} ${pA}, ${equipeB} ${pB}.`;
      } else if (pB > pontosAnteriores.b) {
        anuncioAcessivel = `Ponto para ${equipeB}! Placar: ${equipeA} ${pA}, ${equipeB} ${pB}.`;
      } else {
        anuncioAcessivel = `Ponto desfeito. Placar: ${equipeA} ${pA}, ${equipeB} ${pB}.`;
      }
      pontosAnteriores = { a: pA, b: pB };
    }
  });
</script>

<section class="placar-card" in:slide={{ duration: prefersReducedMotion ? 0 : 250 }}>
  <!-- Anunciador dinâmico de acessibilidade WCAG (leitores de tela) -->
  <div class="sr-only" role="status" aria-live="polite" aria-atomic="true">
    {anuncioAcessivel}
  </div>

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

    <div class="header-right">
      {#if podeControlar}
        <button
          type="button"
          class="btn-cfg-toggle"
          onclick={onAbrirConfiguracao}
          aria-label="Configurar duplas e regras da partida"
          title="Configurar duplas e regras"
        >
          <span class="cfg-icon">⚙️</span>
          <span class="cfg-label">Duplas & Regras</span>
        </button>
      {/if}

      <button
        type="button"
        class="btn-inverter-lados"
        class:ativo={ladosInvertidos}
        onclick={onAlternarLados}
        aria-pressed={ladosInvertidos}
        aria-label="Inverter lados das equipes"
        title="Inverter lados das equipes nesta tela"
      >
        <span class="inverter-icon">⇄</span>
        <span class="inverter-label">{ladosInvertidos ? 'Lados Invertidos' : 'Inverter Lados'}</span>
      </button>

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
        <div class="vitoria-botoes">
          <button
            type="button"
            class="btn-nova-partida"
            disabled={desabilitado || enviando}
            aria-busy={enviando}
            onclick={handleIniciarNovaPartida}
            aria-label="Iniciar Próxima Partida e Trocar Duplas"
          >
            <span class="icone-nova-partida">▶</span>
            <span class="texto-nova-partida">Iniciar Próxima Partida</span>
          </button>
          <button
            type="button"
            class="btn-compartilhar-vitoria"
            onclick={onAbrirCompartilhar}
            aria-label="Compartilhar resultado da partida"
          >
            <span>📢 Compartilhar</span>
          </button>
        </div>
      {:else}
        <div class="aguardando-container">
          <span class="aguardando-nova-partida">Aguardando início da próxima partida…</span>
          <button
            type="button"
            class="btn-compartilhar-vitoria"
            onclick={onAbrirCompartilhar}
            aria-label="Compartilhar resultado da partida"
          >
            <span>📢 Compartilhar Resultado</span>
          </button>
        </div>
      {/if}
    </div>
  {/if}

  <!-- Estado do transporte: quem opera precisa saber se o toque saiu ou não -->
  {#if podeControlar && desabilitado}
    <div class="aviso-conexao" role="status">
      <span class="aviso-icone" aria-hidden="true">⟳</span>
      <span>
        Sem conexão com a sala. Os botões de ponto estão bloqueados e voltam
        sozinhos assim que a reconexão acontecer — nada é marcado às cegas.
      </span>
    </div>
  {:else if podeControlar && enviando}
    <div class="aviso-envio" role="status">
      <span class="aviso-icone pulsando" aria-hidden="true">●</span>
      <span>
        {pendentes > 1
          ? `Enviando ${pendentes} toques na fila…`
          : 'Enviando o toque…'}
      </span>
    </div>
  {/if}

  <!-- Área do placar; o tema é compartilhado pela sala. -->
  {#if temaPlacar === 'esportivo'}
    <div class="placar-esportivo-controle">
      <div class="resultado-esportivo">
        <PlacarResultado
          {pontosA}
          {pontosB}
          {equipeA}
          {equipeB}
          {ladosInvertidos}
          {vencedor}
          movimentoReduzido={prefersReducedMotion}
        />
      </div>
      {#if podeControlar}
        <div class="acoes-ponto" class:lados-invertidos={ladosInvertidos}>
          <button
            type="button"
            class="btn-marcar btn-marcar-a"
            disabled={desabilitado || encerrada}
            aria-busy={enviando}
            onclick={() => handleToquePonto('A')}
            aria-label="Marcar ponto para {equipeA}"
          ><span class="btn-plus">+1</span><span class="btn-sub">{equipeA}</span></button>
          <button
            type="button"
            class="btn-marcar btn-marcar-b"
            disabled={desabilitado || encerrada}
            aria-busy={enviando}
            onclick={() => handleToquePonto('B')}
            aria-label="Marcar ponto para {equipeB}"
          ><span class="btn-plus">+1</span><span class="btn-sub">{equipeB}</span></button>
        </div>
      {/if}
    </div>
  {:else}
  <div class="placar-grid" class:lados-invertidos={ladosInvertidos}>
    <!-- Coluna Equipe A -->
    <div
      class="equipe-col col-time-a {feedbackEquipe === 'A' ? 'flash-a' : ''} {vencedor === 'A' ? 'col-vencedor' : ''}"
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
          disabled={desabilitado || encerrada}
          aria-busy={enviando}
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
      class="equipe-col col-time-b {feedbackEquipe === 'B' ? 'flash-b' : ''} {vencedor === 'B' ? 'col-vencedor' : ''}"
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
          disabled={desabilitado || encerrada}
          aria-busy={enviando}
          onclick={() => handleToquePonto('B')}
          aria-label="Marcar ponto para {equipeB}"
        >
          <span class="btn-plus">+1</span>
          <span class="btn-sub">{equipeB}</span>
        </button>
      {/if}
    </div>
  </div>
  {/if}

  {#if podeControlar}
    <!-- Ação de Correção: Desfazer Último Ponto (US3) -->
    <div class="desfazer-container">
      <button
        type="button"
        class="btn-desfazer"
        disabled={!podeDesfazer}
        aria-busy={enviando}
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

  .placar-esportivo-controle {
    display: grid;
    grid-template-rows: minmax(320px, 1fr) auto;
    gap: 12px;
    min-height: 460px;
  }

  .resultado-esportivo { min-height: 0; }

  .acoes-ponto {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-areas: 'a b';
    gap: 12px;
  }

  .acoes-ponto.lados-invertidos { grid-template-areas: 'b a'; }
  .acoes-ponto .btn-marcar-a { grid-area: a; }
  .acoes-ponto .btn-marcar-b { grid-area: b; }

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

  .header-right {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }

  .btn-cfg-toggle,
  .btn-inverter-lados,
  .btn-lt-toggle {
    background: rgba(var(--veu), 0.05);
    border: 1px solid rgba(var(--veu), 0.12);
    color: var(--text-secondary);
    border-radius: 999px;
    padding: 6px 14px;
    min-height: 44px;
    box-sizing: border-box;
    font-size: 0.78rem;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    cursor: pointer;
    touch-action: manipulation;
    transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease, transform 0.1s ease;
  }

  .btn-cfg-toggle:hover,
  .btn-inverter-lados:hover,
  .btn-lt-toggle:hover {
    background: rgba(var(--veu), 0.1);
    color: var(--texto-contraste);
    border-color: rgba(var(--veu), 0.25);
  }

  .btn-inverter-lados.ativo {
    color: var(--accent-orange);
    border-color: var(--border-active);
    background: rgba(249, 115, 22, 0.12);
  }

  .btn-cfg-toggle:active,
  .btn-inverter-lados:active,
  .btn-lt-toggle:active {
    transform: scale(0.96);
  }

  .cfg-icon,
  .inverter-icon,
  .lt-icon {
    font-size: 0.85rem;
  }

  .cfg-label,
  .inverter-label,
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
    color: var(--texto-contraste);
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

  .vitoria-botoes {
    display: flex;
    gap: 8px;
    align-items: center;
    width: 100%;
  }

  .btn-compartilhar-vitoria {
    background: rgba(var(--veu), 0.08);
    border: 1px solid rgba(var(--veu), 0.2);
    color: var(--texto-contraste);
    border-radius: var(--radius-md);
    padding: 12px 14px;
    font-size: 0.88rem;
    font-weight: 700;
    cursor: pointer;
    white-space: nowrap;
    transition: all 0.15s ease;
  }

  .btn-compartilhar-vitoria:hover {
    background: rgba(var(--veu), 0.16);
    border-color: rgba(var(--veu), 0.35);
  }

  .aguardando-container {
    display: flex;
    flex-direction: column;
    gap: 8px;
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
    grid-template-areas: "time-a divisor time-b";
    align-items: center;
    gap: 12px;
  }

  .placar-grid.lados-invertidos {
    grid-template-areas: "time-b divisor time-a";
  }

  .col-time-a {
    grid-area: time-a;
  }

  .vs-col {
    grid-area: divisor;
  }

  .col-time-b {
    grid-area: time-b;
  }

  .equipe-col {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    background: rgba(var(--veu), 0.02);
    border: 1px solid rgba(var(--veu), 0.05);
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

  /* Avisos de transporte: conexão caída e envio em andamento */
  .aviso-conexao,
  .aviso-envio {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    border-radius: var(--radius-md);
    font-size: 0.85rem;
    font-weight: 600;
    line-height: 1.35;
  }

  .aviso-conexao {
    color: #fde68a;
    background: rgba(245, 158, 11, 0.14);
    border: 1px solid rgba(245, 158, 11, 0.45);
  }

  .aviso-envio {
    color: #a5f3fc;
    background: rgba(6, 182, 212, 0.12);
    border: 1px solid rgba(6, 182, 212, 0.35);
  }

  .aviso-icone {
    font-size: 1rem;
    line-height: 1;
    flex: 0 0 auto;
  }

  .aviso-conexao .aviso-icone {
    animation: girar-aviso 1.1s linear infinite;
  }

  .aviso-icone.pulsando {
    animation: pulsar-aviso 0.9s ease-in-out infinite;
  }

  @keyframes girar-aviso {
    to {
      transform: rotate(360deg);
    }
  }

  @keyframes pulsar-aviso {
    0%, 100% {
      opacity: 0.35;
    }
    50% {
      opacity: 1;
    }
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

  /*
   * Pulso de envio: o toque já saiu e o servidor ainda não respondeu. O botão
   * continua clicável de propósito — o próximo toque entra na fila.
   */
  .btn-marcar[aria-busy='true'],
  .btn-nova-partida[aria-busy='true'],
  .btn-desfazer[aria-busy='true'] {
    animation: pulso-envio 0.9s ease-in-out infinite;
  }

  .btn-marcar[aria-busy='true']::after {
    content: '';
    position: absolute;
    inset: auto 0 6px 0;
    height: 3px;
    margin: 0 auto;
    width: 38%;
    border-radius: 2px;
    background: rgba(var(--veu), 0.85);
    animation: pulso-envio 0.9s ease-in-out infinite;
  }

  .btn-marcar {
    position: relative;
  }

  @keyframes pulso-envio {
    0%, 100% {
      filter: brightness(1);
    }
    50% {
      filter: brightness(1.25);
    }
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

    /* Sem movimento, o estado de envio continua legível por contraste fixo. */
    .btn-marcar[aria-busy='true'],
    .btn-nova-partida[aria-busy='true'],
    .btn-desfazer[aria-busy='true'],
    .btn-marcar[aria-busy='true']::after,
    .aviso-conexao .aviso-icone,
    .aviso-icone.pulsando {
      animation: none !important;
    }

    .btn-marcar[aria-busy='true'] {
      filter: brightness(1.2);
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
    background: rgba(var(--veu), 0.04);
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
    background: rgba(var(--veu), 0.08);
    color: var(--texto-contraste);
    border-color: rgba(var(--veu), 0.2);
  }

  .btn-desfazer:active:not(:disabled) {
    transform: scale(0.98);
    background: rgba(var(--veu), 0.1);
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
