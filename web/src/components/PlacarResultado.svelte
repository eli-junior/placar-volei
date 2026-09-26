<script>
  let {
    pontosA = 0,
    pontosB = 0,
    equipeA = 'Equipe A',
    equipeB = 'Equipe B',
    ladosInvertidos = false,
    vencedor = null,
    movimentoReduzido = false,
  } = $props();

  let iniciou = false;
  let anteriorA = 0;
  let anteriorB = 0;
  let destaque = $state(null);
  let anuncio = $state('');
  const tresDigitosA = $derived(String(Math.abs(Number(pontosA) || 0)).length >= 3);
  const tresDigitosB = $derived(String(Math.abs(Number(pontosB) || 0)).length >= 3);

  $effect(() => {
    const atualA = Number(pontosA) || 0;
    const atualB = Number(pontosB) || 0;

    if (!iniciou) {
      iniciou = true;
      anteriorA = atualA;
      anteriorB = atualB;
      return;
    }

    if (atualA === anteriorA && atualB === anteriorB) return;

    const mudouA = atualA !== anteriorA;
    const mudouB = atualB !== anteriorB;
    const desfez = atualA + atualB < anteriorA + anteriorB;
    destaque = mudouA && mudouB ? 'ambos' : mudouA ? 'a' : 'b';
    anuncio = desfez
      ? `Ponto desfeito. ${equipeA} ${atualA}, ${equipeB} ${atualB}.`
      : `Placar atualizado. ${equipeA} ${atualA}, ${equipeB} ${atualB}.`;

    anteriorA = atualA;
    anteriorB = atualB;

    const timer = setTimeout(() => { destaque = null; }, movimentoReduzido ? 0 : 360);
    return () => clearTimeout(timer);
  });
</script>

<div
  class="resultado"
  class:invertido={ladosInvertidos}
  class:movimento-reduzido={movimentoReduzido}
  aria-label="Placar: {equipeA} {pontosA}, {equipeB} {pontosB}"
>
  <section class="time time-a" class:vencedor={vencedor === 'A'}>
    <span class="nome" title={equipeA}>{equipeA}</span>
    <strong class:tres-digitos={tresDigitosA} class:destaque={destaque === 'a' || destaque === 'ambos'}>{pontosA}</strong>
  </section>

  <div class="divisor" aria-hidden="true">
    <span>×</span>
  </div>

  <section class="time time-b" class:vencedor={vencedor === 'B'}>
    <span class="nome" title={equipeB}>{equipeB}</span>
    <strong class:tres-digitos={tresDigitosB} class:destaque={destaque === 'b' || destaque === 'ambos'}>{pontosB}</strong>
  </section>
</div>

<p class="somente-leitor" role="status" aria-live="polite" aria-atomic="true">{anuncio}</p>

<style>
  .resultado {
    container-type: size;
    display: grid;
    grid-template-columns: minmax(0, 1fr) clamp(32px, 6cqw, 72px) minmax(0, 1fr);
    grid-template-areas: 'a divisor b';
    width: 100%;
    height: 100%;
    min-height: 250px;
    overflow: hidden;
    border: 1px solid var(--acao-secundaria);
    border-radius: clamp(16px, 2.5cqw, 28px);
    background: var(--fundo-superficie);
    box-shadow: var(--sombra-elevada);
  }

  .resultado.invertido { grid-template-areas: 'b divisor a'; }
  .time-a { grid-area: a; --cor-time: var(--time-a); --cor-tenue: var(--time-a-tenue); }
  .time-b { grid-area: b; --cor-time: var(--time-b); --cor-tenue: var(--time-b-tenue); }

  .time {
    position: relative;
    display: grid;
    grid-template-rows: auto minmax(0, 1fr);
    align-items: center;
    justify-items: center;
    min-width: 0;
    padding: clamp(.75rem, 2.3cqw, 1.75rem);
    background: linear-gradient(180deg, var(--cor-tenue), transparent 68%);
  }

  .time::before {
    content: '';
    position: absolute;
    inset: 0 0 auto;
    height: clamp(5px, .7cqw, 10px);
    background: var(--cor-time);
  }

  .nome {
    box-sizing: border-box;
    max-width: 100%;
    min-height: 2.1em;
    padding-top: clamp(.25rem, 1cqh, .75rem);
    overflow: hidden;
    color: var(--texto-medio);
    font-size: clamp(.72rem, min(3cqw, 3cqh), 1.45rem);
    font-weight: 800;
    letter-spacing: .09em;
    line-height: 1.05;
    text-align: center;
    text-overflow: ellipsis;
    text-transform: uppercase;
    white-space: nowrap;
  }

  strong {
    display: grid;
    place-items: center;
    max-width: 100%;
    color: var(--cor-time);
    font-family: var(--fonte-numeros);
    font-size: clamp(7rem, min(50cqw, 74cqh), 32rem);
    font-weight: 600;
    font-variant-numeric: tabular-nums;
    letter-spacing: -.045em;
    line-height: .72;
    text-shadow: 0 0 clamp(12px, 3cqw, 36px) color-mix(in srgb, var(--cor-time) 24%, transparent);
    transform: scale(1);
  }

  strong.destaque { animation: ponto .36s ease-out; }
  strong.tres-digitos { font-size: clamp(5rem, min(27cqw, 54cqh), 18rem); }

  .time.vencedor {
    background: linear-gradient(180deg, color-mix(in srgb, var(--cor-time) 24%, transparent), transparent 72%);
  }

  .divisor {
    grid-area: divisor;
    display: grid;
    place-items: center;
    color: var(--texto-apagado);
  }

  .divisor span {
    display: grid;
    place-items: center;
    width: clamp(30px, 5cqw, 58px);
    aspect-ratio: 1;
    border: 1px solid var(--acao-secundaria);
    border-radius: 50%;
    background: var(--fundo-base);
    font-size: clamp(1.15rem, 3cqw, 2rem);
    font-weight: 800;
  }

  .somente-leitor {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
  }

  @keyframes ponto {
    0% { transform: scale(1); filter: brightness(1); }
    45% { transform: scale(1.08); filter: brightness(1.35); }
    100% { transform: scale(1); filter: brightness(1); }
  }

  .movimento-reduzido strong.destaque { animation: none; }

  @media (max-aspect-ratio: 3 / 4) {
    .resultado { grid-template-columns: minmax(0, 1fr) 30px minmax(0, 1fr); }
    .time { padding-inline: clamp(.35rem, 1.5cqw, .8rem); }
    strong { font-size: clamp(7rem, min(50cqw, 66cqh), 28rem); }
    strong.tres-digitos { font-size: clamp(5rem, min(27cqw, 48cqh), 17rem); }
  }

  @media (prefers-reduced-motion: reduce) {
    strong.destaque { animation: none; }
  }
</style>
