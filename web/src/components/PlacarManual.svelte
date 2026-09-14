<script>
  import { slide, fade } from 'svelte/transition';
  import CartaoDobravel from './CartaoDobravel.svelte';

  let {
    estadoPartida = null,
    quadra = null,
    prefersReducedMotion = false,
    modoImersivo = true,
    paisagem = false,
    onAbrirLinhaDoTempo = () => {},
  } = $props();

  const pontosA = $derived(estadoPartida?.pontos_a ?? 0);
  const pontosB = $derived(estadoPartida?.pontos_b ?? 0);
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
</script>

<div
  class="placar-manual-container"
  class:modo-imersivo={modoImersivo}
  class:layout-paisagem={paisagem}
  class:layout-retrato={!paisagem}
  class:com-vencedor={encerrada && Boolean(vencedorNome)}
>
  <!-- Placa do Topo: Identificação e Regras -->
  <div class="placa-topo">
    <div class="quadra-badge">
      <span class="icone-arena">🏟️</span>
      <span class="nome-quadra">
        {quadra?.arena_nome ? quadra.arena_nome + ' • ' : ''}{quadra?.nome || 'Quadra'}
      </span>
      {#if quadra?.id}
        <span class="pin-pill">#{quadra.id}</span>
      {/if}
    </div>

    <div class="regras-badge">
      <span class="regra-set">SET ÚNICO</span>
      <span class="regra-alvo">ALVO: {alvo} PTS</span>
      {#if vantagem}<span class="regra-detalhe">VANTAGEM</span>{/if}
      {#if teto}<span class="regra-detalhe">TETO {teto}</span>{/if}
    </div>
  </div>

  <!-- Banner de Vitória quando houver vencedor -->
  {#if encerrada && vencedorNome}
    <div class="banner-vitoria" in:slide={{ duration: prefersReducedMotion ? 0 : 250 }}>
      <span class="trofeu">🏆</span>
      <div class="vitoria-info">
        <span class="vitoria-label">FIM DE JOGO</span>
        <span class="vitoria-time">Vitória da {vencedorNome}!</span>
      </div>
    </div>
  {/if}

  <!-- Palco: absorve a sobra vertical e mantém o cavalete centralizado -->
  <div class="palco">
    <!-- Cavalete / Mesa do Placar Manual -->
    <div class="cavalete-mesa">
      <!-- Barra Superior de Fixação dos Anéis -->
      <div class="barra-suporte-aneis">
        <div class="parafuso parafuso-esq"></div>
        <div class="trilho-metalico"></div>
        <div class="parafuso parafuso-dir"></div>
      </div>

      <!-- Seção dos Cartões e Equipes -->
      <div class="painel-cartoes">
        <!-- Coluna Equipe A -->
        <div class="coluna-equipe {vencedor === 'A' ? 'time-vencedor' : ''}">
          <div class="etiqueta-equipe etiqueta-a">
            <span class="etiqueta-texto">{equipeA}</span>
          </div>

          <CartaoDobravel
            valor={pontosA}
            equipe={equipeA}
            tema="a"
            tamanho="fluido"
            {prefersReducedMotion}
          />
        </div>

        <!-- Divisor Central do Placar ("×" ou divisor da bancada) -->
        <div class="divisor-central">
          <div class="vs-badge">
            <span class="vs-simbolo">×</span>
          </div>
        </div>

        <!-- Coluna Equipe B -->
        <div class="coluna-equipe {vencedor === 'B' ? 'time-vencedor' : ''}">
          <div class="etiqueta-equipe etiqueta-b">
            <span class="etiqueta-texto">{equipeB}</span>
          </div>

          <CartaoDobravel
            valor={pontosB}
            equipe={equipeB}
            tema="b"
            tamanho="fluido"
            {prefersReducedMotion}
          />
        </div>
      </div>

      <!-- Base Dobrável com Efeito de Sombra e Perspectiva -->
      <div class="base-cavalete">
        <div class="base-vinco"></div>
      </div>
    </div>
  </div>

  <!-- Rodapé do modo imersivo: Dica sutil e Linha do Tempo -->
  <div class="rodape-imersivo">
    {#if modoImersivo}
      <div class="dica-toque" in:fade={{ duration: prefersReducedMotion ? 0 : 200 }}>
        <span class="dica-icone">👆</span>
        <span class="dica-texto">Toque na tela para opções</span>
      </div>
    {:else}
      <button
        type="button"
        class="btn-lt-espectador"
        onclick={onAbrirLinhaDoTempo}
        aria-label="Abrir linha do tempo da partida"
      >
        <span class="lt-icon">📜</span>
        <span class="lt-label">Linha do Tempo</span>
      </button>
    {/if}
  </div>
</div>

<style>
  /*
   * --tela-w / --tela-h são herdados do SalaQuadra, que os mede em px e
   * inverte os eixos quando o placar está girado. Os fallbacks abaixo valem
   * apenas se o componente for usado fora dele.
   */
  .placar-manual-container {
    /* Cartão fora do modo imersivo: acompanha a largura, sem exageros. */
    --cartao-w: clamp(118px, calc((var(--tela-w, 100vw) - 104px) / 2), 180px);
    --cartao-h: calc(var(--cartao-w) * 1.22);
    --cartao-num: calc(var(--cartao-w) * 0.78);
    --etiqueta-w: var(--cartao-w);
    --divisor-w: 32px;
    --cavalete-max: 460px;

    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
    padding: 10px 0;
  }

  /*
   * MODO IMERSIVO — o placar ocupa a tela inteira.
   *
   * O tamanho do cartão é o menor entre o que cabe na largura (duas colunas,
   * divisor e molduras) e o que cabe na altura (topo, rodapé e o cavalete).
   * Assim o mesmo cálculo serve para retrato e paisagem, inclusive com a
   * tela girada por software.
   */
  .placar-manual-container.modo-imersivo {
    --cartao-w: clamp(
      92px,
      min(
        calc((var(--tela-w, 100vw) - var(--moldura-w)) / 2),
        calc((var(--tela-h, 100vh) - var(--moldura-h)) / 1.22)
      ),
      var(--cartao-max)
    );
    --cartao-h: min(
      calc(var(--cartao-w) * var(--razao-max)),
      calc(var(--tela-h, 100vh) - var(--moldura-h))
    );
    --cartao-num: min(calc(var(--cartao-w) * 0.65), calc(var(--cartao-h) * 0.62));
    --etiqueta-w: var(--cartao-w);

    height: 100%;
    justify-content: space-between;
    gap: 0;
    padding: 0;
  }

  /*
   * --moldura-w soma tudo que disputa a largura com os dois cartões:
   * padding da sala + padding do cavalete + gaps do grid + divisor central.
   * --moldura-h faz o mesmo na vertical: topo, rodapé, trilho, etiqueta e gaps.
   * Se estes números mentirem, a etiqueta e o cartão saem de esquadro.
   */

  /* Retrato: a largura é o limite. Cartão mais alto para preencher a sobra. */
  .modo-imersivo.layout-retrato {
    --divisor-w: 26px;
    --moldura-w: 74px; /* 12 sala + 16 cavalete + 12 gaps + 34 divisor */
    --moldura-h: 212px; /* 16 sala + 52 topo + 36 rodapé + 104 cavalete + folga */
    --cartao-max: 280px;
    --razao-max: 1.34;
    --cavalete-max: 560px;
  }

  .modo-imersivo.layout-retrato.com-vencedor {
    --moldura-h: 276px; /* 212 + ~64px banner de vitória */
  }

  /* Em pé a largura manda: aperta a moldura para o número crescer */
  .modo-imersivo.layout-retrato .cavalete-mesa {
    padding: 10px 8px 12px 8px;
  }

  .modo-imersivo.layout-retrato .painel-cartoes {
    gap: 6px;
  }

  /* Paisagem: a altura é o limite. Enxuga o topo e o rodapé e alarga o cavalete. */
  .modo-imersivo.layout-paisagem {
    --divisor-w: 54px;
    --moldura-w: 140px; /* 24 sala + 28 cavalete + 24 gaps + 64 divisor */
    --moldura-h: 142px; /* 16 sala + 24 topo + 22 rodapé + 74 cavalete + folga */
    --cartao-max: 400px;
    --razao-max: 1.3;
    --cavalete-max: 920px;
  }

  .modo-imersivo.layout-paisagem.com-vencedor {
    --moldura-h: 198px; /* 142 + ~56px banner de vitória */
  }

  /* Deitado sobra pouca altura: cada pixel de moldura vira número no cartão */
  .modo-imersivo.layout-paisagem .coluna-equipe {
    gap: 5px;
  }

  .modo-imersivo.layout-paisagem .base-cavalete {
    display: none;
  }

  /* Palco central: absorve toda a sobra vertical */
  .palco {
    flex: 1 1 auto;
    min-height: 0;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .placar-manual-container:not(.modo-imersivo) .palco {
    flex: 0 0 auto;
  }

  /* Placa do Topo */
  .placa-topo {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    flex: 0 0 auto;
  }

  .modo-imersivo .placa-topo {
    padding-top: 6px;
  }

  .modo-imersivo.layout-paisagem .placa-topo {
    flex-direction: row;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
    justify-content: center;
    padding-top: 2px;
  }

  .quadra-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 999px;
    padding: 4px 14px;
  }

  .pin-pill {
    background: #0284c7;
    color: #ffffff;
    font-size: 0.75rem;
    font-weight: 800;
    letter-spacing: 0.05em;
    padding: 2px 6px;
    border-radius: 6px;
    margin-left: 2px;
  }

  .modo-imersivo.layout-paisagem .quadra-badge {
    padding: 2px 12px;
  }

  .icone-arena {
    font-size: 0.9rem;
  }

  .nome-quadra {
    font-size: 0.82rem;
    font-weight: 700;
    color: var(--text-primary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .regras-badge {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--text-secondary);
    letter-spacing: 0.06em;
  }

  .modo-imersivo.layout-paisagem .nome-quadra,
  .modo-imersivo.layout-paisagem .regras-badge {
    font-size: 0.7rem;
  }

  .regra-set {
    color: var(--accent-orange);
  }

  .regra-alvo {
    color: #ffffff;
  }

  .regra-detalhe {
    color: var(--text-muted);
  }

  /* Banner de Vitória */
  .banner-vitoria {
    width: 100%;
    max-width: 440px;
    background: linear-gradient(90deg, rgba(245, 158, 11, 0.25) 0%, rgba(234, 88, 12, 0.25) 100%);
    border: 2px solid var(--accent-orange);
    border-radius: var(--radius-md);
    padding: 12px 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 14px;
    box-shadow: 0 4px 20px rgba(249, 115, 22, 0.35);
    flex: 0 0 auto;
  }

  .modo-imersivo.layout-paisagem .banner-vitoria {
    padding: 6px 14px;
    gap: 10px;
  }

  .trofeu {
    font-size: 2.2rem;
  }

  .modo-imersivo.layout-paisagem .trofeu {
    font-size: 1.5rem;
  }

  .vitoria-info {
    display: flex;
    flex-direction: column;
  }

  .vitoria-label {
    font-size: 0.75rem;
    font-weight: 800;
    text-transform: uppercase;
    color: var(--accent-orange);
    letter-spacing: 0.08em;
  }

  .vitoria-time {
    font-size: 1.25rem;
    font-weight: 800;
    color: #ffffff;
  }

  .modo-imersivo.layout-paisagem .vitoria-time {
    font-size: 1rem;
  }

  /* Cavalete / Bancada do Placar */
  .cavalete-mesa {
    width: 100%;
    max-width: var(--cavalete-max, 460px);
    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    border: 2px solid rgba(255, 255, 255, 0.12);
    border-radius: 18px;
    box-shadow:
      0 16px 40px rgba(0, 0, 0, 0.6),
      inset 0 1px 1px rgba(255, 255, 255, 0.15);
    padding: 10px 12px 14px 12px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    position: relative;
  }

  /* Em tela cheia o cavalete abraça os cartões em vez de esticar sozinho */
  .modo-imersivo .cavalete-mesa {
    width: fit-content;
    max-width: min(100%, var(--cavalete-max));
  }

  .modo-imersivo.layout-paisagem .cavalete-mesa {
    padding: 8px 14px 10px 14px;
    gap: 6px;
  }

  /* Barra Metálica Superior */
  .barra-suporte-aneis {
    width: 100%;
    height: 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 10px;
    position: relative;
    flex: 0 0 auto;
  }

  /* Trilho recuado e escuro: é a barra de fixação do cavalete, não um slider */
  .trilho-metalico {
    position: absolute;
    left: 14%;
    right: 14%;
    height: 3px;
    background: linear-gradient(90deg, #1e293b 0%, #64748b 35%, #64748b 65%, #1e293b 100%);
    border-radius: 2px;
    box-shadow: 0 1px 1px rgba(0, 0, 0, 0.7);
    opacity: 0.85;
  }

  .parafuso {
    width: 7px;
    height: 7px;
    border-radius: 2px;
    background: #334155;
    border: 1px solid rgba(148, 163, 184, 0.45);
    box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.7);
    z-index: 2;
  }

  /* Painel dos Cartões */
  .painel-cartoes {
    width: 100%;
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: center;
    justify-items: center;
    gap: 8px;
  }

  .modo-imersivo.layout-paisagem .painel-cartoes {
    gap: 12px;
  }

  .coluna-equipe {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    min-width: 0;
    transition: transform 0.2s ease;
  }

  .time-vencedor {
    transform: scale(1.02);
  }

  /* Etiquetas das Equipes no estilo plaqueta de mesa */
  /* Casa exatamente com a largura do cartão — é o que mantém o esquadro */
  .etiqueta-equipe {
    width: var(--etiqueta-w, 100%);
    max-width: 100%;
    padding: 6px 8px;
    border-radius: 6px;
    text-align: center;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.1);
  }

  .modo-imersivo.layout-paisagem .etiqueta-equipe {
    padding: 4px 8px;
  }

  .etiqueta-a {
    background: linear-gradient(135deg, #0891b2 0%, #0e7490 100%);
    border-color: rgba(6, 182, 212, 0.5);
  }

  .etiqueta-b {
    background: linear-gradient(135deg, #ea580c 0%, #c2410c 100%);
    border-color: rgba(249, 115, 22, 0.5);
  }

  .etiqueta-texto {
    font-size: clamp(0.72rem, calc(var(--cartao-w) * 0.075), 1.25rem);
    font-weight: 800;
    color: #ffffff;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    display: block;
  }

  /* Divisor Central */
  .divisor-central {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 2px;
  }

  .vs-badge {
    width: var(--divisor-w);
    height: var(--divisor-w);
    border-radius: 50%;
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.1);
    display: grid;
    place-items: center;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
  }

  .vs-simbolo {
    font-size: calc(var(--divisor-w) * 0.55);
    font-weight: 700;
    color: var(--text-muted);
    line-height: 1;
  }

  /* Base do Cavalete: sombra de apoio, não uma barra de rolagem */
  .base-cavalete {
    width: 62%;
    height: 6px;
    background: radial-gradient(
      ellipse at center,
      rgba(0, 0, 0, 0.75) 0%,
      rgba(0, 0, 0, 0.35) 55%,
      rgba(0, 0, 0, 0) 100%
    );
    border-radius: 50%;
    margin-top: 2px;
    flex: 0 0 auto;
  }

  /* Rodapé do Modo Imersivo */
  .rodape-imersivo {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 36px;
    flex: 0 0 auto;
  }

  .modo-imersivo.layout-paisagem .rodape-imersivo {
    min-height: 26px;
  }

  .dica-toque {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 500;
    color: var(--text-muted);
    animation: pulsarSuave 2.5s infinite ease-in-out;
  }

  .modo-imersivo.layout-paisagem .dica-toque {
    padding: 3px 12px;
    font-size: 0.7rem;
  }

  @keyframes pulsarSuave {
    0%, 100% {
      opacity: 0.5;
    }
    50% {
      opacity: 0.9;
    }
  }

  .btn-lt-espectador {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.15);
    color: var(--text-secondary);
    border-radius: 999px;
    padding: 6px 16px;
    font-size: 0.85rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    touch-action: manipulation;
    transition: background 0.15s ease, color 0.15s ease;
  }

  .btn-lt-espectador:hover {
    background: rgba(255, 255, 255, 0.12);
    color: #ffffff;
  }

  @media (prefers-reduced-motion: reduce) {
    .dica-toque {
      animation: none;
      opacity: 0.75;
    }
  }
</style>
