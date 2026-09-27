<script>
  import { fly, fade, slide } from 'svelte/transition';
  import PlacarClassico from './PlacarClassico.svelte';
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
    onAbrirCompartilhar = () => {},
    // Ações secundárias ficam num único menu (CV4.DS3.US1).
    // Equipe do ponto que o Desfazer vai anular, quando conhecida.
    ultimoPonto = null,
    ladosInvertidos = false,
  } = $props();

  let feedbackEquipe = $state(null);
  // Botão que originou o último envio (CV5.DS4.US2): só ele fica `aria-busy`,
  // para o leitor de tela não anunciar "ocupado" em todos os botões.
  let origemEnvio = $state(null);
  let feedbackTimer = null;
  let prefersReducedMotion = $state(false);

  function handleIniciarNovaPartida() {
    if (enviando || desabilitado) return;
    origemEnvio = 'nova';
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
  const podeMarcar = $derived(podeControlar && !desabilitado && !encerrada);

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
  const ultimoNome = $derived(ultimoPonto === 'A' ? equipeA : ultimoPonto === 'B' ? equipeB : null);

  function handleToqueDesfazer() {
    if (!podeDesfazer) return;
    vibrar(30);
    origemEnvio = 'desfazer';
    onDesfazerPonto();
  }

  /*
   * Um toque nunca é engolido por já haver outro em voo: o comando é entregue
   * ao pai, que serializa a fila. Aqui só cuidamos do retorno imediato — vibração,
   * clarão no botão da equipe e `aria-busy` no botão enquanto o envio acontece.
   */
  function handleToquePonto(equipe) {
    if (!podeMarcar) return;

    vibrar(35);

    feedbackEquipe = equipe;
    if (feedbackTimer) clearTimeout(feedbackTimer);
    feedbackTimer = setTimeout(() => {
      feedbackEquipe = null;
    }, 300);

    origemEnvio = equipe;
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
      anuncioAcessivel = `Fim de jogo! ${venc} venceu. Placar final: ${equipeA} ${pA}, ${equipeB} ${pB}.`;
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

<!--
  Operação (CV4.DS3.US1): tudo que marca o placar cabe numa tela, sem rolar.
  +1 fica sob cada equipe (nas laterais em paisagem) e segue a inversão de
  lados; Desfazer está sempre a um toque. Ações secundárias vão para o menu ⋯.
-->
<section
  class="placar-card"
  class:lados-invertidos={ladosInvertidos}
  in:slide={{ duration: prefersReducedMotion ? 0 : 250 }}
>
  <!-- Anunciador dinâmico de acessibilidade WCAG (leitores de tela) -->
  <div class="sr-only" role="status" aria-live="polite" aria-atomic="true">
    {anuncioAcessivel}
  </div>

  {#if encerrada && vencedorNome}
    <div class="banner-vitoria" in:slide={{ duration: prefersReducedMotion ? 0 : 250 }}>
      <div class="vitoria-cabecalho">
        <span class="trofeu">🏆</span>
        <div class="vitoria-texto">
          <span class="vitoria-titulo">Fim de Jogo!</span>
          <span class="vitoria-vencedor">{vencedorNome} venceu!</span>
        </div>
      </div>

      {#if podeControlar}
        <div class="vitoria-botoes">
          <button
            type="button"
            class="btn-nova-partida"
            disabled={desabilitado || enviando}
            aria-busy={enviando && origemEnvio === 'nova'}
            onclick={handleIniciarNovaPartida}
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
        </div>
      {/if}
    </div>
  {/if}

  {#if podeControlar && enviando && !desabilitado}
    <div class="aviso-envio" role="status">
      <span class="aviso-icone pulsando" aria-hidden="true">●</span>
      <span>{pendentes > 1 ? `Enviando ${pendentes} toques na fila…` : 'Enviando o toque…'}</span>
    </div>
  {/if}

  <div class="palco">
    <div class="resultado">
      {#if temaPlacar === 'esportivo'}
        <PlacarResultado
          {pontosA}
          {pontosB}
          {equipeA}
          {equipeB}
          {ladosInvertidos}
          {vencedor}
          movimentoReduzido={prefersReducedMotion}
        />
      {:else}
        <PlacarClassico
          {pontosA}
          {pontosB}
          {equipeA}
          {equipeB}
          {ladosInvertidos}
          movimentoReduzido={prefersReducedMotion}
        />
      {/if}
    </div>

    <button
      type="button"
      class="btn-marcar btn-marcar-a"
      class:flash={feedbackEquipe === 'A'}
      disabled={!podeMarcar}
      aria-busy={enviando && origemEnvio === 'A'}
      onclick={() => handleToquePonto('A')}
      aria-label="Marcar ponto para {equipeA}"
    ><span class="btn-plus">+1</span><span class="btn-sub">{equipeA}</span></button>
    <button
      type="button"
      class="btn-marcar btn-marcar-b"
      class:flash={feedbackEquipe === 'B'}
      disabled={!podeMarcar}
      aria-busy={enviando && origemEnvio === 'B'}
      onclick={() => handleToquePonto('B')}
      aria-label="Marcar ponto para {equipeB}"
    ><span class="btn-plus">+1</span><span class="btn-sub">{equipeB}</span></button>
  </div>

  <div class="base">
    <button
      type="button"
      class="btn-desfazer"
      disabled={!podeDesfazer}
      aria-busy={enviando && origemEnvio === 'desfazer'}
      onclick={handleToqueDesfazer}
      aria-label={ultimoNome ? `Desfazer último ponto, de ${ultimoNome}` : 'Desfazer último ponto marcado'}
    >
      <span class="desfazer-texto"><span aria-hidden="true">↺</span> Desfazer</span>
      {#if ultimoNome && podeDesfazer}<small>último: +1 {ultimoNome}</small>{/if}
    </button>
  </div>
</section>

<style>
  /*
   * Operação sem rolagem: a carta ocupa o que sobra da tela e o palco cresce.
   * Em paisagem os +1 vão para as laterais, perto dos polegares.
   */
  .placar-card {
    container-type: inline-size;
    display: flex;
    flex-direction: column;
    gap: 10px;
    flex: 1 1 auto;
    min-height: 0;
  }

  .palco {
    flex: 1 1 auto;
    min-height: 0;
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: minmax(0, 1fr) auto;
    grid-template-areas:
      'resultado resultado'
      'a b';
    gap: 10px;
  }

  .lados-invertidos .palco { grid-template-areas: 'resultado resultado' 'b a'; }
  .palco .resultado { grid-area: resultado; min-height: 0; display: flex; }
  .palco .resultado > :global(*) { flex: 1 1 auto; min-width: 0; }
  .palco .btn-marcar-a { grid-area: a; }
  .palco .btn-marcar-b { grid-area: b; }

  @container (min-width: 720px) {
    .palco {
      grid-template-columns: minmax(120px, 17%) minmax(0, 1fr) minmax(120px, 17%);
      grid-template-rows: minmax(0, 1fr);
      grid-template-areas: 'a resultado b';
    }
    .lados-invertidos .palco { grid-template-areas: 'b resultado a'; }
    .palco .btn-marcar { height: auto; min-height: 120px; }
  }

  .base {
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    gap: 8px;
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

  /* Avisos de transporte: conexão caída e envio em andamento */
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

  .aviso-envio {
    /* Token do tema: no Modo Sol o cartão é branco e o ciano claro sumia. */
    color: var(--acento-info);
    background: rgba(6, 182, 212, 0.12);
    border: 1px solid rgba(6, 182, 212, 0.35);
  }

  .aviso-icone {
    font-size: 1rem;
    line-height: 1;
    flex: 0 0 auto;
  }

  .aviso-icone.pulsando {
    animation: pulsar-aviso 0.9s ease-in-out infinite;
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
    .aviso-icone.pulsando {
      animation: none !important;
    }

    .btn-marcar[aria-busy='true'] {
      filter: brightness(1.2);
    }
  }

  /* Estilos do Botão Desfazer (US3) */

  .btn-desfazer {
    width: 100%;
    min-height: 56px;
    flex-direction: column;
    gap: 0;
    line-height: 1.2;
    background: var(--bg-surface);
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

  .desfazer-texto {
    color: var(--text-primary);
    font-weight: 800;
    letter-spacing: 0.02em;
  }

  .btn-desfazer small {
    max-width: 100%;
    overflow: hidden;
    color: var(--text-secondary);
    font-size: 0.75rem;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .btn-marcar.flash { filter: brightness(1.2); }
  .btn-sub { max-width: 100%; overflow: hidden; padding: 0 8px; text-overflow: ellipsis; white-space: nowrap; }

  /*
   * Celular deitado: a altura é o recurso escasso. Compacta a moldura e os
   * botões para que placar, +1 e desfazer caibam sem rolagem.
   */
  @media (orientation: landscape) and (max-height: 500px) {
    .placar-card {
      padding: 12px 14px 14px 14px;
      gap: 10px;
    }

    .btn-marcar {
      height: 60px;
    }

    .btn-plus {
      font-size: 1.7rem;
    }

    .btn-desfazer {
      /* 48px: é a correção mais usada, não pode encolher abaixo do alvo mínimo. */
      height: 48px;
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
