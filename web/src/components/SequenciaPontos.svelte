<script>
  // Faixa de sequência de pontos sob o placar: uma bolinha por ponto ativo,
  // na cor da equipe, a mais recente à direita.
  let {
    pontos = [],
    equipeA = 'Equipe A',
    equipeB = 'Equipe B',
    movimentoReduzido = false,
  } = $props();

  let faixaEl = $state(null);

  const resumo = $derived(
    pontos.length
      ? `Sequência de pontos: ${pontos.map((p) => (p.equipe === 'A' ? equipeA : equipeB)).join(', ')}`
      : 'Sequência de pontos: nenhum ponto ainda'
  );

  $effect(() => {
    pontos.length;
    if (faixaEl) faixaEl.scrollTo({ left: faixaEl.scrollWidth, behavior: movimentoReduzido ? 'instant' : 'smooth' });
  });
</script>

<div class="sequencia" class:vazia={!pontos.length} bind:this={faixaEl} role="img" aria-label={resumo}>
  {#each pontos as ponto, i (ponto.id)}
    <span
      class="bolinha"
      class:time-a={ponto.equipe === 'A'}
      class:time-b={ponto.equipe === 'B'}
      class:recente={i === pontos.length - 1}
      class:movimento-reduzido={movimentoReduzido}
      aria-hidden="true"
    ></span>
  {/each}
</div>

<style>
  .sequencia {
    display: flex;
    align-items: center;
    gap: 7px;
    box-sizing: border-box;
    width: fit-content;
    max-width: 100%;
    margin-inline: auto;
    min-height: 30px;
    padding: 4px 10px;
    border-radius: 999px;
    background: color-mix(in srgb, var(--fundo-superficie) 80%, transparent);
    overflow-x: auto;
    scrollbar-width: none;
  }
  .sequencia::-webkit-scrollbar { display: none; }
  /* Sem pontos não há o que mostrar: a altura fica (o placar não pula), a pílula some. */
  .sequencia.vazia { background: transparent; }

  .bolinha {
    flex: 0 0 auto;
    width: 18px;
    height: 18px;
    border-radius: 50%;
  }
  .time-a { background: var(--time-a); }
  .time-b { background: var(--time-b); }

  .recente {
    box-shadow: 0 0 0 2px var(--fundo-superficie), 0 0 0 3.5px currentColor;
    color: var(--texto-medio);
    animation: entrar .3s ease-out;
  }
  .recente.movimento-reduzido { animation: none; }

  @keyframes entrar {
    from { transform: scale(0); }
    to { transform: scale(1); }
  }
</style>
