<script>
  import { onMount } from 'svelte';
  import Icone from './Icone.svelte';
  import Avatar from './Avatar.svelte';
  import PortaoSegredo from './PortaoSegredo.svelte';
  import PainelRodada from './PainelRodada.svelte';
  import PainelConducao from './PainelConducao.svelte';
  import { guardarSegredoDono, lerApelido, lerSegredoDono } from '../lib/preferencias.js';
  import { criarConexao } from '../lib/conexao.js';
  import { chamarRodada, chamarSessao, criarQuadraDoPlacar, estadoMaisNovo, faltamParaSortear, moverPosicao, rotuloSincronia } from '../lib/jogadores.js';

  let { onVoltar = () => {} } = $props();

  let segredo = $state(lerSegredoDono());
  let estado = $state(null);
  let carregando = $state(false);
  let ocupado = $state(false);
  let erro = $state(null);
  let confirmandoEncerrar = $state(false);
  let nome = $state('');
  let genero = $state('');
  let nota = $state('');
  let erroRapido = $state(null);
  let alvo = $state(10);
  let conectado = $state(false);
  let online = $state(typeof navigator === 'undefined' ? true : navigator.onLine);
  let erroQuadra = $state(null);
  let erroEscalacao = $state(null);

  const presentes = $derived(estado?.presentes ?? []);
  const ausentes = $derived(estado?.ausentes ?? []);
  const rodada = $derived(estado?.rodada ?? null);
  // Com rodada em proposta ou em andamento a presença fica travada (RN-15).
  const travada = $derived(Boolean(rodada));
  const podeAtrasado = $derived(rodada?.estado === 'em_andamento' && !rodada.mata_mata_iniciado);
  const sincronia = $derived(rotuloSincronia(conectado, online));
  const faltam = $derived(faltamParaSortear(presentes.length, estado?.minimo ?? 4));

  // Estado novo só entra se for mais recente que o mostrado: a resposta HTTP de
  // quem agiu e a mensagem do WebSocket podem chegar fora de ordem.
  function aplicar(novo) {
    estado = estadoMaisNovo(estado, novo);
  }

  // Sincronia entre aparelhos (US-05): o segredo vai na primeira mensagem,
  // nunca na URL.
  const conexao = criarConexao({
    criarSocket: () => {
      const protocolo = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const socket = new WebSocket(`${protocolo}//${window.location.host}/ws/gerenciador`);
      socket.addEventListener('open', () => socket.send(JSON.stringify({ tipo: 'AUTENTICAR', segredo })));
      return socket;
    },
    aoMensagem: (mensagem) => {
      if (mensagem.tipo === 'ESTADO_INICIAL') { conectado = true; conexao.confirmar(); aplicar(mensagem.payload); }
      else if (mensagem.tipo === 'ESTADO_ATUALIZADO') aplicar(mensagem.payload);
    },
    aoCair: () => { conectado = false; },
    aoFechar: (codigo) => {
      if (codigo === 4401) { sair(); erro = 'Segredo recusado. Confira e tente de novo.'; return false; }
      return true;
    },
  });

  onMount(() => {
    if (segredo) { carregar(); conexao.conectar('gerenciador'); }
    // Reserva da sincronia: ao voltar o foco ou a rede, reconecta e atualiza.
    const aoVoltar = () => {
      if (document.hidden || !segredo) return;
      conexao.retomar();
      if (!ocupado) carregar();
    };
    const aoMudarRede = () => { online = navigator.onLine; if (online) aoVoltar(); };
    document.addEventListener('visibilitychange', aoVoltar);
    window.addEventListener('online', aoMudarRede);
    window.addEventListener('offline', aoMudarRede);
    return () => {
      document.removeEventListener('visibilitychange', aoVoltar);
      window.removeEventListener('online', aoMudarRede);
      window.removeEventListener('offline', aoMudarRede);
      conexao.desconectar();
    };
  });

  async function carregar() {
    carregando = true;
    erro = null;
    try {
      aplicar(await chamarSessao(segredo, ''));
    } catch (e) {
      if (e.status === 404) sair();
      erro = e.message || 'Não foi possível carregar a sessão.';
    } finally {
      carregando = false;
    }
  }

  async function entrar(digitado) {
    segredo = digitado;
    await carregar();
    if (segredo) { guardarSegredoDono(segredo); conexao.conectar('gerenciador'); }
  }

  function sair() {
    conexao.desconectar();
    conectado = false;
    segredo = '';
    estado = null;
    guardarSegredoDono('');
  }

  // Toda ação devolve o estado novo da sessão.
  async function agir(caminho, opcoes, chamar = chamarSessao) {
    ocupado = true;
    erro = null;
    try {
      const resposta = await chamar(segredo, caminho, opcoes);
      aplicar(resposta);
      return resposta;
    } catch (e) {
      if (e.status === 404) { sair(); }
      const mensagem = e.message;
      // 409 ou ordem que não bate com os presentes: o estado mudou em outro
      // aparelho; recarrega para refletir.
      if (e.status === 409 || e.campo === 'jogador_ids') await carregar();
      erro = mensagem;
      return null;
    } finally {
      ocupado = false;
    }
  }

  const abrir = () => agir('', { metodo: 'POST' });
  const marcar = (j) => agir(`/presencas/${j.id}`, { metodo: 'PUT' });
  const desmarcar = (j) => agir(`/presencas/${j.id}`, { metodo: 'DELETE' });
  const mover = (j, delta) => agir('/ordem', { metodo: 'PUT', corpo: { jogador_ids: moverPosicao(presentes.map(p => p.id), j.id, delta) } });

  const registrarAtrasado = (j) => agir('/atrasado', { metodo: 'POST', corpo: { jogador_id: j.id } }, chamarRodada);
  const sortear = () => agir('/sorteio', { metodo: 'POST', corpo: { alvo } }, chamarRodada);
  const resortear = () => agir('/resortear', { metodo: 'POST', corpo: { alvo } }, chamarRodada);
  const confirmar = () => agir('/confirmar', { metodo: 'POST' }, chamarRodada);
  const descartar = () => agir('/descartar', { metodo: 'POST' }, chamarRodada);
  const cancelarRodada = () => agir('/cancelar', { metodo: 'POST' }, chamarRodada);

  // A proposta mostra o alvo gravado; trocar de alvo na tela vale no próximo resortear.
  $effect(() => { if (rodada) alvo = rodada.alvo; });

  // Ações do vínculo e da chamada: o erro aparece no próprio bloco da quadra.
  async function agirQuadra(acao) {
    ocupado = true;
    erroQuadra = null;
    try {
      aplicar(await acao());
    } catch (e) {
      if (e.status === 404) { sair(); erro = e.message; return; }
      erroQuadra = e.message;
      if (e.status === 409) await carregar();
    } finally {
      ocupado = false;
    }
  }
  const chamarPartida = () => agirQuadra(() => chamarRodada(segredo, '/chamar-partida', { metodo: 'POST' }));
  const iniciarMataMata = () => agirQuadra(() => chamarRodada(segredo, '/iniciar-mata-mata', { metodo: 'POST' }));
  const encerrarPartida = () => agirQuadra(() => chamarRodada(segredo, '/encerrar-partida', { metodo: 'POST' }));
  async function escalar(jogadorId) {
    ocupado = true;
    erroEscalacao = null;
    try {
      aplicar(await chamarRodada(segredo, '/escalar-parceiro', { metodo: 'POST', corpo: { jogador_id: jogadorId } }));
    } catch (e) {
      if (e.status === 404) { sair(); erro = e.message; return; }
      const mensagem = e.message;
      if (e.status === 409) await carregar();
      erroEscalacao = mensagem;
    } finally {
      ocupado = false;
    }
  }
  const vincular = (codigo) => agirQuadra(() => chamarSessao(segredo, '/quadra', { metodo: 'PUT', corpo: { codigo } }));
  const desvincular = () => agirQuadra(() => chamarSessao(segredo, '/quadra', { metodo: 'DELETE' }));
  const criarEVincular = () => agirQuadra(async () => {
    const codigo = await criarQuadraDoPlacar(lerApelido() || 'Operador');
    return chamarSessao(segredo, '/quadra', { metodo: 'PUT', corpo: { codigo } });
  });

  async function encerrar() {
    confirmandoEncerrar = false;
    await agir('/encerrar', { metodo: 'POST' });
  }

  async function cadastrarRapido(evento) {
    evento.preventDefault();
    erroRapido = null;
    const corpo = { nome, genero };
    if (nota !== null && nota !== undefined && String(nota).trim() !== '') corpo.nota = Number(nota);
    ocupado = true;
    try {
      const r = await chamarSessao(segredo, '/presencas/rapido', { metodo: 'POST', corpo });
      aplicar({ ...r, jogador: undefined });
      nome = ''; genero = ''; nota = '';
    } catch (e) {
      if (e.status === 404) { sair(); erro = e.message; return; }
      erroRapido = e.message;
    } finally {
      ocupado = false;
    }
  }
</script>

<main class="sessao">
  <nav class="topo" aria-label="Navegação">
    <button class="voltar" type="button" onclick={onVoltar}><span aria-hidden="true">←</span><span>Início</span></button>
    {#if segredo}
      <span class="sincronia {sincronia.chave}">{sincronia.rotulo}</span>
      <button class="secundario" type="button" onclick={carregar} disabled={carregando}><Icone nome="atualizar" tamanho="1.1em" /><span>Atualizar</span></button>
    {/if}
  </nav>

  <h1>Sessão</h1>

  {#if !segredo}
    <PortaoSegredo {erro} ocupado={carregando} onEntrar={entrar} />
  {:else}
    {#if erro}<div class="alerta" role="alert"><Icone nome="alerta" tamanho="1.1em" /><span>{erro}</span></div>{/if}

    {#if !estado}
      <p class="vazio">Carregando…</p>
    {:else if !estado.sessao}
      <section class="cartao" aria-labelledby="titulo-sem-sessao">
        <h2 id="titulo-sem-sessao">Nenhuma sessão aberta</h2>
        <p class="ajuda">Abra a sessão do dia para marcar quem chegou.</p>
        <button class="acao-principal" type="button" onclick={abrir} disabled={ocupado}>Abrir sessão</button>
      </section>
    {:else}
      {#if rodada?.estado === 'proposta'}
        <PainelRodada {rodada} {ocupado} onResortear={resortear} onDescartar={descartar} onConfirmar={confirmar} />
      {:else if rodada && estado.conducao}
        <PainelConducao {rodada} conducao={estado.conducao} quadra={estado.quadra} {ocupado} {erroQuadra} onChamar={chamarPartida} onEncerrar={encerrarPartida} onEscalar={escalar} onIniciarMataMata={iniciarMataMata} {erroEscalacao} onCriarQuadra={criarEVincular} onVincular={vincular} onDesvincular={desvincular} onCancelar={cancelarRodada} />
      {:else if estado.ultimo_campeao}
        <section class="cartao" aria-labelledby="titulo-campeao">
          <h2 id="titulo-campeao">Campeões da rodada {estado.ultimo_campeao.rodada}</h2>
          <p role="status"><strong>Time {estado.ultimo_campeao.time}</strong> — {estado.ultimo_campeao.jogadores.join(' e ')}</p>
          <p class="ajuda">A rodada terminou. Já dá para sortear a próxima.</p>
        </section>
      {/if}

      <section aria-labelledby="titulo-presentes">
        <h2 id="titulo-presentes">Presentes ({presentes.length})</h2>
        <p class="ajuda" role="status">
          {#if faltam > 0}Faltam {faltam} para poder sortear (mínimo {estado.minimo}).{:else}Já dá para sortear (mínimo {estado.minimo}).{/if}
        </p>
        {#if !presentes.length}
          <p class="vazio">Ninguém marcado ainda. Marque abaixo, na ordem em que chegam.</p>
        {:else}
          <ol class="lista">
            {#each presentes as j, i (j.id)}
              <li>
                <span class="ordem" aria-label="Chegada nº {j.ordem}">{j.ordem}º</span>
                <Avatar {segredo} jogador={j} />
                <span class="nome">{j.nome}</span>
                <span class="genero">{j.genero === 'H' ? 'Homem' : 'Mulher'} · nota {j.nota}</span>
                <span class="botoes">
                  <button class="secundario" type="button" onclick={() => mover(j, -1)} disabled={ocupado || travada || i === 0} aria-label="Subir {j.nome}">↑</button>
                  <button class="secundario" type="button" onclick={() => mover(j, 1)} disabled={ocupado || travada || i === presentes.length - 1} aria-label="Descer {j.nome}">↓</button>
                  <button class="secundario" type="button" onclick={() => desmarcar(j)} disabled={ocupado || travada} aria-label="Desmarcar {j.nome}">Desmarcar</button>
                </span>
              </li>
            {/each}
          </ol>
        {/if}
      </section>

      {#if !rodada}
        <section class="cartao" aria-labelledby="titulo-sorteio">
          <h2 id="titulo-sorteio">Sortear a rodada</h2>
          <fieldset>
            <legend>Pontos da partida</legend>
            <label class="opcao"><input type="radio" name="alvo" value={10} bind:group={alvo} disabled={ocupado} /> 10 pontos</label>
            <label class="opcao"><input type="radio" name="alvo" value={12} bind:group={alvo} disabled={ocupado} /> 12 pontos</label>
          </fieldset>
          <button class="acao-principal" type="button" onclick={sortear} disabled={ocupado || faltam > 0}>Sortear duplas</button>
          {#if faltam > 0}<p class="ajuda">Faltam {faltam} presente(s) para sortear.</p>{/if}
        </section>
      {/if}

      <section aria-labelledby="titulo-ausentes">
        <h2 id="titulo-ausentes">Ausentes ({ausentes.length})</h2>
        {#if !ausentes.length}
          <p class="vazio">Todos os jogadores ativos estão presentes.</p>
        {:else}
          <ul class="lista">
            {#each ausentes as j (j.id)}
              <li>
                <Avatar {segredo} jogador={j} />
                <span class="nome">{j.nome}</span>
                <span class="genero">{j.genero === 'H' ? 'Homem' : 'Mulher'} · nota {j.nota}</span>
                {#if podeAtrasado}
                  <button class="secundario" type="button" onclick={() => registrarAtrasado(j)} disabled={ocupado} aria-label="Registrar {j.nome} como atrasado">Chegou atrasado</button>
                {:else}
                  <button class="secundario" type="button" onclick={() => marcar(j)} disabled={ocupado || travada} aria-label="Marcar {j.nome} como presente">Presente</button>
                {/if}
              </li>
            {/each}
          </ul>
        {/if}
      </section>

      {#if podeAtrasado}
        <p class="ajuda">Quem chega agora entra como atrasado, sozinho no fim da fila, e escolhe o parceiro na sua vez. Depois do início do mata-mata, só na próxima rodada.</p>
      {/if}
      {#if travada}
        <p class="ajuda">Presença travada: há uma rodada {rodada.estado === 'proposta' ? 'em proposta' : 'em andamento'}. Descarte ou cancele a rodada para marcar, desmarcar ou cadastrar.</p>
      {:else}
      <form class="cartao" onsubmit={cadastrarRapido} aria-labelledby="titulo-rapido" novalidate>
        <h2 id="titulo-rapido">Cadastro rápido</h2>
        <p class="ajuda">Quem não está na base: cadastra e já marca presente, no fim da ordem.</p>
        {#if erroRapido}<div class="alerta" role="alert"><Icone nome="alerta" tamanho="1.1em" /><span>{erroRapido}</span></div>{/if}
        <label for="rapido-nome">Nome</label>
        <input id="rapido-nome" type="text" maxlength="40" autocomplete="off" placeholder="Nome e sobrenome" bind:value={nome} disabled={ocupado} />
        <fieldset>
          <legend>Gênero</legend>
          <label class="opcao"><input type="radio" name="rapido-genero" value="H" bind:group={genero} disabled={ocupado} /> Homem</label>
          <label class="opcao"><input type="radio" name="rapido-genero" value="M" bind:group={genero} disabled={ocupado} /> Mulher</label>
        </fieldset>
        <label for="rapido-nota">Nota <span class="ajuda">(1 a 100; vazio = 60)</span></label>
        <input id="rapido-nota" type="number" inputmode="numeric" min="1" max="100" step="1" placeholder="60" bind:value={nota} disabled={ocupado} />
        <button class="acao-principal" type="submit" disabled={ocupado}>Cadastrar e marcar presente</button>
      </form>
      {/if}

      <section class="encerrar" aria-label="Encerrar sessão">
        {#if confirmandoEncerrar}
          <p class="ajuda">Encerrar a sessão do dia? A lista de presença sai da tela.</p>
          <div class="botoes">
            <button class="perigo" type="button" onclick={encerrar} disabled={ocupado}>Sim, encerrar</button>
            <button class="secundario" type="button" onclick={() => confirmandoEncerrar = false}>Cancelar</button>
          </div>
        {:else}
          <button class="secundario" type="button" onclick={() => confirmandoEncerrar = true} disabled={ocupado || travada}>Encerrar sessão</button>
          {#if travada}<p class="ajuda">Descarte a proposta ou cancele a rodada antes de encerrar a sessão.</p>{/if}
        {/if}
      </section>
    {/if}
  {/if}
</main>

<style>
  .sessao { box-sizing: border-box; max-width: 640px; margin: 0 auto; padding: calc(var(--sa-topo) + 1rem) 1rem calc(var(--sa-baixo) + 2rem); display: flex; flex-direction: column; gap: 1rem; color: var(--texto-forte); }
  .topo { display: flex; justify-content: space-between; gap: .5rem; }
  .sincronia { margin-left: auto; align-self: center; padding: .15rem .6rem; border-radius: var(--raio-circular); background: var(--fundo-cartao-ativo); color: var(--texto-medio); font-size: var(--texto-legenda); font-weight: 700; }
  .sincronia.reconectando, .sincronia.offline { color: var(--estado-erro-suave); }
  h1 { margin: 0; font-size: var(--texto-titulo-forte); }
  h2 { margin: 0 0 .5rem; font-size: var(--texto-destaque); }
  .voltar, .secundario, .perigo { display: inline-flex; align-items: center; gap: .4rem; min-height: 44px; padding: 0 .85rem; border: 1px solid var(--acao-secundaria); border-radius: 12px; background: var(--fundo-superficie); color: var(--texto-medio); font: inherit; font-size: var(--texto-apoio); font-weight: 700; cursor: pointer; }
  .secundario:disabled, .perigo:disabled { opacity: .45; cursor: not-allowed; }
  .perigo { border-color: var(--estado-erro); color: var(--estado-erro-suave); }
  .cartao { display: flex; flex-direction: column; gap: .6rem; padding: 1rem; border: 1px solid var(--borda-sutil); border-radius: var(--raio-padrao); background: var(--fundo-superficie); }
  .cartao h2 { margin: 0; }
  .ajuda { margin: 0; color: var(--texto-suave); font-size: var(--texto-apoio); }
  label, legend { font-size: var(--texto-apoio); color: var(--texto-medio); }
  input[type='text'], input[type='number'] { box-sizing: border-box; width: 100%; min-height: 48px; padding: .75rem .9rem; border: 1px solid var(--acao-secundaria); border-radius: 10px; outline: none; background: var(--fundo-base); color: var(--texto-forte); font: inherit; }
  input:focus-visible { border-color: var(--foco-cor); box-shadow: var(--foco-anel); }
  fieldset { display: flex; gap: 1.2rem; margin: 0; padding: 0; border: 0; }
  legend { padding: 0; margin-bottom: .3rem; }
  .opcao { display: inline-flex; align-items: center; gap: .5rem; min-height: 44px; }
  .opcao input { width: 1.2rem; height: 1.2rem; }
  .acao-principal { display: flex; align-items: center; justify-content: center; min-height: 52px; padding: 0 1.1rem; border: 0; border-radius: 10px; background: var(--acao-primaria); color: var(--acao-primaria-texto); font: inherit; font-weight: 800; cursor: pointer; }
  .acao-principal:disabled { opacity: .45; cursor: not-allowed; }
  .alerta { display: flex; align-items: flex-start; gap: .6rem; padding: .75rem; border: 1px solid color-mix(in srgb, var(--estado-erro) 45%, transparent); border-radius: 10px; background: color-mix(in srgb, var(--estado-erro) 12%, transparent); color: var(--estado-erro-suave); font-size: .83rem; line-height: 1.4; }
  .lista { display: flex; flex-direction: column; gap: .5rem; margin: 0; padding: 0; list-style: none; }
  li { display: flex; flex-wrap: wrap; align-items: center; gap: .5rem; padding: .6rem .75rem; border: 1px solid var(--borda-sutil); border-radius: var(--raio-padrao); background: var(--fundo-cartao); }
  .ordem { min-width: 2.2rem; font-family: var(--fonte-numeros); font-size: var(--texto-destaque); font-weight: 700; color: var(--texto-forte); }
  .nome { flex: 1 1 8rem; font-weight: 700; }
  .genero { color: var(--texto-suave); font-size: var(--texto-legenda); }
  .botoes { display: flex; gap: .4rem; flex-wrap: wrap; }
  .vazio { margin: 0; color: var(--texto-suave); }
  .encerrar { padding-top: .5rem; border-top: 1px solid var(--borda-sutil); display: flex; flex-direction: column; gap: .6rem; }
</style>
