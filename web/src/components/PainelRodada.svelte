<script>
  import { descreverTime, posicaoDaCombinacao, primeiraPartida } from '../lib/jogadores.js';

  // Apresentação da proposta ou da rodada em andamento (CV8.DS2.US3).
  // As ações vêm de fora; este componente só mostra e dispara.
  let { rodada, ocupado = false, onResortear = () => {}, onDescartar = () => {}, onConfirmar = () => {} } = $props();

  const proposta = $derived(rodada.estado === 'proposta');
  const primeira = $derived(primeiraPartida(rodada.times));
  const posicao = $derived(posicaoDaCombinacao(rodada));
</script>

<section class="rodada" aria-labelledby="titulo-rodada">
  <h2 id="titulo-rodada">
    {proposta ? 'Proposta' : 'Rodada'} {rodada.numero} <span class="alvo">· {rodada.formato === 'trio' ? 'trios' : 'duplas'} · alvo {rodada.alvo}</span>
  </h2>
  {#if proposta}
    <p class="ajuda">
      {#if rodada.numero > 1}Reequilibrada pelo saldo da sessão (nota ajustada entre parênteses). {/if}Confira {rodada.formato === 'trio' ? 'os trios' : 'as duplas'} e a fila. Combinação {posicao.atual} de {posicao.total} igualmente equilibradas{#if posicao.total === 1}; não há outra para trocar{/if}.
    </p>
  {/if}

  {#if primeira}
    <p class="primeira" role="status">
      <strong>Primeira partida:</strong> Time {primeira[0].fila} × Time {primeira[1].fila}
    </p>
  {/if}

  <ol class="fila">
    {#each rodada.times as time (time.fila)}
      <li class:incompleto={time.incompleto} class:em-quadra={time.fila <= 2}>
        <span class="posicao">Time {time.fila}{#if time.fila <= 2} <span class="selo">em quadra</span>{/if}</span>
        <span class="jogadores">{descreverTime(time)}</span>
        <span class="soma">soma {time.soma}</span>
        {#if time.incompleto}<span class="aviso">Incompleto: escolhe {rodada.tamanho - time.jogadores.length === 1 ? 'o parceiro' : 'os parceiros'} na sua vez.</span>{/if}
      </li>
    {/each}
  </ol>

  <div class="botoes">
    {#if proposta}
      <button class="acao-principal" type="button" onclick={onConfirmar} disabled={ocupado}>Confirmar e iniciar</button>
      <button class="secundario" type="button" onclick={onResortear} disabled={ocupado || posicao.total === 1}>Resortear</button>
      <button class="secundario" type="button" onclick={onDescartar} disabled={ocupado}>Descartar</button>
    {/if}
  </div>
</section>

<style>
  .rodada { display: flex; flex-direction: column; gap: .6rem; padding: 1rem; border: 1px solid var(--borda-ativa); border-radius: var(--raio-padrao); background: var(--fundo-superficie); color: var(--texto-forte); }
  h2 { margin: 0; font-size: var(--texto-destaque); }
  .alvo { color: var(--texto-suave); font-weight: 600; }
  .ajuda { margin: 0; color: var(--texto-suave); font-size: var(--texto-apoio); }
  .primeira { margin: 0; padding: .6rem .75rem; border-radius: var(--raio-justo); background: var(--fundo-cartao-ativo); }
  .fila { display: flex; flex-direction: column; gap: .5rem; margin: 0; padding: 0; list-style: none; }
  li { display: flex; flex-wrap: wrap; align-items: baseline; gap: .25rem .75rem; padding: .6rem .75rem; border: 1px solid var(--borda-sutil); border-radius: var(--raio-padrao); background: var(--fundo-cartao); }
  li.em-quadra { border-color: var(--borda-ativa); }
  .posicao { font-weight: 800; }
  .selo { margin-left: .35rem; padding: .05rem .45rem; border-radius: var(--raio-circular); background: var(--fundo-cartao-ativo); color: var(--texto-medio); font-size: var(--texto-micro); font-weight: 700; }
  .jogadores { flex: 1 1 12rem; }
  .soma { color: var(--texto-suave); font-size: var(--texto-legenda); }
  .aviso { flex-basis: 100%; color: var(--texto-medio); font-size: var(--texto-legenda); }
  .botoes { display: flex; flex-wrap: wrap; gap: .5rem; align-items: center; }
  .acao-principal { display: inline-flex; align-items: center; justify-content: center; min-height: 48px; padding: 0 1.1rem; border: 0; border-radius: 10px; background: var(--acao-primaria); color: var(--acao-primaria-texto); font: inherit; font-weight: 800; cursor: pointer; }
  .secundario { display: inline-flex; align-items: center; min-height: 44px; padding: 0 .85rem; border: 1px solid var(--acao-secundaria); border-radius: 12px; background: var(--fundo-superficie); color: var(--texto-medio); font: inherit; font-size: var(--texto-apoio); font-weight: 700; cursor: pointer; }
  button:disabled { opacity: .45; cursor: not-allowed; }
</style>
