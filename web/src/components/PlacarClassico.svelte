<script>
  import CartaoDobravel from './CartaoDobravel.svelte';

  let {
    pontosA = 0,
    pontosB = 0,
    equipeA = 'Equipe A',
    equipeB = 'Equipe B',
    ladosInvertidos = false,
    movimentoReduzido = false,
  } = $props();
</script>

<div
  class="classico"
  class:invertido={ladosInvertidos}
  aria-label="Placar clássico: {equipeA} {pontosA}, {equipeB} {pontosB}"
>
  <section class="time time-a">
    <span class="nome" title={equipeA}>{equipeA}</span>
    <CartaoDobravel valor={pontosA} equipe={equipeA} tema="a" tamanho="fluido" prefersReducedMotion={movimentoReduzido} />
  </section>
  <span class="divisor" aria-hidden="true">×</span>
  <section class="time time-b">
    <span class="nome" title={equipeB}>{equipeB}</span>
    <CartaoDobravel valor={pontosB} equipe={equipeB} tema="b" tamanho="fluido" prefersReducedMotion={movimentoReduzido} />
  </section>
</div>

<style>
  .classico {
    container-type: size;
    display: grid;
    grid-template-columns: minmax(0, 1fr) clamp(28px, 5cqw, 64px) minmax(0, 1fr);
    grid-template-areas: 'a divisor b';
    align-items: center;
    width: 100%;
    height: 100%;
    min-height: 250px;
    padding: clamp(.65rem, 2cqw, 1.5rem);
    box-sizing: border-box;
    overflow: hidden;
    border: 1px solid var(--acao-secundaria);
    border-radius: clamp(16px, 2.5cqw, 28px);
    background: linear-gradient(180deg, var(--fundo-superficie), var(--fundo-elevado));
    box-shadow: var(--sombra-elevada);
  }

  .classico.invertido { grid-template-areas: 'b divisor a'; }
  .time-a { grid-area: a; }
  .time-b { grid-area: b; }

  .time {
    display: grid;
    grid-template-rows: auto minmax(0, 1fr);
    gap: clamp(.55rem, 1.5cqh, 1rem);
    width: 100%;
    height: 100%;
    min-width: 0;
    min-height: 0;
    place-items: stretch center;
  }

  .nome {
    width: 100%;
    overflow: hidden;
    padding: .55rem .35rem;
    box-sizing: border-box;
    border-radius: 8px;
    background: var(--cor-time);
    color: #fff;
    font-size: clamp(.7rem, min(2.7cqw, 2.7cqh), 1.35rem);
    font-weight: 850;
    letter-spacing: .08em;
    text-align: center;
    text-overflow: ellipsis;
    text-transform: uppercase;
    white-space: nowrap;
  }

  .time-a { --cor-time: var(--time-a); }
  .time-b { --cor-time: var(--time-b); }

  .time :global(.cartao-wrapper) {
    --cartao-w: 100%;
    --cartao-h: 100%;
    min-height: 0;
  }

  .divisor {
    grid-area: divisor;
    display: grid;
    place-items: center;
    color: var(--texto-apagado);
    font-size: clamp(1.15rem, 3cqw, 2rem);
    font-weight: 850;
  }

  @media (max-aspect-ratio: 3 / 4) {
    .classico { padding-inline: .35rem; }
  }
</style>
