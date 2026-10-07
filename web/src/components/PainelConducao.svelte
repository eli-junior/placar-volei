<script>
  import { descreverTime } from '../lib/jogadores.js';

  // Condução da rodada em andamento (CV8.DS3.US5): quadra do placar, partida,
  // fila, reis e eliminados. As ações vêm de fora.
  let {
    rodada,
    conducao,
    quadra = null,
    ocupado = false,
    erroQuadra = null,
    onChamar = () => {},
    onCriarQuadra = () => {},
    onVincular = () => {},
    onDesvincular = () => {},
    onCancelar = () => {},
  } = $props();

  let codigo = $state('');
  let confirmandoCancelar = $state(false);
  const temPartida = $derived(Boolean(conducao.partida));
  const timeDa = (fila) => conducao.em_quadra.find((t) => t.fila === fila);

  function vincular(evento) {
    evento.preventDefault();
    const digitado = codigo.trim();
    if (digitado) onVincular(digitado);
    codigo = '';
  }
</script>

<section class="conducao" aria-labelledby="titulo-conducao">
  <h2 id="titulo-conducao">Rodada {rodada.numero} <span class="alvo">· alvo {rodada.alvo}</span></h2>

  <div class="bloco" aria-labelledby="titulo-quadra">
    <h3 id="titulo-quadra">Quadra do placar</h3>
    {#if erroQuadra}<p class="erro" role="alert">{erroQuadra}</p>{/if}
    {#if quadra}
      <p class="ajuda">
        Quadra <strong>{quadra.codigo}</strong>{#if quadra.nome} ({quadra.nome}){/if}:
        {#if quadra.disponivel}<span class="ok">disponível</span> ·
          <a href="/quadra/{quadra.codigo}" target="_blank" rel="noopener">Abrir o placar</a>
        {:else}<span class="ruim">indisponível — vincule de novo</span>{/if}
      </p>
    {:else}
      <p class="ajuda">Nenhuma quadra vinculada. O placar mostra as duplas da partida chamada.</p>
    {/if}
    {#if !temPartida}
      <div class="botoes">
        <button class="secundario" type="button" onclick={onCriarQuadra} disabled={ocupado}>Criar quadra e vincular</button>
        {#if quadra}<button class="secundario" type="button" onclick={onDesvincular} disabled={ocupado}>Desvincular</button>{/if}
      </div>
      <form class="vincular" onsubmit={vincular}>
        <label for="codigo-quadra-vinculo">Ou vincule uma quadra existente pelo código</label>
        <div class="linha">
          <input id="codigo-quadra-vinculo" type="text" inputmode="numeric" maxlength="5" autocomplete="off" placeholder="00000" bind:value={codigo} disabled={ocupado} />
          <button class="secundario" type="submit" disabled={ocupado || !codigo.trim()}>Vincular</button>
        </div>
      </form>
    {/if}
  </div>

  <div class="bloco" aria-labelledby="titulo-partida">
    <h3 id="titulo-partida">{temPartida ? 'Partida em quadra' : 'Próxima partida'}</h3>
    {#if conducao.em_quadra.length === 2}
      <p class="confronto" role="status">
        <strong>Time {conducao.em_quadra[0].fila}</strong> × <strong>Time {conducao.em_quadra[1].fila}</strong>
        {#if temPartida}<span class="selo">chamada</span>{/if}
      </p>
      <ul class="times">
        {#each conducao.em_quadra as time (time.fila)}
          <li class:incompleto={time.incompleto}>
            <span class="posicao">Time {time.fila}</span>
            <span class="jogadores">{descreverTime(time)}</span>
            {#if time.vitorias > 0}<span class="selo">{time.vitorias} vitória seguida</span>{/if}
            {#if time.incompleto}<span class="aviso">Incompleto: escolhe o parceiro na sua vez.</span>{/if}
          </li>
        {/each}
      </ul>
    {:else if conducao.em_quadra.length === 1}
      <p class="ajuda">Time {conducao.em_quadra[0].fila} está sozinho na quadra: a fase de fila terminou.</p>
    {:else}
      <p class="ajuda">Ninguém em quadra: a fase de fila terminou.</p>
    {/if}
    <div class="botoes">
      <button class="acao-principal" type="button" onclick={onChamar} disabled={ocupado || !conducao.pode_chamar}>Chamar partida</button>
    </div>
    {#if conducao.motivo}<p class="ajuda" role="status">{conducao.motivo}</p>{/if}
  </div>

  <div class="bloco" aria-labelledby="titulo-fila">
    <h3 id="titulo-fila">Fila ({conducao.fila.length})</h3>
    {#if !conducao.fila.length}
      <p class="ajuda">Ninguém esperando.</p>
    {:else}
      <ol class="times">
        {#each conducao.fila as time, i (time.fila)}
          <li class:incompleto={time.incompleto}>
            <span class="posicao">{i + 1}º · Time {time.fila}</span>
            <span class="jogadores">{descreverTime(time)}</span>
            {#if time.incompleto}<span class="aviso">Incompleto: escolhe o parceiro na sua vez.</span>{/if}
          </li>
        {/each}
      </ol>
    {/if}
  </div>

  <div class="bloco" aria-labelledby="titulo-reis">
    <h3 id="titulo-reis">Reis ({conducao.reis.length})</h3>
    {#if !conducao.reis.length}
      <p class="ajuda">Ninguém com 2 vitórias seguidas ainda.</p>
    {:else}
      <ol class="times">
        {#each conducao.reis as time (time.fila)}
          <li><span class="posicao">{time.ordem}º rei · Time {time.fila}</span> <span class="jogadores">{descreverTime(time)}</span></li>
        {/each}
      </ol>
    {/if}
  </div>

  <div class="bloco" aria-labelledby="titulo-eliminados">
    <h3 id="titulo-eliminados">Eliminados ({conducao.eliminados.length})</h3>
    {#if !conducao.eliminados.length}
      <p class="ajuda">Ninguém perdeu ainda. Quem perde uma partida sai da rodada.</p>
    {:else}
      <ul class="eliminados">
        {#each conducao.eliminados as j (j.id)}
          <li>{j.nome} <span class="ajuda">(Time {j.time})</span></li>
        {/each}
      </ul>
    {/if}
  </div>

  <div class="botoes">
    {#if confirmandoCancelar}
      <p class="ajuda">Cancelar a rodada {rodada.numero}? A fila é descartada e a presença volta a ser editável.</p>
      <button class="perigo" type="button" onclick={() => { confirmandoCancelar = false; onCancelar(); }} disabled={ocupado}>Sim, cancelar rodada</button>
      <button class="secundario" type="button" onclick={() => confirmandoCancelar = false}>Voltar</button>
    {:else}
      <button class="secundario" type="button" onclick={() => confirmandoCancelar = true} disabled={ocupado}>Cancelar rodada</button>
    {/if}
  </div>
</section>

<style>
  .conducao { display: flex; flex-direction: column; gap: .9rem; padding: 1rem; border: 1px solid var(--borda-ativa); border-radius: var(--raio-padrao); background: var(--fundo-superficie); color: var(--texto-forte); }
  h2 { margin: 0; font-size: var(--texto-destaque); }
  h3 { margin: 0 0 .4rem; font-size: var(--texto-corpo); }
  .alvo { color: var(--texto-suave); font-weight: 600; }
  .bloco { display: flex; flex-direction: column; gap: .5rem; padding: .75rem; border: 1px solid var(--borda-sutil); border-radius: var(--raio-padrao); background: var(--fundo-cartao); }
  .ajuda { margin: 0; color: var(--texto-suave); font-size: var(--texto-apoio); }
  .ok { color: var(--texto-medio); font-weight: 700; }
  .ruim, .erro { color: var(--estado-erro-suave); font-weight: 700; }
  .erro { margin: 0; font-size: var(--texto-apoio); }
  a { color: var(--texto-forte); }
  .confronto { margin: 0; padding: .6rem .75rem; border-radius: var(--raio-justo); background: var(--fundo-cartao-ativo); }
  .times, .eliminados { display: flex; flex-direction: column; gap: .4rem; margin: 0; padding: 0; list-style: none; }
  .times li { display: flex; flex-wrap: wrap; align-items: baseline; gap: .25rem .75rem; padding: .5rem .65rem; border: 1px solid var(--borda-sutil); border-radius: var(--raio-justo); background: var(--fundo-superficie); }
  .eliminados li { font-size: var(--texto-apoio); }
  .posicao { font-weight: 800; }
  .jogadores { flex: 1 1 12rem; }
  .selo { padding: .05rem .45rem; border-radius: var(--raio-circular); background: var(--fundo-cartao-ativo); color: var(--texto-medio); font-size: var(--texto-micro); font-weight: 700; }
  .aviso { flex-basis: 100%; color: var(--texto-medio); font-size: var(--texto-legenda); }
  .botoes { display: flex; flex-wrap: wrap; gap: .5rem; align-items: center; }
  .botoes .ajuda { flex-basis: 100%; }
  .vincular { display: flex; flex-direction: column; gap: .35rem; }
  .vincular label { font-size: var(--texto-apoio); color: var(--texto-medio); }
  .linha { display: flex; gap: .5rem; }
  input { box-sizing: border-box; min-height: 44px; width: 8rem; padding: .5rem .75rem; border: 1px solid var(--acao-secundaria); border-radius: 10px; background: var(--fundo-base); color: var(--texto-forte); font: inherit; letter-spacing: .1em; }
  input:focus-visible { border-color: var(--foco-cor); box-shadow: var(--foco-anel); outline: none; }
  .acao-principal { display: inline-flex; align-items: center; justify-content: center; min-height: 48px; padding: 0 1.1rem; border: 0; border-radius: 10px; background: var(--acao-primaria); color: var(--acao-primaria-texto); font: inherit; font-weight: 800; cursor: pointer; }
  .secundario, .perigo { display: inline-flex; align-items: center; min-height: 44px; padding: 0 .85rem; border: 1px solid var(--acao-secundaria); border-radius: 12px; background: var(--fundo-superficie); color: var(--texto-medio); font: inherit; font-size: var(--texto-apoio); font-weight: 700; cursor: pointer; }
  .perigo { border-color: var(--estado-erro); color: var(--estado-erro-suave); }
  button:disabled { opacity: .45; cursor: not-allowed; }
</style>
