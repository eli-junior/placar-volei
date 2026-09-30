<script>
  import CartaoDobravel from './CartaoDobravel.svelte';

  let {
    pontosA = 0,
    pontosB = 0,
    equipeA = 'Equipe A',
    equipeB = 'Equipe B',
    ladosInvertidos = false,
    ultimoPonto = null,
    movimentoReduzido = false,
    onEditarEquipe = null,
  } = $props();

  // Um pulso por ponto: só quando o total sobe, nunca no desfazer.
  let pulso = $state(null);
  let totalAnterior = null;
  $effect(() => {
    const total = (Number(pontosA) || 0) + (Number(pontosB) || 0);
    const equipe = ultimoPonto;
    const subiu = totalAnterior !== null && total > totalAnterior;
    totalAnterior = total;
    if (!subiu || !equipe || movimentoReduzido) return;
    pulso = equipe;
    const timer = setTimeout(() => { pulso = null; }, 600);
    return () => clearTimeout(timer);
  });
</script>

<div
  class="classico"
  class:invertido={ladosInvertidos}
  aria-label="Placar clássico: {equipeA} {pontosA}, {equipeB} {pontosB}"
>
  <section class="time time-a" class:tres-digitos={String(pontosA).length > 2} class:ultimo={ultimoPonto === 'A'} class:apagado={ultimoPonto === 'B'} class:pulso={pulso === 'A'}>
    {#if onEditarEquipe}<button type="button" class="nome editavel" title="Editar jogadores" aria-label="Editar jogadores da {equipeA}" onclick={() => onEditarEquipe('A')}>{equipeA}</button>{:else}<span class="nome" title={equipeA}>{equipeA}</span>{/if}
    <CartaoDobravel valor={pontosA} equipe={equipeA} tema="a" tamanho="fluido" prefersReducedMotion={movimentoReduzido} />
  </section>
  <div class="divisor" aria-hidden="true">
    <svg viewBox="0 0 100 100"><path d="M8 8L92 92M92 8L8 92" /></svg>
  </div>
  <section class="time time-b" class:tres-digitos={String(pontosB).length > 2} class:ultimo={ultimoPonto === 'B'} class:apagado={ultimoPonto === 'A'} class:pulso={pulso === 'B'}>
    {#if onEditarEquipe}<button type="button" class="nome editavel" title="Editar jogadores" aria-label="Editar jogadores da {equipeB}" onclick={() => onEditarEquipe('B')}>{equipeB}</button>{:else}<span class="nome" title={equipeB}>{equipeB}</span>{/if}
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

  /* Nome como botão para quem controla (CV6.DS1.US6). */
  button.nome.editavel { display: block; width: 100%; border: 0; font-family: inherit; cursor: pointer; text-decoration: underline dotted color-mix(in srgb, currentColor 45%, transparent); text-underline-offset: 4px; }
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

  /* Último ponto: cartão de quem pontuou cresce e acende; o outro recua. */
  .time :global(.cartao-wrapper) { transition: transform .25s ease, opacity .25s ease, filter .25s ease; }
  .time.ultimo :global(.cartao-wrapper) {
    transform: scale(1.06);
    filter: drop-shadow(0 0 14px color-mix(in srgb, var(--cor-time) 55%, transparent));
  }
  .time.apagado :global(.cartao-wrapper) { opacity: .62; }
  .time.pulso :global(.cartao-wrapper) { animation: pulso-classico .6s ease-out; }
  @keyframes pulso-classico {
    0% { transform: scale(1); filter: brightness(1); }
    40% { transform: scale(1.14); filter: brightness(1.5) drop-shadow(0 0 22px var(--cor-time)); }
    100% { transform: scale(1.06); }
  }

  .time :global(.cartao-wrapper) {
    --cartao-w: 100%;
    --cartao-h: 100%;
    min-height: 0;
  }

  /* Escala P/M/G (CV6.DS1.US3) também no clássico: tamanho automático pelo
     contêiner, multiplicado pela escala e limitado ao que cabe no cartão. */
  .time { --cartao-num: clamp(3.5rem, min(calc(min(22cqw, 48cqh) * var(--escala-numeros, 1)), 34cqw, 62cqh), 40rem); }
  .time.tres-digitos { --cartao-num: clamp(3rem, min(calc(min(15cqw, 40cqh) * var(--escala-numeros, 1)), 23cqw, 62cqh), 28rem); }

  /* Mesmo divisor do esportivo: linha e × cheios no centro, sumindo nas pontas. */
  .divisor {
    grid-area: divisor;
    position: relative;
    align-self: stretch;
    display: grid;
    place-items: center;
    color: var(--texto-medio);
  }

  .divisor::before {
    content: '';
    position: absolute;
    inset: 0 auto;
    left: 50%;
    width: 2px;
    transform: translateX(-50%);
    background: linear-gradient(180deg, transparent, currentColor 50%, transparent);
  }

  .divisor svg {
    position: relative;
    width: clamp(30px, 5cqw, 64px);
    aspect-ratio: 1;
    padding: 4px;
    background: var(--fundo-elevado);
    fill: none;
    stroke: currentColor;
    stroke-width: 18;
    stroke-linecap: round;
    mask-image: radial-gradient(circle, #000 20%, transparent 72%);
  }

  /* Tela em pé: uma equipe sobre a outra (CV6.DS1.US3). */
  @media (max-aspect-ratio: 3 / 4) {
    .classico {
      padding-inline: .35rem;
      grid-template-columns: minmax(0, 1fr);
      grid-template-rows: minmax(0, 1fr) auto minmax(0, 1fr);
      grid-template-areas: 'a' 'divisor' 'b';
    }
    .classico.invertido { grid-template-areas: 'b' 'divisor' 'a'; }
    /* Em pé a linha vira horizontal. */
    .divisor { align-self: center; justify-self: stretch; }
    .divisor::before { inset: auto 0; top: 50%; left: 0; width: auto; height: 2px; transform: translateY(-50%); background: linear-gradient(90deg, transparent, currentColor 50%, transparent); }
    .time { --cartao-num: clamp(3.5rem, min(calc(min(42cqw, 22cqh) * var(--escala-numeros, 1)), 70cqw, 30cqh), 40rem); }
    .time.tres-digitos { --cartao-num: clamp(3rem, min(calc(min(30cqw, 20cqh) * var(--escala-numeros, 1)), 48cqw, 30cqh), 28rem); }
  }
</style>
