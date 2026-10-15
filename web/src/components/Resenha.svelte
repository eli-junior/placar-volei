<script>
  import { onMount, tick } from 'svelte';
  import { toBlob } from 'html-to-image';
  import Icone from './Icone.svelte';
  import Avatar from './Avatar.svelte';
  import PortaoSegredo from './PortaoSegredo.svelte';
  import { guardarSegredoDono, lerSegredoDono } from '../lib/preferencias.js';
  import { chamarSessao } from '../lib/jogadores.js';
  import { comSinal, contarPartida, dataDaResenha, montarCartoes, nomeDoArquivo, nomesDe, recorde } from '../lib/resenha.js';

  // Resenha do Joguinho (CV8.DS9.US25): cartões 4:5 de tamanho fixo, um por
  // imagem para o grupo. O que se vê é o que se baixa: cada cartão vira um PNG
  // de 1080 × 1350. Prêmios e números vêm prontos de /api/sessao/estatisticas.
  let { onVoltar = () => {} } = $props();

  // 4:5, o formato que o WhatsApp mostra inteiro no feed da conversa.
  const IMAGEM = { largura: 1080, altura: 1350 };

  let segredo = $state(lerSegredoDono());
  let dados = $state(null);
  let carregando = $state(false);
  let erro = $state(null);
  let gerando = $state(null); // "Gerando 2 de 6…" enquanto exporta
  let aviso = $state(null);
  /** @type {HTMLElement[]} */
  let nos = $state([]);

  const jogadores = $derived(dados?.jogadores ?? {});
  const rei = $derived(dados?.premios?.find((p) => p.id === 'rei') ?? null);
  const aoVivo = $derived(Boolean(dados?.sessao && !dados.sessao.encerrada_em));
  const cartoes = $derived(dados?.sessao ? montarCartoes(dados) : []);
  const data = $derived(dataDaResenha(dados?.sessao?.aberta_em));
  const podeCompartilhar = typeof navigator !== 'undefined' && typeof navigator.canShare === 'function';

  // A foto e as iniciais usam o nome completo; o texto usa o curto.
  const rosto = (id) => ({ ...jogadores[id], nome: jogadores[id]?.nome_completo ?? jogadores[id]?.nome ?? '?' });
  const tamanhoDoRei = (n) => (n === 1 ? '22cqw' : n === 2 ? '18cqw' : '13cqw');
  const titulos = { premios: '🏅 Os prêmios', galeria: '📸 Galeria da resenha', tabela: '📊 A tabela não mente' };

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

  async function gerarImagens() {
    await tick();
    await document.fonts?.ready;
    const fundo = getComputedStyle(document.body).getPropertyValue('--fundo-base').trim() || '#0f172a';
    const arquivos = [];
    for (const [i, no] of nos.entries()) {
      if (!no) continue;
      gerando = `Gerando ${i + 1} de ${cartoes.length}…`;
      const blob = await toBlob(no, { pixelRatio: 1, canvasWidth: IMAGEM.largura, canvasHeight: IMAGEM.altura, backgroundColor: fundo });
      if (blob) arquivos.push(new File([blob], nomeDoArquivo(dados.sessao.aberta_em, i + 1), { type: 'image/png' }));
    }
    return arquivos;
  }

  async function exportar(modo) {
    if (gerando) return;
    aviso = null;
    try {
      const arquivos = await gerarImagens();
      if (modo === 'compartilhar' && navigator.canShare?.({ files: arquivos })) {
        gerando = 'Abrindo o compartilhamento…';
        await navigator.share({ files: arquivos, title: `Resenha do joguinho — ${data}` });
      } else {
        for (const arquivo of arquivos) {
          const link = document.createElement('a');
          link.href = URL.createObjectURL(arquivo);
          link.download = arquivo.name;
          link.click();
          setTimeout(() => URL.revokeObjectURL(link.href), 10_000);
        }
        aviso = `${arquivos.length} ${arquivos.length === 1 ? 'imagem baixada' : 'imagens baixadas'}. É só mandar no grupo.`;
      }
    } catch (e) {
      // Fechar a folha de compartilhamento não é erro.
      if (e?.name !== 'AbortError') aviso = 'Não deu para gerar as imagens. Tente de novo.';
    } finally {
      gerando = null;
    }
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
    <h1 class="titulo-simples">Resenha</h1>
    <section class="exportar" aria-label="Levar para o grupo">
      {#if podeCompartilhar}
        <button class="acao-principal" type="button" onclick={() => exportar('compartilhar')} disabled={Boolean(gerando)}><Icone nome="compartilhar" tamanho="1.1em" /><span>Mandar no grupo</span></button>
      {/if}
      <button class={podeCompartilhar ? 'botao' : 'acao-principal'} type="button" onclick={() => exportar('baixar')} disabled={Boolean(gerando)}><Icone nome="copiar" tamanho="1.1em" /><span>Baixar {cartoes.length} {cartoes.length === 1 ? 'imagem' : 'imagens'}</span></button>
      <p class="estado" role="status">{gerando ?? aviso ?? ''}</p>
    </section>

    <ol class="cartoes" aria-label="Cartões da resenha">
      {#each cartoes as cartao, i (`${cartao.tipo}-${cartao.parte}`)}
        <li>
          <article class="cartao" bind:this={nos[i]} aria-label="Cartão {cartao.numero} de {cartao.total}">
            <header class="faixa"><span>🏐 Resenha do joguinho</span><span>{data}</span></header>

            {#if cartao.tipo === 'capa'}
              <div class="capa">
                <h2 class="data">{data}</h2>
                {#if aoVivo}<p class="ao-vivo">● parcial: o joguinho ainda está rolando</p>{/if}
                <ul class="numeros" aria-label="Resumo do dia">
                  <li><strong>{dados.resumo.partidas}</strong><span>partidas</span></li>
                  <li><strong>{dados.resumo.pontos}</strong><span>pontos</span></li>
                  <li><strong>{dados.resumo.jogadores}</strong><span>na areia</span></li>
                  <li><strong>{dados.resumo.rodadas}</strong><span>rodadas</span></li>
                </ul>
                {#if rei}
                  <div class="rei">
                    <span class="coroa" aria-hidden="true">👑</span>
                    <h3>{rei.titulo}</h3>
                    <div class="rostos">
                      {#each rei.jogadores as id (id)}
                        <figure><Avatar {segredo} jogador={rosto(id)} tamanho={tamanhoDoRei(rei.jogadores.length)} /><figcaption>{jogadores[id]?.nome}</figcaption></figure>
                      {/each}
                    </div>
                    <p class="feito">{rei.texto}</p>
                  </div>
                {:else}
                  <p class="sem-jogo">Nenhuma partida encerrada ainda. A resenha começa no primeiro ponto. 👀</p>
                {/if}
                {#if dados.campeoes.length}
                  <ul class="campeoes" aria-label="Campeões das rodadas">
                    {#each dados.campeoes.slice(-3) as c (c.rodada)}
                      <li><span>🏆 Rodada {c.rodada}</span><strong>{nomesDe(c.jogadores, jogadores)}</strong></li>
                    {/each}
                  </ul>
                {/if}
              </div>
            {:else}
              <h2 class="titulo-cartao">{titulos[cartao.tipo]}{#if cartao.partes > 1}<span class="parte">{cartao.parte}/{cartao.partes}</span>{/if}</h2>

              {#if cartao.tipo === 'premios'}
                <ul class="premios">
                  {#each cartao.itens as premio (premio.id)}
                    {@const partida = premio.partida ? contarPartida(premio.partida, jogadores) : null}
                    <li class="premio {premio.tom}">
                      <span class="emoji" aria-hidden="true">{premio.emoji}</span>
                      <div>
                        <h3>{premio.titulo}{#if partida}<span class="placar-premio">{partida.placar}</span>{/if}</h3>
                        {#if partida}
                          <p class="nomes">{partida.vencedores} <span class="contra">{premio.partida.lado_a.length > 1 ? 'venceram' : 'venceu'}</span> {partida.perdedores}</p>
                        {:else}
                          <p class="nomes">{nomesDe(premio.jogadores, jogadores)}</p>
                        {/if}
                        <p class="texto">{premio.texto}</p>
                      </div>
                    </li>
                  {/each}
                </ul>
              {:else if cartao.tipo === 'galeria'}
                <ul class="galeria">
                  {#each cartao.itens as g (g.jogador)}
                    <li class="retrato {g.tom}">
                      <Avatar {segredo} jogador={rosto(g.jogador)} tamanho="14cqw" />
                      <strong class="nome">{jogadores[g.jogador]?.nome}</strong>
                      <span class="titulo-jogador"><span aria-hidden="true">{g.emoji}</span> {g.titulo}</span>
                      <span class="recorde">{recorde(g)}{#if g.selos.length}<span class="selos" aria-label="Outros prêmios">{g.selos.join(' ')}</span>{/if}</span>
                    </li>
                  {/each}
                </ul>
              {:else}
                <table>
                  <thead>
                    <tr><th scope="col">#</th><th scope="col">Jogador</th><th scope="col" title="Jogos">J</th><th scope="col" title="Vitórias">V</th><th scope="col" title="Derrotas">D</th><th scope="col" title="Aproveitamento">%</th><th scope="col" title="Saldo de pontos da dupla">Saldo</th></tr>
                  </thead>
                  <tbody>
                    {#each cartao.itens as t (t.jogador)}
                      <tr>
                        <td>{dados.tabela.indexOf(t) + 1}</td>
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
                <p class="nota">Pontos são da dupla (ou trio) em que o jogador estava. Reclamações com a organização. 🙃</p>
              {/if}
            {/if}

            <footer class="faixa"><span>Placar Vôlei</span><span>{cartao.numero}/{cartao.total}</span></footer>
          </article>
        </li>
      {/each}
    </ol>
  {/if}
</main>

<style>
  .resenha { box-sizing: border-box; width: 100%; max-width: 640px; margin: 0 auto; padding: calc(var(--sa-topo) + 1rem) 1rem calc(var(--sa-baixo) + 2rem); display: flex; flex-direction: column; gap: 1rem; color: var(--texto-forte); }
  .topo { display: flex; justify-content: space-between; gap: .5rem; }
  .botao, .acao-principal { display: inline-flex; align-items: center; justify-content: center; gap: .45rem; min-height: 48px; padding: 0 1rem; border-radius: 12px; font: inherit; font-weight: 800; cursor: pointer; }
  .botao { border: 1px solid var(--acao-secundaria); background: var(--fundo-superficie); color: var(--texto-medio); font-size: var(--texto-apoio); }
  .acao-principal { border: 0; background: var(--acao-primaria); color: var(--acao-primaria-texto); }
  .botao:disabled, .acao-principal:disabled { opacity: .45; cursor: not-allowed; }
  .titulo-simples { margin: 0; font-size: var(--texto-titulo-forte); }
  .vazio { margin: 0; color: var(--texto-suave); text-align: center; }
  .alerta { display: flex; gap: .5rem; align-items: center; padding: .75rem; border-radius: var(--raio-padrao); background: rgba(var(--veu), .06); color: var(--estado-erro-suave); }

  .exportar { display: flex; flex-wrap: wrap; gap: .5rem; }
  .exportar > button { flex: 1 1 12rem; }
  .estado { flex-basis: 100%; min-height: 1.2em; margin: 0; color: var(--texto-suave); font-size: var(--texto-apoio); text-align: center; }

  .cartoes { display: flex; flex-direction: column; gap: 1rem; margin: 0; padding: 0; list-style: none; }
  /* A altura é travada pela largura do item: `aspect-ratio` sozinho cede ao conteúdo. */
  .cartoes > li { container-type: inline-size; }

  /* O cartão: 4:5, tudo medido em cqw para a imagem sair igual em qualquer tela. */
  .cartao { container-type: inline-size; box-sizing: border-box; display: flex; flex-direction: column; width: 100%; height: 125cqw; overflow: hidden; padding: 5cqw; border-radius: var(--raio-amplo); border: 1px solid var(--borda-sutil); background: radial-gradient(110% 70% at 90% -5%, var(--marca-tenue), transparent 60%), var(--fundo-superficie); font-size: 4cqw; animation: surgir 300ms ease-out both; }
  .faixa { display: flex; justify-content: space-between; gap: 2cqw; color: var(--marca-suave); font-size: 2.9cqw; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }
  footer.faixa { margin-top: auto; padding-top: 2cqw; color: var(--texto-suave); letter-spacing: .04em; }
  .titulo-cartao { margin: 2.5cqw 0; font-size: 6.5cqw; line-height: 1.1; }
  .parte { margin-left: 1.5cqw; color: var(--texto-suave); font-size: 4.5cqw; }

  .capa { flex: 1; display: flex; flex-direction: column; align-items: center; text-align: center; min-height: 0; }
  .data { margin: 2cqw 0 0; font-family: var(--fonte-numeros); font-size: 12cqw; line-height: 1; font-weight: 600; text-transform: uppercase; }
  .ao-vivo { margin: 1cqw 0 0; color: var(--estado-erro-suave); font-size: 3.3cqw; font-weight: 700; }
  .numeros { align-self: stretch; display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5cqw; margin: 3.5cqw 0 0; padding: 0; list-style: none; }
  .numeros li { display: flex; flex-direction: column; padding: 1.5cqw 0; border-radius: 2.5cqw; background: rgba(var(--veu), .05); }
  .numeros strong { font-family: var(--fonte-numeros); font-size: 9cqw; line-height: 1; color: var(--marca); }
  .numeros span { color: var(--texto-suave); font-size: 3cqw; }
  .rei { align-self: stretch; display: flex; flex-direction: column; align-items: center; gap: 1.5cqw; margin-top: 3.5cqw; padding: 3cqw; border-radius: 5cqw; border: 1px solid var(--marca); background: linear-gradient(180deg, var(--marca-tenue), transparent 75%); }
  .coroa { font-size: 8cqw; line-height: 1; }
  .rei h3 { margin: 0; color: var(--marca-suave); font-size: 6.5cqw; text-transform: uppercase; letter-spacing: .04em; }
  .rostos { display: flex; flex-wrap: wrap; justify-content: center; gap: 4cqw; }
  .rostos figure { display: flex; flex-direction: column; align-items: center; gap: 1cqw; margin: 0; }
  .rostos :global(.avatar) { box-shadow: 0 0 0 .8cqw var(--marca); }
  .rostos figcaption { font-size: 4.5cqw; font-weight: 800; }
  .feito { margin: 0; color: var(--texto-medio); font-size: 4.2cqw; font-weight: 700; }
  .sem-jogo { margin: auto 0; color: var(--texto-suave); }
  .campeoes { align-self: stretch; display: flex; flex-direction: column; gap: 1cqw; margin: auto 0 0; padding: 3cqw 0 0; list-style: none; }
  .campeoes li { display: flex; justify-content: space-between; gap: 2cqw; font-size: 3.6cqw; }
  .campeoes span { color: var(--texto-suave); font-weight: 700; }
  .campeoes strong { color: var(--marca-suave); text-align: right; }

  .premios { display: flex; flex-direction: column; gap: 1.8cqw; margin: 0; padding: 0; list-style: none; }
  .premio { --tom: var(--acento-info); display: flex; gap: 3cqw; align-items: flex-start; padding: 1.8cqw 3cqw; border-radius: 3cqw; background: rgba(var(--veu), .04); border-left: 1.2cqw solid var(--tom); }
  .premio.positivo, .retrato.positivo { --tom: var(--marca); }
  .premio.negativo, .retrato.negativo { --tom: var(--estado-erro); }
  .premio.neutro, .retrato.neutro { --tom: var(--acento-info); }
  .emoji { font-size: 7.5cqw; line-height: 1.1; }
  .premio h3 { margin: 0; color: var(--tom); font-size: 4.8cqw; line-height: 1.15; }
  .placar-premio { margin-left: 2cqw; color: var(--texto-forte); font-family: var(--fonte-numeros); font-size: 6cqw; }
  .nomes { margin: .3cqw 0 0; font-size: 4cqw; font-weight: 800; }
  .contra { color: var(--texto-suave); font-weight: 600; }
  .texto { margin: .3cqw 0 0; color: var(--texto-suave); font-size: 3.5cqw; line-height: 1.25; }

  .galeria { display: grid; grid-template-columns: 1fr 1fr; gap: 2cqw; margin: 0; padding: 0; list-style: none; }
  .retrato { --tom: var(--acento-info); display: flex; flex-direction: column; align-items: center; gap: .4cqw; padding: 2cqw; border-radius: 3.5cqw; background: rgba(var(--veu), .04); text-align: center; }
  .retrato :global(.avatar) { box-shadow: 0 0 0 .8cqw var(--tom); margin-bottom: 1cqw; }
  .nome { font-size: 4.3cqw; }
  .titulo-jogador { color: var(--tom); font-size: 3.6cqw; font-weight: 800; line-height: 1.2; }
  .recorde { color: var(--texto-suave); font-size: 3cqw; font-weight: 700; }
  .selos { margin-left: 1cqw; }

  table { width: 100%; border-collapse: collapse; font-size: 3.7cqw; }
  th, td { padding: 1.3cqw 1cqw; text-align: center; border-bottom: 1px solid var(--borda-sutil); }
  thead th { color: var(--texto-suave); font-size: 2.9cqw; text-transform: uppercase; }
  tbody th { text-align: left; font-weight: 700; white-space: nowrap; }
  tbody tr:last-child > * { border-bottom: 0; }
  td.positivo { color: var(--estado-sucesso); font-weight: 800; }
  td.negativo { color: var(--estado-erro-suave); font-weight: 800; }
  .nota { margin: 2cqw 0 0; color: var(--texto-suave); font-size: 3cqw; }

  @keyframes surgir { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
  @media (prefers-reduced-motion: reduce) { .cartao { animation: none; } }
</style>
