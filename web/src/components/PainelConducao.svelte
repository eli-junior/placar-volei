<script>
  import { ajusteDaNota, descreverTime, notaAtual } from '../lib/jogadores.js';
  import { oQueSePerde } from '../lib/joguinho.js';

  // Condução da rodada em andamento (CV8.DS3.US5): quadra do placar, partida,
  // fila, reis e eliminados. As ações vêm de fora.
  let {
    rodada,
    conducao,
    quadra = null,
    ocupado = false,
    erroQuadra = null,
    onChamar = () => {},
    onEncerrar = () => {},
    onAnular = () => {},
    onPular = () => {},
    onEscalar = () => {},
    podeDesfazer = false,
    onDesfazer = () => {},
    onSubstituir = () => {},
    erroSubstituicao = null,
    onIniciarMataMata = () => {},
    onEncerrarSemCampeao = () => {},
    erroEscalacao = null,
    onCriarQuadra = () => {},
    onVincular = () => {},
    onDesvincular = () => {},
    onCancelar = () => {},
  } = $props();

  let codigo = $state('');
  let confirmandoCancelar = $state(false);
  let confirmandoDesfazer = $state(false);
  let confirmandoAnular = $state(false);
  let confirmandoSemRei = $state(false);
  let saiu = $state('');
  let entra = $state('');
  const sub = $derived(conducao.substituicao);

  function substituir(evento) {
    evento.preventDefault();
    if (saiu && entra) onSubstituir(saiu, entra);
    saiu = '';
    entra = '';
  }
  const temPartida = $derived(Boolean(conducao.partida));
  const placar = $derived(conducao.partida?.placar ?? null);
  const fimDaFila = $derived(conducao.fase === 'fim_da_fila');
  const mataMata = $derived(conducao.fase === 'mata_mata');
  const mm = $derived(conducao.mata_mata);
  // Rodada triangular de 3 times (RN-18): `tri` só existe enquanto há partidas a jogar.
  const tri = $derived(conducao.triangular);
  const semRei = $derived(conducao.fase === 'sem_rei');
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
        {:else if temPartida}<span class="ruim">indisponível — anule a partida para trocar de quadra</span>
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

  {#if conducao.escalacao}
    {@const esc = conducao.escalacao}
    <div class="bloco destaque" aria-labelledby="titulo-escalacao">
      <h3 id="titulo-escalacao">Escolher {esc.faltam > 1 ? `os ${esc.faltam} parceiros` : 'o parceiro'} do Time {esc.time}</h3>
      <p class="ajuda">
        {esc.jogadores?.join(' e ') ?? esc.jogador} {esc.jogadores?.length > 1 ? 'estão' : 'está'} {esc.origem === 'atrasado' ? 'chegando no meio da rodada' : 'sem time completo'} e {esc.jogadores?.length > 1 ? 'escolhem' : 'escolhe'} {esc.faltam > 1 ? `${esc.faltam} parceiros` : 'o parceiro'} na vez.
      </p>
      {#if erroEscalacao}<p class="erro" role="alert">{erroEscalacao}</p>{/if}
      {#if esc.ninguem}
        <p class="ajuda">Ninguém elegível agora: não há jogador eliminado disponível para completar o Time {esc.time}.</p>
        {#if esc.pode_pular}
          <button class="secundario" type="button" onclick={onPular} disabled={ocupado}>Pular o Time {esc.time} (vai para o fim da fila)</button>
        {:else if conducao.rodada_triangular}
          <p class="ajuda">Na rodada triangular ninguém é eliminado antes da final e a ordem das partidas é fixa: encerre a rodada sem campeão (abaixo) para sortear de novo.</p>
        {:else}
          <p class="ajuda">Não há outro time para entrar no lugar dele: cancele a rodada se precisar seguir.</p>
        {/if}
      {:else}
        {#each esc.grupos as grupo (grupo.rotulo)}
          <p class="ajuda"><strong>{grupo.rotulo}</strong></p>
          {#if esc.aviso_hh}<p class="ajuda">Não há alternativa de gênero: o time fechará só de um sexo, por falta de opção.</p>{/if}
          <ul class="times">
            {#each grupo.jogadores as j (j.id)}
              <li>
                <span class="jogadores">{j.nome} <span class="ajuda">({j.genero === 'H' ? 'Homem' : 'Mulher'} · nota {notaAtual(j)}{ajusteDaNota(j)})</span></span>
                <button class="secundario" type="button" onclick={() => onEscalar(j.id)} disabled={ocupado} aria-label="Escalar {j.nome} com {esc.jogador}">Escalar</button>
              </li>
            {/each}
          </ul>
        {/each}
      {/if}
    </div>
  {/if}

  {#if sub && sub.entram.length}
    <form class="bloco" onsubmit={substituir} aria-labelledby="titulo-substituir">
      <h3 id="titulo-substituir">Substituir quem saiu</h3>
      <p class="ajuda">O time mantém vitórias e posição. Quem sai fica ausente nas próximas rodadas.</p>
      {#if erroSubstituicao}<p class="erro" role="alert">{erroSubstituicao}</p>{/if}
      <label for="sub-saiu">Quem saiu</label>
      <select id="sub-saiu" bind:value={saiu} disabled={ocupado}>
        <option value="">Escolha…</option>
        {#each sub.saem as j (j.id)}<option value={j.id}>{j.nome} (Time {j.time})</option>{/each}
      </select>
      <label for="sub-entra">Quem entra</label>
      <select id="sub-entra" bind:value={entra} disabled={ocupado}>
        <option value="">Escolha…</option>
        {#each sub.entram as j (j.id)}<option value={j.id}>{j.nome} · {j.genero === 'H' ? 'Homem' : 'Mulher'} · {j.origem === 'aguardando' ? 'aguardando na fila' : 'eliminado'}</option>{/each}
      </select>
      <button class="secundario" type="submit" disabled={ocupado || !saiu || !entra}>Substituir</button>
    </form>
  {/if}

  <div class="bloco" aria-labelledby="titulo-partida">
    <h3 id="titulo-partida">{temPartida ? 'Partida em quadra' : mataMata ? 'Próxima partida do mata-mata' : 'Próxima partida'}</h3>
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
            {#if time.vitorias > 0}<span class="selo" title="{time.vitorias} {time.vitorias === 1 ? 'vitória seguida' : 'vitórias seguidas'}"><span aria-hidden="true">{time.vitorias}V</span><span class="sr-only">{time.vitorias} {time.vitorias === 1 ? 'vitória seguida' : 'vitórias seguidas'}</span></span>{/if}
            {#if time.incompleto}<span class="aviso">Incompleto: escolhe o parceiro na sua vez.</span>{/if}
          </li>
        {/each}
      </ul>
    {/if}
    {#if temPartida && placar}
      <p class="placar" role="status">
        Placar: <strong>{placar.a} × {placar.b}</strong>
        {#if placar.encerrada}<span class="selo">terminou — Time {placar.vencedor === 'A' ? conducao.partida.time_a : conducao.partida.time_b} venceu</span>{:else}<span class="selo">em jogo</span>{/if}
      </p>
    {/if}
    {#if tri && conducao.em_quadra.length === 2}
      {@const [a, b] = conducao.em_quadra}
      {@const espera = conducao.fila[0]}
      <p class="faixa" role="status">
        {#if tri.etapa === 1}
          Rodada triangular: os 3 times se enfrentam e só é rei quem vence os outros dois.
        {:else if tri.etapa === 2}
          Triângulo: o Time {espera.fila} venceu e espera. Se o Time {b.fila} vencer, enfrenta o Time {espera.fila} na final; se o Time {a.fila} vencer, termina sem rei.
        {:else}
          Final do triângulo: o Time {a.fila} vence e é o rei; se perder, termina sem rei.
        {/if}
      </p>
    {/if}
    {#if semRei}
      <p class="faixa" role="status">Rodada triangular terminou sem rei. As partidas contam no saldo; encerre a rodada para liberar o próximo sorteio.</p>
    {/if}
    {#if fimDaFila && mm && conducao.rodada_triangular}
      <p class="faixa" role="status">Time {mm.desafiante.fila} venceu os outros dois e é o rei. Coroar o campeão encerra a rodada.</p>
    {:else if fimDaFila && mm}
      <p class="faixa" role="status">
        A fase de fila terminou. {mm.rivais.length
          ? `Time ${mm.desafiante.fila} abre o mata-mata contra ${mm.rivais.map((t) => `Time ${t.fila}`).join(', depois ')}.`
          : `Time ${mm.desafiante.fila} abre o mata-mata e, sem reis, já é o campeão.`}
        Ao iniciar, ninguém mais entra na rodada.
      </p>
    {/if}
    {#if mataMata && mm}
      <p class="faixa" role="status">Mata-mata: quem ganha fica, quem perde sai. Time {mm.desafiante.fila} em quadra.{mm.rivais.length > 1 ? ` Depois: ${mm.rivais.slice(1).map((t) => `Time ${t.fila}`).join(', ')}.` : ''}</p>
    {/if}
    <div class="botoes">
      {#if conducao.pode_encerrar_sem_campeao}
        {#if confirmandoSemRei}
          <p class="ajuda">Encerrar a rodada sem campeão? Não dá para desfazer a última partida depois.</p>
          <button class="perigo" type="button" onclick={() => { confirmandoSemRei = false; onEncerrarSemCampeao(); }} disabled={ocupado}>Sim, encerrar sem campeão</button>
          <button class="secundario" type="button" onclick={() => (confirmandoSemRei = false)}>Voltar</button>
        {:else}
          <button class="acao-principal" type="button" onclick={() => (confirmandoSemRei = true)} disabled={ocupado}>Encerrar sem campeão</button>
        {/if}
      {:else if conducao.pode_iniciar_mata_mata}
        <button class="acao-principal" type="button" onclick={onIniciarMataMata} disabled={ocupado}>{mm && mm.rivais.length ? 'Iniciar mata-mata' : 'Coroar campeão'}</button>
      {:else if temPartida}
        <button class="acao-principal" type="button" onclick={onEncerrar} disabled={ocupado || !conducao.pode_encerrar}>Encerrar partida</button>
      {:else}
        <button class="acao-principal" type="button" onclick={onChamar} disabled={ocupado || !conducao.pode_chamar}>Chamar partida</button>
      {/if}
    </div>
    {#if temPartida && conducao.motivo_encerrar}<p class="ajuda">{conducao.motivo_encerrar}</p>
    {:else if !temPartida && !fimDaFila && !semRei && conducao.motivo}<p class="ajuda" role="status">{conducao.motivo}</p>{/if}
    {#if temPartida && conducao.pode_anular}
      {#if confirmandoAnular}
        <p class="ajuda">Anular a partida Time {conducao.partida.time_a} × Time {conducao.partida.time_b}? Ela não conta: os dois times voltam a ser a próxima partida e a rodada segue. O placar da quadra não é apagado.</p>
        <div class="botoes">
          <button class="perigo" type="button" onclick={() => { confirmandoAnular = false; onAnular(); }} disabled={ocupado}>Sim, anular a partida</button>
          <button class="secundario" type="button" onclick={() => (confirmandoAnular = false)}>Manter</button>
        </div>
      {:else}
        <div class="botoes">
          <button class="secundario" type="button" onclick={() => (confirmandoAnular = true)} disabled={ocupado}>Anular partida</button>
        </div>
      {/if}
    {/if}
  </div>

  {#if conducao.historico.length}
    <div class="bloco" aria-labelledby="titulo-historico">
      <h3 id="titulo-historico">Partidas encerradas ({conducao.historico.length})</h3>
      <ol class="times">
        {#each conducao.historico as h (h.ordem)}
          <li>
            <span class="posicao">{h.ordem}ª</span>
            <span class="jogadores confronto">
              <span class="lado" class:vencedor={h.vencedor === h.time_a}>Time {h.time_a}</span>
              <strong class="resultado"><span class="pt a" class:ganhou={h.vencedor === h.time_a}>{h.placar_a}</span> <span class="x" aria-hidden="true">×</span> <span class="pt b" class:ganhou={h.vencedor === h.time_b}>{h.placar_b}</span></strong>
              <span class="lado" class:vencedor={h.vencedor === h.time_b}>Time {h.time_b}</span>
            </span>
            {#if h.fase === 'mata_mata'}<span class="selo">mata-mata</span>{/if}
            <span class="selo">Time {h.vencedor} venceu</span>
          </li>
        {/each}
      </ol>
      {#if podeDesfazer}
        {#if confirmandoDesfazer}
          <p class="ajuda">Desfaz a última partida e volta a fila, os reis e as vitórias ao que eram antes dela. Só dá para desfazer uma vez seguida.</p>
          <div class="botoes">
            <button class="secundario" type="button" onclick={() => { confirmandoDesfazer = false; onDesfazer(); }} disabled={ocupado}>Sim, desfazer a partida</button>
            <button class="secundario" type="button" onclick={() => (confirmandoDesfazer = false)}>Manter</button>
          </div>
        {:else}
          <button class="secundario" type="button" onclick={() => (confirmandoDesfazer = true)} disabled={ocupado}>Desfazer última partida</button>
        {/if}
      {/if}
    </div>
  {/if}

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

  {#if conducao.saldos.length}
    <div class="bloco" aria-labelledby="titulo-saldos">
      <h3 id="titulo-saldos">Saldo da rodada</h3>
      <p class="ajuda">Pontos feitos − sofridos; quem foi escalado soma os dois times.</p>
      <ul class="eliminados">
        {#each conducao.saldos as s (s.id)}
          <li>{s.nome} <span class="ajuda">({s.partidas} partida{s.partidas === 1 ? '' : 's'})</span> <strong>{s.saldo > 0 ? '+' : ''}{s.saldo}</strong></li>
        {/each}
      </ul>
    </div>
  {/if}

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
      <p class="ajuda">Cancelar a rodada {rodada.numero}? Perde-se: {oQueSePerde(rodada, conducao).join('; ')}. Os registros ficam gravados, mas a rodada deixa de contar e a presença volta a ser editável. A quadra do placar não é tocada.</p>
      <button class="perigo" type="button" onclick={() => { confirmandoCancelar = false; onCancelar(); }} disabled={ocupado}>Sim, cancelar rodada</button>
      <button class="secundario" type="button" onclick={() => confirmandoCancelar = false}>Voltar</button>
    {:else}
      <button class="secundario" type="button" onclick={() => confirmandoCancelar = true} disabled={ocupado}>Cancelar rodada</button>
    {/if}
  </div>
</section>

<style>
  .confronto { display: inline-flex; align-items: center; flex-wrap: wrap; gap: 6px 10px; }
  .confronto .lado { opacity: .8; }
  .confronto .lado.vencedor { opacity: 1; font-weight: 700; }
  /* Placarzinho: fundo escuro nos dois temas, cores do time fixas e claras
     para manter o contraste (as do tema claro são escuras demais para ele). */
  .confronto .resultado {
    display: inline-flex;
    align-items: stretch;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 8px;
    background: #0b1220;
    font-family: var(--fonte-numeros);
    font-size: 1.35rem;
    font-weight: 600;
    line-height: 1;
    font-variant-numeric: tabular-nums;
    white-space: nowrap;
  }
  .confronto .pt { min-width: 2ch; padding: 4px 9px 2px; text-align: center; opacity: .8; }
  .confronto .pt.a { color: #22d3ee; }
  .confronto .pt.b { color: #fb923c; }
  .confronto .pt.ganhou { opacity: 1; text-shadow: 0 0 10px currentColor; }
  .confronto .x { align-self: center; padding: 0 2px; color: #94a3b8; font-size: .9rem; }

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
  .destaque { border-color: var(--borda-ativa); }
  .placar { margin: 0; font-size: var(--texto-destaque); }
  .faixa { margin: 0; padding: .6rem .75rem; border: 1px solid var(--borda-ativa); border-radius: var(--raio-justo); background: var(--fundo-cartao-ativo); font-weight: 700; }
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
