<script>
  import { fade, slide } from 'svelte/transition';
  import Icone from './Icone.svelte';
  import PlacarResultado from './PlacarResultado.svelte';

  let {
    estadoPartida = null,
    quadra = null,
    prefersReducedMotion = false,
    modoImersivo = true,
    paisagem = false,
    ladosInvertidos = false,
    onAlternarLados = () => {},
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
  const vencedorNome = $derived(vencedor === 'A' ? equipeA : vencedor === 'B' ? equipeB : null);
</script>

<section
  class="placar-esportivo"
  class:modo-imersivo={modoImersivo}
  class:paisagem
  class:retrato={!paisagem}
  aria-label="Acompanhamento da partida"
>
  <header class="contexto">
    <div class="identidade">
      <Icone nome="bola" tamanho="1em" />
      <span class="nome-quadra" title={quadra?.nome || 'Quadra'}>{quadra?.nome || 'Quadra'}</span>
      {#if quadra?.id}<span class="codigo">#{quadra.id}</span>{/if}
    </div>
    <div class="regras" aria-label="Regras da partida">
      <span>SET ÚNICO</span>
      <strong>ALVO {alvo}</strong>
      {#if vantagem}<span>VANTAGEM</span>{/if}
      {#if teto}<span>TETO {teto}</span>{/if}
    </div>
  </header>

  {#if encerrada && vencedorNome}
    <div class="vitoria" in:slide={{ duration: prefersReducedMotion ? 0 : 220 }}>
      <Icone nome="trofeu" tamanho="1.35em" />
      <span><small>FIM DE JOGO</small> Vitória de <strong>{vencedorNome}</strong></span>
    </div>
  {/if}

  <div class="area-resultado">
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

  <footer class="rodape">
    {#if modoImersivo}
      <p class="dica" in:fade={{ duration: prefersReducedMotion ? 0 : 160 }}>Toque na tela para ver opções</p>
    {:else}
      <div class="acoes" in:fade={{ duration: prefersReducedMotion ? 0 : 160 }}>
        <button type="button" class:ativo={ladosInvertidos} onclick={onAlternarLados} aria-pressed={ladosInvertidos}>
          <span aria-hidden="true">⇄</span>
          <span>{ladosInvertidos ? 'Lados invertidos' : 'Inverter lados'}</span>
        </button>
        <button type="button" onclick={onAbrirLinhaDoTempo}>
          <Icone nome="linhaDoTempo" tamanho="1.05em" />
          <span>Linha do tempo</span>
        </button>
      </div>
    {/if}
  </footer>
</section>

<style>
  .placar-esportivo {
    box-sizing: border-box;
    display: grid;
    grid-template-rows: auto auto minmax(280px, 1fr) auto;
    grid-template-areas:
      'contexto'
      'vitoria'
      'resultado'
      'rodape';
    gap: clamp(.5rem, 1.6vmin, 1rem);
    width: 100%;
    min-height: min(760px, calc(var(--tela-h, 100vh) - 24px));
    padding: clamp(.4rem, 1.4vmin, .9rem);
    color: var(--texto-forte);
  }

  .placar-esportivo.modo-imersivo {
    height: 100%;
    min-height: 0;
    grid-template-rows: auto auto minmax(0, 1fr) auto;
    padding: 0;
  }

  .contexto {
    grid-area: contexto;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: clamp(.7rem, 2.5vw, 1.5rem);
    min-width: 0;
    color: var(--texto-suave);
    font-size: clamp(.66rem, 1.8vmin, .82rem);
    font-weight: 750;
    letter-spacing: .07em;
    text-transform: uppercase;
  }

  .identidade, .regras {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: .45rem;
    min-width: 0;
  }

  .identidade {
    padding: .35rem .65rem;
    border: 1px solid var(--acao-secundaria);
    border-radius: 999px;
    background: var(--fundo-superficie);
  }

  .nome-quadra {
    max-width: min(28vw, 260px);
    overflow: hidden;
    color: var(--texto-medio);
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .codigo {
    padding: .15rem .38rem;
    border-radius: 5px;
    background: var(--acento-info-forte);
    color: #fff;
    font-family: var(--fonte-numeros);
    font-size: 1.05em;
  }

  .regras strong { color: var(--texto-forte); }
  .regras span:first-child { color: var(--time-b); }

  .vitoria {
    grid-area: vitoria;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: .65rem;
    padding: .5rem .9rem;
    border: 1px solid color-mix(in srgb, var(--marca) 60%, transparent);
    border-radius: 10px;
    background: color-mix(in srgb, var(--marca) 14%, var(--fundo-superficie));
    color: var(--marca);
    font-size: clamp(.85rem, 2vmin, 1.1rem);
  }

  .vitoria small { margin-right: .45rem; font-size: .7em; letter-spacing: .09em; }
  .area-resultado { grid-area: resultado; min-height: 0; }

  .rodape {
    grid-area: rodape;
    display: grid;
    place-items: center;
    min-height: 42px;
  }

  .dica {
    margin: 0;
    padding: .38rem .8rem;
    border: 1px solid var(--acao-secundaria);
    border-radius: 999px;
    color: var(--texto-apagado);
    font-size: clamp(.68rem, 1.8vmin, .82rem);
  }

  .acoes {
    display: flex;
    justify-content: center;
    gap: .65rem;
    width: 100%;
  }

  .acoes button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: .45rem;
    min-height: 46px;
    padding: 0 1rem;
    border: 1px solid var(--acao-secundaria);
    border-radius: 999px;
    background: var(--fundo-superficie);
    color: var(--texto-medio);
    font: inherit;
    font-size: .82rem;
    font-weight: 750;
  }

  .acoes button.ativo {
    border-color: var(--marca);
    color: var(--marca);
  }

  @media (max-width: 560px) {
    .placar-esportivo { gap: .45rem; padding-inline: .15rem; }
    .contexto { flex-direction: column; gap: .35rem; }
    .nome-quadra { max-width: 52vw; }
    .regras { gap: .35rem; font-size: .68rem; }
    .acoes { gap: .4rem; }
    .acoes button { flex: 1; padding-inline: .55rem; }
  }

  @media (max-height: 540px) {
    .placar-esportivo { grid-template-rows: auto auto minmax(0, 1fr) auto; gap: .3rem; }
    .contexto { flex-direction: row; }
    .rodape { min-height: 34px; }
    .dica { padding-block: .2rem; }
    .acoes button { min-height: 40px; }
  }
</style>
