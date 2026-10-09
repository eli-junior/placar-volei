<script>
  import { onMount } from 'svelte';
  import Icone from './Icone.svelte';
  import Avatar from './Avatar.svelte';
  import PortaoSegredo from './PortaoSegredo.svelte';
  import PainelRodada from './PainelRodada.svelte';
  import PainelConducao from './PainelConducao.svelte';
  import { guardarJoguinhoVelhoVisto, guardarSegredoDono, lerApelido, lerJoguinhoVelhoVisto, lerSegredoDono } from '../lib/preferencias.js';
  import { efeitoDaRetirada, joguinhoVelho, oQueSePerde } from '../lib/joguinho.js';
  import { criarConexao } from '../lib/conexao.js';
  import { chamarRodada, chamarSessao, criarQuadraDoPlacar, estadoMaisNovo, faltamParaSortear, mensagemFaltam, moverPara, moverPosicao, rotuloSincronia } from '../lib/jogadores.js';

  let { onVoltar = () => {}, onGerenciarJogadores = () => {} } = $props();

  let segredo = $state(lerSegredoDono());
  let estado = $state(null);
  let carregando = $state(false);
  let ocupado = $state(false);
  let erro = $state(null);
  let confirmandoEncerrar = $state(false);
  // Jogador que o operador está prestes a retirar da rodada (US19).
  let retirandoId = $state(null);
  let velhoVisto = $state(lerJoguinhoVelhoVisto());
  let alvo = $state(10);
  let formato = $state('dupla');
  let conectado = $state(false);
  let online = $state(typeof navigator === 'undefined' ? true : navigator.onLine);
  let erroQuadra = $state(null);
  let erroEscalacao = $state(null);
  let erroSubstituicao = $state(null);

  const presentes = $derived(estado?.presentes ?? []);
  const ausentes = $derived(estado?.ausentes ?? []);
  const rodada = $derived(estado?.rodada ?? null);
  // Com rodada em proposta ou em andamento a presença fica travada (RN-15).
  const travada = $derived(Boolean(rodada));
  // Joguinho de outro dia: avisa antes de seguir (some se o operador escolheu continuar).
  const velho = $derived(estado?.sessao && estado.sessao.id !== velhoVisto ? joguinhoVelho(estado.sessao.aberta_em) : null);
  const aSePerder = $derived(rodada ? oQueSePerde(rodada, estado?.conducao) : []);
  const podeAtrasado = $derived(rodada?.estado === 'em_andamento' && !rodada.mata_mata_iniciado);
  const sincronia = $derived(rotuloSincronia(conectado, online));
  const minimoSorteio = $derived(formato === 'trio' ? 6 : (estado?.minimo ?? 4));
  const faltam = $derived(faltamParaSortear(presentes.length, minimoSorteio));

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
      // Bloqueio por tentativas: o segredo salvo pode estar certo, então fica (US17).
      if (codigo === 4429) { erro = 'Muitas tentativas incorretas neste aparelho. Aguarde alguns minutos e recarregue.'; return false; }
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
      if (e.recusado) sair();
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
      if (e.recusado) { sair(); }
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

  // Arrastar pela alça: a lista mostra a nova ordem enquanto o dedo anda e só
  // grava ao soltar. Os centros dos itens são medidos ao começar (sem tremer).
  let listaEl = $state(null);
  let arrasto = $state(null);
  const idsPresentes = $derived(presentes.map(p => p.id));
  const listaExibida = $derived(
    arrasto ? moverPara(idsPresentes, arrasto.id, arrasto.destino).map(id => presentes.find(p => p.id === id)) : presentes
  );
  function iniciarArrasto(e, j) {
    if (ocupado || travada || !listaEl) return;
    e.preventDefault();
    const centros = [...listaEl.querySelectorAll(':scope > li')].map(li => {
      const r = li.getBoundingClientRect();
      return r.top + r.height / 2;
    });
    e.currentTarget.setPointerCapture(e.pointerId);
    arrasto = { id: j.id, destino: idsPresentes.indexOf(j.id), centros };
  }
  function moverArrasto(e) {
    if (!arrasto) return;
    const origem = idsPresentes.indexOf(arrasto.id);
    const destino = arrasto.centros.filter((c, i) => i !== origem && c < e.clientY).length;
    if (destino !== arrasto.destino) arrasto = { ...arrasto, destino };
  }
  async function soltarArrasto() {
    if (!arrasto) return;
    const { id, destino } = arrasto;
    arrasto = null;
    const nova = moverPara(idsPresentes, id, destino);
    if (nova.join() !== idsPresentes.join()) await agir('/ordem', { metodo: 'PUT', corpo: { jogador_ids: nova } });
  }

  const registrarAtrasado = (j) => agir('/atrasado', { metodo: 'POST', corpo: { jogador_id: j.id } }, chamarRodada);
  const sortear = () => agir('/sorteio', { metodo: 'POST', corpo: { alvo, formato } }, chamarRodada);
  const resortear = () => agir('/resortear', { metodo: 'POST', corpo: { alvo, formato } }, chamarRodada);
  const confirmar = () => agir('/confirmar', { metodo: 'POST' }, chamarRodada);
  const descartar = () => agir('/descartar', { metodo: 'POST' }, chamarRodada);
  const cancelarRodada = () => agir('/cancelar', { metodo: 'POST' }, chamarRodada);

  // A proposta mostra o alvo gravado; trocar de alvo na tela vale no próximo resortear.
  $effect(() => { if (rodada) { alvo = rodada.alvo; formato = rodada.formato ?? 'dupla'; } });

  // Ações do vínculo e da chamada: o erro aparece no próprio bloco da quadra.
  async function agirQuadra(acao) {
    ocupado = true;
    erroQuadra = null;
    try {
      aplicar(await acao());
    } catch (e) {
      if (e.recusado) { sair(); erro = e.message; return; }
      erroQuadra = e.message;
      if (e.status === 409) await carregar();
    } finally {
      ocupado = false;
    }
  }
  const chamarPartida = () => agirQuadra(() => chamarRodada(segredo, '/chamar-partida', { metodo: 'POST' }));
  const iniciarMataMata = () => agirQuadra(() => chamarRodada(segredo, '/iniciar-mata-mata', { metodo: 'POST' }));
  const encerrarSemCampeao = () => agirQuadra(() => chamarRodada(segredo, '/encerrar-sem-campeao', { metodo: 'POST' }));
  const encerrarPartida = () => agirQuadra(() => chamarRodada(segredo, '/encerrar-partida', { metodo: 'POST' }));
  const anularPartida = () => agirQuadra(() => chamarRodada(segredo, '/anular-partida', { metodo: 'POST' }));
  const retirar = async (j) => { retirandoId = null; await agir('/retirar', { metodo: 'POST', corpo: { jogador_id: j.id } }, chamarRodada); };

  async function pularTime() {
    ocupado = true;
    erroEscalacao = null;
    try {
      aplicar(await chamarRodada(segredo, '/pular-time', { metodo: 'POST' }));
    } catch (e) {
      if (e.recusado) { sair(); erro = e.message; return; }
      erroEscalacao = e.message;
      if (e.status === 409) await carregar();
    } finally {
      ocupado = false;
    }
  }

  async function escalar(jogadorId) {
    ocupado = true;
    erroEscalacao = null;
    try {
      aplicar(await chamarRodada(segredo, '/escalar-parceiro', { metodo: 'POST', corpo: { jogador_id: jogadorId } }));
    } catch (e) {
      if (e.recusado) { sair(); erro = e.message; return; }
      const mensagem = e.message;
      if (e.status === 409) await carregar();
      erroEscalacao = mensagem;
    } finally {
      ocupado = false;
    }
  }
  async function substituir(saiuId, entraId) {
    ocupado = true;
    erroSubstituicao = null;
    try {
      aplicar(await chamarRodada(segredo, '/substituir', { metodo: 'POST', corpo: { saiu_id: saiuId, entra_id: entraId } }));
    } catch (e) {
      if (e.recusado) { sair(); erro = e.message; return; }
      const mensagem = e.message;
      if (e.status === 409) await carregar();
      erroSubstituicao = mensagem;
    } finally {
      ocupado = false;
    }
  }
  const desfazerPartida = () => agirQuadra(() => chamarRodada(segredo, '/desfazer-partida', { metodo: 'POST' }));
  const vincular = (codigo) => agirQuadra(() => chamarSessao(segredo, '/quadra', { metodo: 'PUT', corpo: { codigo } }));
  const desvincular = () => agirQuadra(() => chamarSessao(segredo, '/quadra', { metodo: 'DELETE' }));
  const criarEVincular = () => agirQuadra(async () => {
    const codigo = await criarQuadraDoPlacar(lerApelido() || 'Operador');
    return chamarSessao(segredo, '/quadra', { metodo: 'PUT', corpo: { codigo } });
  });

  // Com rodada ativa, encerrar cancela a rodada na mesma operação (CV8.DS7.US20).
  async function encerrar() {
    confirmandoEncerrar = false;
    await agir('/encerrar', { metodo: 'POST', ...(rodada ? { corpo: { cancelar_rodada: true } } : {}) });
  }

  function continuarVelho() {
    velhoVisto = estado.sessao.id;
    guardarJoguinhoVelhoVisto(velhoVisto);
  }
</script>

<main class="sessao">
  <nav class="topo" aria-label="Navegação">
    <button class="voltar" type="button" onclick={onVoltar}><Icone nome="voltar" tamanho="1.2em" traco={2.6} /><span>Início</span></button>
    {#if segredo}
      <span class="sincronia {sincronia.chave}">{sincronia.rotulo}</span>
      <button class="secundario" type="button" onclick={carregar} disabled={carregando}><Icone nome="atualizar" tamanho="1.1em" /><span>Atualizar</span></button>
    {/if}
  </nav>

  <h1>Joguinho</h1>

  {#if !segredo}
    <PortaoSegredo {erro} ocupado={carregando} onEntrar={entrar} />
  {:else}
    {#if erro}<div class="alerta" role="alert"><Icone nome="alerta" tamanho="1.1em" /><span>{erro}</span></div>{/if}

    {#if !estado}
      <p class="vazio">Carregando…</p>
    {:else if !estado.sessao}
      <section class="cartao" aria-labelledby="titulo-sem-sessao">
        <h2 id="titulo-sem-sessao">Nenhum joguinho rolando</h2>
        <p class="ajuda">Comece um novo joguinho para marcar quem chegou.</p>
        <button class="acao-principal" type="button" onclick={abrir} disabled={ocupado}>Novo joguinho</button>
      </section>
    {:else}
      {#snippet encerrarJoguinho()}
        {#if confirmandoEncerrar}
          {#if rodada}
            <p class="ajuda" role="alert">
              Há a {rodada.estado === 'proposta' ? 'proposta' : 'rodada'} {rodada.numero} {rodada.estado === 'proposta' ? 'aberta' : 'em andamento'}. Encerrar o joguinho a cancela. Perde-se: {aSePerder.join('; ')}. {rodada.estado === 'em_andamento' ? 'A quadra do placar não é tocada. ' : ''}A lista de presença sai da tela.
            </p>
          {:else}
            <p class="ajuda">Encerrar o joguinho? A lista de presença sai da tela.</p>
          {/if}
          <div class="botoes">
            <button class="critico" type="button" onclick={encerrar} disabled={ocupado}>{rodada ? 'Cancelar rodada e encerrar' : 'Sim, encerrar'}</button>
            <button class="secundario" type="button" onclick={() => confirmandoEncerrar = false}>Voltar</button>
          </div>
        {:else}
          <button class="critico" type="button" onclick={() => confirmandoEncerrar = true} disabled={ocupado}>Encerrar joguinho</button>
        {/if}
      {/snippet}

      {#if velho}
        <section class="cartao velho" aria-labelledby="titulo-velho">
          <h2 id="titulo-velho">Joguinho aberto em {velho.data} ({velho.quando})</h2>
          <p class="ajuda">Este joguinho é de outro dia. Continue se a jogatina é a mesma, ou encerre para começar um novo.</p>
          {#if !confirmandoEncerrar}
            <button class="secundario" type="button" onclick={continuarVelho} disabled={ocupado}>Continuar este joguinho</button>
          {/if}
          {@render encerrarJoguinho()}
        </section>
      {/if}

      {#if rodada?.estado === 'proposta'}
        <PainelRodada {rodada} {ocupado} onResortear={resortear} onDescartar={descartar} onConfirmar={confirmar} />
      {:else if rodada && estado.conducao}
        <PainelConducao {rodada} conducao={estado.conducao} quadra={estado.quadra} {ocupado} {erroQuadra} onChamar={chamarPartida} onEncerrar={encerrarPartida} onAnular={anularPartida} onEscalar={escalar} onPular={pularTime} podeDesfazer={estado.pode_desfazer} onDesfazer={desfazerPartida} onSubstituir={substituir} {erroSubstituicao} onIniciarMataMata={iniciarMataMata} onEncerrarSemCampeao={encerrarSemCampeao} {erroEscalacao} onCriarQuadra={criarEVincular} onVincular={vincular} onDesvincular={desvincular} onCancelar={cancelarRodada} />
      {:else if estado.ultimo_campeao}
        <section class="cartao" aria-labelledby="titulo-campeao">
          <h2 id="titulo-campeao">Campeões da rodada {estado.ultimo_campeao.rodada}</h2>
          <p role="status"><strong>Time {estado.ultimo_campeao.time}</strong> — {estado.ultimo_campeao.jogadores.join(' e ')}</p>
          <p class="ajuda">A rodada terminou. Já dá para sortear a próxima.</p>
          {#if estado.pode_desfazer}
            <button class="secundario" type="button" onclick={desfazerPartida} disabled={ocupado}>Desfazer a última partida (reabre a rodada)</button>
          {/if}
          {#if erroQuadra}<p class="alerta" role="alert">{erroQuadra}</p>{/if}
        </section>
      {/if}

      <section aria-labelledby="titulo-presentes">
        <h2 id="titulo-presentes">Presentes ({presentes.length})</h2>
        {#if travada}
          <p class="ajuda" role="status">Presença travada: há uma rodada {rodada.estado === 'proposta' ? 'em proposta' : 'em andamento'}. Para marcar, desmarcar ou reordenar, {rodada.estado === 'proposta' ? 'descarte a proposta' : 'cancele a rodada'} no painel acima.</p>
        {/if}
        {#if !presentes.length}
          <p class="vazio">Ninguém marcado ainda. Marque abaixo, na ordem em que chegam.</p>
        {:else}
          <ol class="lista" bind:this={listaEl}>
            {#each listaExibida as j, i (j.id)}
              <li class:arrastando={arrasto?.id === j.id}>
                <button
                  class="alca"
                  type="button"
                  aria-label="Arrastar {j.nome} para mudar a ordem de chegada"
                  disabled={ocupado || travada}
                  onpointerdown={e => iniciarArrasto(e, j)}
                  onpointermove={moverArrasto}
                  onpointerup={soltarArrasto}
                  onpointercancel={() => { arrasto = null; }}
                >⠿</button>
                <span class="ordem" aria-label="Chegada nº {j.ordem}">{j.ordem}º</span>
                <Avatar {segredo} jogador={j} />
                <span class="nome">{j.nome}</span>
                <span class="genero">{j.genero === 'H' ? 'Homem' : 'Mulher'} · nota {j.nota}</span>
                <span class="botoes">
                  <button class="secundario" type="button" onclick={() => mover(j, -1)} disabled={ocupado || travada || i === 0} aria-label="Subir {j.nome}">↑</button>
                  <button class="secundario" type="button" onclick={() => mover(j, 1)} disabled={ocupado || travada || i === presentes.length - 1} aria-label="Descer {j.nome}">↓</button>
                  <button class="secundario" type="button" onclick={() => desmarcar(j)} disabled={ocupado || travada} aria-label="Desmarcar {j.nome}">Desmarcar</button>
                  {#if rodada?.estado === 'em_andamento'}
                    {@const ef = efeitoDaRetirada(j.id, estado.conducao)}
                    <button class="secundario" type="button" onclick={() => (retirandoId = j.id)} disabled={ocupado || ef.emJogo} aria-label="Retirar {j.nome} da rodada">Retirar da rodada</button>
                  {/if}
                </span>
                {#if rodada?.estado === 'em_andamento'}
                  {@const ef = efeitoDaRetirada(j.id, estado.conducao)}
                  {#if ef.emJogo}
                    <p class="ajuda motivo">Em jogo na partida chamada: encerre ou anule a partida para retirar.</p>
                  {:else if retirandoId === j.id}
                    <div class="confirma">
                      <p class="ajuda" role="alert">
                        Retirar {j.nome} da rodada? Ele fica ausente nas próximas rodadas{ef.efeitos.length ? `; ${ef.efeitos.join('; ')}` : ''}. Os resultados já registrados não mudam.
                      </p>
                      <div class="botoes">
                        <button class="perigo" type="button" onclick={() => retirar(j)} disabled={ocupado}>Sim, retirar</button>
                        <button class="secundario" type="button" onclick={() => (retirandoId = null)}>Voltar</button>
                      </div>
                    </div>
                  {/if}
                {/if}
              </li>
            {/each}
          </ol>
        {/if}
      </section>

      {#if !rodada}
        <section class="cartao" aria-labelledby="titulo-sorteio">
          <h2 id="titulo-sorteio">Sortear a rodada</h2>
          <fieldset>
            <legend>Pontos da partida: <strong>{alvo} pts</strong></legend>
            <input class="slider-alvo" type="range" min="6" max="25" step="1" aria-label="Pontos da partida" bind:value={alvo} disabled={ocupado} />
          </fieldset>
          <fieldset>
            <legend>Formato dos times</legend>
            <label class="opcao"><input type="radio" name="formato" value="dupla" bind:group={formato} disabled={ocupado} /> Duplas</label>
            <label class="opcao"><input type="radio" name="formato" value="trio" bind:group={formato} disabled={ocupado} /> Trios</label>
          </fieldset>
          <button class="acao-principal" type="button" onclick={sortear} disabled={ocupado || faltam > 0}>{formato === 'trio' ? 'Sortear trios' : 'Sortear duplas'}</button>
          {#if faltam > 0}<p class="ajuda" role="status">{mensagemFaltam(faltam)}</p>{/if}
        </section>
      {/if}

      <section aria-labelledby="titulo-ausentes">
        <h2 id="titulo-ausentes">Ausentes ({ausentes.length})</h2>
        {#if travada && !podeAtrasado && ausentes.length}
          <p class="ajuda">Presença travada pela rodada: o motivo está no aviso de Presentes.</p>
        {/if}
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
      {#if !travada}
      <section class="cartao" aria-labelledby="titulo-gerenciar">
        <h2 id="titulo-gerenciar">Jogadores</h2>
        <p class="ajuda">Cadastre, edite ou inative jogadores na tela de Jogadores e volte aqui para marcar quem chegou.</p>
        <button class="acao-principal" type="button" onclick={onGerenciarJogadores} disabled={ocupado}>Gerenciar jogadores</button>
      </section>
      {/if}

      {#if !velho}
        <section class="encerrar" aria-label="Encerrar joguinho">
          {@render encerrarJoguinho()}
        </section>
      {/if}
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
  /* Ação crítica de fundo cheio. Usa o tom "ativo" do destrutivo: o branco sobre ele passa de 4,5:1 e sobre o tom base não. */
  .critico { display: flex; align-items: center; justify-content: center; min-height: 52px; padding: 0 1.1rem; border: 0; border-radius: 10px; background: var(--acao-destrutiva-ativa); color: var(--acao-destrutiva-texto); font: inherit; font-weight: 800; cursor: pointer; }
  .critico:disabled, .acao-principal:disabled { opacity: .45; cursor: not-allowed; }
  .cartao { display: flex; flex-direction: column; gap: .6rem; padding: 1rem; border: 1px solid var(--borda-sutil); border-radius: var(--raio-padrao); background: var(--fundo-superficie); }
  .cartao h2 { margin: 0; }
  .ajuda { margin: 0; color: var(--texto-suave); font-size: var(--texto-apoio); }
  label, legend { font-size: var(--texto-apoio); color: var(--texto-medio); }
  input:focus-visible { border-color: var(--foco-cor); box-shadow: var(--foco-anel); }
  fieldset { display: flex; flex-wrap: wrap; gap: 1.2rem; margin: 0; padding: 0; border: 0; }
  .slider-alvo { flex: 1 1 100%; min-height: 44px; }
  legend { padding: 0; margin-bottom: .3rem; }
  .opcao { display: inline-flex; align-items: center; gap: .5rem; min-height: 44px; }
  .opcao input { width: 1.2rem; height: 1.2rem; }
  .acao-principal { display: flex; align-items: center; justify-content: center; min-height: 52px; padding: 0 1.1rem; border: 0; border-radius: 10px; background: var(--acao-primaria); color: var(--acao-primaria-texto); font: inherit; font-weight: 800; cursor: pointer; }
  .acao-principal:disabled { opacity: .45; cursor: not-allowed; }
  .alerta { display: flex; align-items: flex-start; gap: .6rem; padding: .75rem; border: 1px solid color-mix(in srgb, var(--estado-erro) 45%, transparent); border-radius: 10px; background: color-mix(in srgb, var(--estado-erro) 12%, transparent); color: var(--estado-erro-suave); font-size: .83rem; line-height: 1.4; }
  .lista { display: flex; flex-direction: column; gap: .5rem; margin: 0; padding: 0; list-style: none; }
  li { display: flex; flex-wrap: wrap; align-items: center; gap: .5rem; padding: .6rem .75rem; border: 1px solid var(--borda-sutil); border-radius: var(--raio-padrao); background: var(--fundo-cartao); }
  .alca { touch-action: none; cursor: grab; min-width: 44px; min-height: 44px; border: 0; border-radius: 10px; background: transparent; color: var(--texto-suave); font-size: 1.4rem; line-height: 1; }
  .alca:disabled { opacity: .4; cursor: not-allowed; }
  .arrastando { background: var(--fundo-elevado, var(--fundo-base)); box-shadow: var(--foco-anel); }
  .ordem { min-width: 2.2rem; font-family: var(--fonte-numeros); font-size: var(--texto-destaque); font-weight: 700; color: var(--texto-forte); }
  .nome { flex: 1 1 8rem; font-weight: 700; }
  .genero { color: var(--texto-suave); font-size: var(--texto-legenda); }
  .botoes { display: flex; gap: .4rem; flex-wrap: wrap; }
  .vazio { margin: 0; color: var(--texto-suave); }
  .motivo, .confirma { flex-basis: 100%; }
  .cartao.velho { border-color: var(--borda-ativa); }
  .encerrar { padding-top: .5rem; border-top: 1px solid var(--borda-sutil); display: flex; flex-direction: column; gap: .6rem; }
</style>
