<script>
  import { onMount } from 'svelte';
  import Icone from './Icone.svelte';
  import Avatar from './Avatar.svelte';
  import PortaoSegredo from './PortaoSegredo.svelte';
  import { guardarSegredoDono, lerSegredoDono } from '../lib/preferencias.js';
  import { chamarSessao } from '../lib/jogadores.js';
  import { comSinal, contarPartida, dataDaResenha, nomesDe, recorde } from '../lib/resenha.js';

  // Resenha do Joguinho (CV8.DS9.US25): a tela é feita para o print que vai
  // para o grupo. Prêmios e números vêm prontos de /api/sessao/estatisticas.
  let { onVoltar = () => {} } = $props();

  let segredo = $state(lerSegredoDono());
  let dados = $state(null);
  let carregando = $state(false);
  let erro = $state(null);

  const jogadores = $derived(dados?.jogadores ?? {});
  const rei = $derived(dados?.premios?.find((p) => p.id === 'rei') ?? null);
  const premios = $derived((dados?.premios ?? []).filter((p) => p.id !== 'rei'));
  const aoVivo = $derived(Boolean(dados?.sessao && !dados.sessao.encerrada_em));

  // A foto e as iniciais usam o nome completo; o texto usa o curto.
  const rosto = (id) => ({ ...jogadores[id], nome: jogadores[id]?.nome_completo ?? jogadores[id]?.nome ?? '?' });

  onMount(() => { if (segredo) carregar(); });

  async function carregar() {
    carregando = true;
    erro = null;
    try {
      dados = await chamarSessao(segredo, '/estatisticas');
    } catch (e) {
      if (e.recusado) { segredo = ''; guardarSegredoDono(''); }
      erro = e.message || 'Não foi possível carregar a resenha.';
    } finally {
      carregando = false;
    }
  }

  async function entrar(digitado) {
    segredo = digitado;
    await carregar();
    if (segredo) guardarSegredoDono(segredo);
  }
</script>

<main class="resenha">
  <nav class="topo" aria-label="Navegação">
    <button class="botao" type="button" onclick={onVoltar}><Icone nome="voltar" tamanho="1.2em" traco={2.6} /><span>Joguinho</span></button>
    {#if segredo}
      <button class="botao" type="button" onclick={carregar} disabled={carregando}><Icone nome="atualizar" tamanho="1.1em" /><span>Atualizar</span></button>
    {/if}
  </nav>

  {#if !segredo}
    <h1 class="titulo-simples">Resenha</h1>
    <PortaoSegredo {erro} ocupado={carregando} onEntrar={entrar} />
  {:else if erro}
    <div class="alerta" role="alert"><Icone nome="alerta" tamanho="1.1em" /><span>{erro}</span></div>
  {:else if !dados}
    <p class="vazio">Carregando a resenha…</p>
  {:else if !dados.sessao}
    <h1 class="titulo-simples">Resenha</h1>
    <p class="vazio">Ainda não teve joguinho. Sem jogo, sem resenha. 🤷</p>
  {:else}
    <header class="capa">
      <p class="sobretitulo">🏐 Resenha do joguinho</p>
      <h1>{dataDaResenha(dados.sessao.aberta_em)}</h1>
      {#if aoVivo}<p class="ao-vivo">● parcial: o joguinho ainda está rolando</p>{/if}
      <ul class="numeros" aria-label="Resumo do dia">
        <li><strong>{dados.resumo.partidas}</strong><span>partidas</span></li>
        <li><strong>{dados.resumo.pontos}</strong><span>pontos</span></li>
        <li><strong>{dados.resumo.jogadores}</strong><span>na areia</span></li>
        <li><strong>{dados.resumo.rodadas}</strong><span>rodadas</span></li>
      </ul>
    </header>

    {#if dados.resumo.partidas === 0}
      <p class="vazio">Nenhuma partida encerrada ainda. A resenha começa no primeiro ponto. 👀</p>
    {/if}

    {#if rei}
      <section class="rei" aria-labelledby="titulo-rei">
        <span class="coroa" aria-hidden="true">👑</span>
        <h2 id="titulo-rei">{rei.titulo}</h2>
        <div class="rostos">
          {#each rei.jogadores as id (id)}
            <figure>
              <Avatar {segredo} jogador={rosto(id)} tamanho={rei.jogadores.length > 2 ? 64 : 88} />
              <figcaption>{jogadores[id]?.nome}</figcaption>
            </figure>
          {/each}
        </div>
        <p class="feito">{rei.texto}</p>
      </section>
    {/if}

    {#if premios.length}
      <section aria-labelledby="titulo-premios">
        <h2 id="titulo-premios" class="secao">🏅 Os prêmios</h2>
        <ul class="premios">
          {#each premios as premio, i (premio.id)}
            {@const partida = premio.partida ? contarPartida(premio.partida, jogadores) : null}
            <li class="premio {premio.tom}" style:--atraso="{i * 60}ms">
              <span class="emoji" aria-hidden="true">{premio.emoji}</span>
              <div>
                <h3>{premio.titulo}</h3>
                {#if partida}
                  <p class="placar-premio"><strong>{partida.placar}</strong></p>
                  <p class="nomes">{partida.vencedores} <span class="contra">{premio.partida.lado_a.length > 1 ? 'venceram' : 'venceu'}</span> {partida.perdedores}</p>
                {:else}
                  <p class="nomes">{nomesDe(premio.jogadores, jogadores)}</p>
                {/if}
                <p class="texto">{premio.texto}</p>
              </div>
            </li>
          {/each}
        </ul>
      </section>
    {/if}

    {#if dados.galeria.length}
      <section aria-labelledby="titulo-galeria">
        <h2 id="titulo-galeria" class="secao">📸 Galeria da resenha</h2>
        <ul class="galeria">
          {#each dados.galeria as g (g.jogador)}
            <li class="retrato {g.tom}">
              <Avatar {segredo} jogador={rosto(g.jogador)} tamanho={56} />
              <div class="quem">
                <strong class="nome">{jogadores[g.jogador]?.nome}</strong>
                <span class="recorde">{recorde(g)}</span>
              </div>
              <div class="titulo-jogador">
                <span class="emoji-titulo" aria-hidden="true">{g.emoji}</span>
                <span>{g.titulo}</span>
                {#if g.selos.length}<span class="selos" aria-label="Outros prêmios">{g.selos.join(' ')}</span>{/if}
              </div>
            </li>
          {/each}
        </ul>
      </section>
    {/if}

    {#if dados.campeoes.length}
      <section aria-labelledby="titulo-campeoes">
        <h2 id="titulo-campeoes" class="secao">🏆 Campeões das rodadas</h2>
        <ul class="campeoes">
          {#each dados.campeoes as c (c.rodada)}
            <li><span class="rodada">Rodada {c.rodada}</span><strong>{nomesDe(c.jogadores, jogadores)}</strong></li>
          {/each}
        </ul>
      </section>
    {/if}

    {#if dados.tabela.length}
      <section aria-labelledby="titulo-tabela">
        <h2 id="titulo-tabela" class="secao">📊 A tabela não mente</h2>
        <div class="rolagem">
          <table>
            <thead>
              <tr><th scope="col">#</th><th scope="col">Jogador</th><th scope="col" title="Jogos">J</th><th scope="col" title="Vitórias">V</th><th scope="col" title="Derrotas">D</th><th scope="col" title="Aproveitamento">%</th><th scope="col" title="Saldo de pontos da dupla">Saldo</th></tr>
            </thead>
            <tbody>
              {#each dados.tabela as t, i (t.jogador)}
                <tr>
                  <td>{i + 1}</td>
                  <th scope="row">{jogadores[t.jogador]?.nome}</th>
                  <td>{t.jogos}</td>
                  <td>{t.vitorias}</td>
                  <td>{t.derrotas}</td>
                  <td>{t.aproveitamento}</td>
                  <td class:positivo={t.saldo > 0} class:negativo={t.saldo < 0}>{comSinal(t.saldo)}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
        <p class="nota">Pontos são da dupla (ou trio) em que o jogador estava. Reclamações com a organização. 🙃</p>
      </section>
    {/if}

    <footer>🏐 Placar Vôlei</footer>
  {/if}
</main>

<style>
  .resenha { box-sizing: border-box; max-width: 640px; margin: 0 auto; padding: calc(var(--sa-topo) + 1rem) 1rem calc(var(--sa-baixo) + 2rem); display: flex; flex-direction: column; gap: 1.25rem; color: var(--texto-forte); }
  .topo { display: flex; justify-content: space-between; gap: .5rem; }
  .botao { display: inline-flex; align-items: center; gap: .4rem; min-height: 44px; padding: 0 .85rem; border: 1px solid var(--acao-secundaria); border-radius: 12px; background: var(--fundo-superficie); color: var(--texto-medio); font: inherit; font-size: var(--texto-apoio); font-weight: 700; cursor: pointer; }
  .botao:disabled { opacity: .45; cursor: not-allowed; }
  .titulo-simples { margin: 0; font-size: var(--texto-titulo-forte); }
  .vazio { margin: 0; color: var(--texto-suave); text-align: center; }
  .alerta { display: flex; gap: .5rem; align-items: center; padding: .75rem; border-radius: var(--raio-padrao); background: rgba(var(--veu), .06); color: var(--estado-erro-suave); }

  .capa { position: relative; overflow: hidden; padding: 1.25rem 1rem 1rem; border-radius: var(--raio-amplo); background: radial-gradient(120% 90% at 85% -10%, var(--marca-tenue), transparent 60%), var(--fundo-superficie); border: 1px solid var(--borda-sutil); text-align: center; }
  .sobretitulo { margin: 0; color: var(--marca-suave); font-size: var(--texto-micro); font-weight: 800; letter-spacing: .14em; text-transform: uppercase; }
  .capa h1 { margin: .2rem 0 0; font-family: var(--fonte-numeros); font-size: 2.6rem; line-height: 1; font-weight: 600; text-transform: uppercase; }
  .ao-vivo { margin: .4rem 0 0; color: var(--estado-erro-suave); font-size: var(--texto-legenda); font-weight: 700; }
  .numeros { display: grid; grid-template-columns: repeat(4, 1fr); gap: .4rem; margin: 1rem 0 0; padding: 0; list-style: none; }
  .numeros li { display: flex; flex-direction: column; padding: .45rem .2rem; border-radius: var(--raio-justo); background: rgba(var(--veu), .05); }
  .numeros strong { font-family: var(--fonte-numeros); font-size: 2rem; line-height: 1; color: var(--marca); }
  .numeros span { color: var(--texto-suave); font-size: var(--texto-micro); }

  .rei { display: flex; flex-direction: column; align-items: center; gap: .5rem; padding: 1.25rem 1rem; border-radius: var(--raio-amplo); border: 1px solid var(--marca); background: linear-gradient(180deg, var(--marca-tenue), transparent 75%), var(--fundo-superficie); box-shadow: 0 0 32px var(--marca-tenue); text-align: center; animation: surgir 300ms ease-out both; }
  .coroa { font-size: 2.6rem; line-height: 1; animation: balancar 2.4s ease-in-out infinite; }
  .rei h2 { margin: 0; color: var(--marca-suave); font-size: var(--texto-titulo-forte); text-transform: uppercase; letter-spacing: .04em; }
  .rostos { display: flex; flex-wrap: wrap; justify-content: center; gap: 1rem; }
  .rostos figure { display: flex; flex-direction: column; align-items: center; gap: .35rem; margin: 0; }
  .rostos :global(.avatar) { box-shadow: 0 0 0 3px var(--marca); }
  .rostos figcaption { font-weight: 800; }
  .feito { margin: 0; color: var(--texto-medio); font-weight: 700; }

  .secao { margin: 0 0 .6rem; font-size: var(--texto-titulo); }

  .premios { display: grid; grid-template-columns: 1fr; gap: .6rem; margin: 0; padding: 0; list-style: none; }
  @media (min-width: 520px) { .premios { grid-template-columns: 1fr 1fr; } }
  .premio { --tom: var(--acento-info); display: flex; gap: .75rem; align-items: flex-start; padding: .8rem .9rem; border-radius: var(--raio-padrao); background: var(--fundo-superficie); border: 1px solid var(--borda-sutil); border-left: 4px solid var(--tom); animation: surgir 300ms ease-out both; animation-delay: var(--atraso, 0ms); }
  .premio.positivo, .retrato.positivo { --tom: var(--marca); }
  .premio.negativo, .retrato.negativo { --tom: var(--estado-erro); }
  .premio.neutro, .retrato.neutro { --tom: var(--acento-info); }
  .emoji { font-size: 2rem; line-height: 1.1; }
  .premio h3 { margin: 0; color: var(--tom); font-size: var(--texto-destaque); }
  .nomes { margin: .15rem 0 0; font-weight: 800; }
  .contra { color: var(--texto-suave); font-weight: 600; }
  .placar-premio { margin: .1rem 0 0; font-family: var(--fonte-numeros); font-size: 1.8rem; line-height: 1; }
  .texto { margin: .2rem 0 0; color: var(--texto-suave); font-size: var(--texto-apoio); }

  .galeria { display: flex; flex-direction: column; gap: .5rem; margin: 0; padding: 0; list-style: none; }
  .retrato { --tom: var(--acento-info); display: grid; grid-template-columns: auto 1fr; grid-template-areas: 'foto quem' 'foto titulo'; column-gap: .75rem; row-gap: .15rem; align-items: center; padding: .6rem .75rem; border-radius: var(--raio-padrao); background: var(--fundo-superficie); border: 1px solid var(--borda-sutil); }
  .retrato :global(.avatar) { grid-area: foto; box-shadow: 0 0 0 3px var(--tom); }
  .quem { grid-area: quem; display: flex; align-items: baseline; justify-content: space-between; gap: .5rem; min-width: 0; }
  .nome { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .recorde { flex: none; color: var(--texto-suave); font-size: var(--texto-legenda); font-weight: 700; }
  .titulo-jogador { grid-area: titulo; display: flex; flex-wrap: wrap; align-items: center; gap: .35rem; color: var(--tom); font-weight: 800; }
  .selos { color: var(--texto-forte); }

  .campeoes { display: flex; flex-direction: column; gap: .4rem; margin: 0; padding: 0; list-style: none; }
  .campeoes li { display: flex; justify-content: space-between; gap: .75rem; padding: .6rem .8rem; border-radius: var(--raio-padrao); background: var(--fundo-superficie); border: 1px solid var(--borda-sutil); }
  .rodada { color: var(--texto-suave); font-weight: 700; }
  .campeoes strong { text-align: right; color: var(--marca-suave); }

  .rolagem { overflow-x: auto; border-radius: var(--raio-padrao); border: 1px solid var(--borda-sutil); }
  table { width: 100%; border-collapse: collapse; background: var(--fundo-superficie); font-size: var(--texto-apoio); }
  th, td { padding: .5rem .45rem; text-align: center; border-bottom: 1px solid var(--borda-sutil); }
  thead th { color: var(--texto-suave); font-size: var(--texto-micro); text-transform: uppercase; }
  tbody th { text-align: left; font-weight: 700; white-space: nowrap; }
  tbody tr:last-child > * { border-bottom: 0; }
  td.positivo { color: var(--estado-sucesso); font-weight: 800; }
  td.negativo { color: var(--estado-erro-suave); font-weight: 800; }
  .nota { margin: .5rem 0 0; color: var(--texto-suave); font-size: var(--texto-legenda); }

  footer { color: var(--texto-suave); font-size: var(--texto-legenda); text-align: center; }

  @keyframes surgir { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
  @keyframes balancar { 0%, 100% { transform: rotate(-6deg); } 50% { transform: rotate(6deg); } }
  @media (prefers-reduced-motion: reduce) {
    .rei, .premio, .coroa { animation: none; }
  }
</style>
