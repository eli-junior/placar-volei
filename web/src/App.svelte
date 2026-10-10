<script>
  import { onMount } from 'svelte';
  import HomePlacar from './components/HomePlacar.svelte';
  import ModalEntrar from './components/ModalEntrar.svelte';
  import Jogadores from './components/Jogadores.svelte';
  import Sessao from './components/Sessao.svelte';
  import PaginaNaoEncontrada from './components/PaginaNaoEncontrada.svelte';
  import { resolverRota } from './lib/rotas.js';
  import SalaQuadra from './components/SalaQuadra.svelte';
  import { noAplicativoAndroid } from './lib/casca.js';
  import { aceitarSnapshot, lerJson, mensagemDeErro } from './sync.js';
  import { criarConexao } from './lib/conexao.js';

  let quadraAtual = $state(null);
  // Base de jogadores (CV8): só no navegador, nunca dentro do APK.
  let telaJogadores = $state(false);
  let telaSessao = $state(false);
  // Caminho que não existe: mostra a página de aviso (CV8.DS7.US18).
  let caminhoInexistente = $state(null);
  let eu = $state(null);
  let participantes = $state([]);
  let estadoPartida = $state(null);
  let linhaDoTempo = $state([]);
  let ultimoSnapshot = null;
  let submetendo = $state(false);
  let operando = $state(false);
  // Toques que já foram aceitos e ainda não voltaram do servidor. A fila existe
  // para que nenhum toque rápido consecutivo seja descartado em silêncio.
  let pendentes = $state(0);
  let filaComandos = Promise.resolve();
  let erro = $state(null);
  let modalEntrarAberto = $state(false);
  let quadraSelecionadaParaEntrar = $state(null);
  let wsConectado = $state(false);
  const conexao = criarConexao({
    criarSocket: quadraId => {
      const protocolo = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      return new WebSocket(`${protocolo}//${window.location.host}/ws/${quadraId}`);
    },
    aoMensagem: tratarMensagem,
    aoCair: () => { wsConectado = false; },
    aoFechar: codigo => {
      if (codigo === 4404) { salaExpirada(); return false; }
      if (codigo === 4401) {
        handleVoltarParaHome(false);
        window.history.replaceState({}, '', '/');
        erro = 'Sua sessão não é mais válida. Entre novamente com seu apelido.';
        return false;
      }
      return true;
    },
  });

  function aplicarSnapshot(data) {
    if (!aceitarSnapshot(ultimoSnapshot, data, quadraAtual?.partida_id)) return;
    ultimoSnapshot = data;
    quadraAtual = { ...quadraAtual, ...data.quadra };
    estadoPartida = data.estado_partida;
    linhaDoTempo = data.linha_do_tempo;
    participantes = data.participantes;
    eu = participantes.find(p => p.id === eu?.id) || eu;
  }

  function desconectar() {
    conexao.desconectar();
    wsConectado = false;
  }

  function handleVoltarParaHome(navegar = true) {
    desconectar();
    quadraAtual = null;
    eu = null;
    participantes = [];
    estadoPartida = null;
    linhaDoTempo = [];
    ultimoSnapshot = null;
    erro = null;
    modalEntrarAberto = false;
    quadraSelecionadaParaEntrar = null;
    if (navegar) window.history.pushState({}, '', '/');
  }

  // Sala que este aparelho pediu para liberar: o aviso do socket pode chegar antes da resposta.
  let liberandoSalaId = null;

  function salaExpirada(motivo) {
    if (motivo === 'liberada' && liberandoSalaId && liberandoSalaId === quadraAtual?.id) motivo = 'liberada-por-mim';
    handleVoltarParaHome(false);
    window.history.replaceState({}, '', '/');
    erro = motivo === 'liberada-por-mim'
      ? 'Quadra liberada. Crie um novo placar quando quiser.'
      : motivo === 'liberada'
      ? 'A quadra foi liberada pelo administrador. Crie um novo placar ou entre em outra sala.'
      : 'Esta sala expirou ou foi encerrada pelo servidor. Crie um novo placar ou entre em outra sala.';
  }

  // Volta do segundo plano ou da rede: reconecta já, sem esperar o backoff.
  function retomarConexao() {
    if (document.visibilityState === 'hidden') return;
    conexao.retomar();
  }

  function tratarMensagem(msg) {
    try {
      if (msg.tipo === 'SALA_EXPIRADA') return salaExpirada(msg.payload?.motivo);
      if (msg.tipo === 'ESTADO_INICIAL') {
        if (!msg.payload.quadra || msg.payload.quadra.id !== quadraAtual?.id) return salaExpirada();
        // Estado inicial é a verdade da conexão nova: substitui o anterior
        // mesmo que o seq tenha voltado (servidor reiniciado).
        ultimoSnapshot = null;
        aplicarSnapshot(msg.payload);
        wsConectado = true;
        conexao.confirmar();
      } else if (msg.tipo === 'PLACAR_ATUALIZADO') {
        aplicarSnapshot(msg.payload);
      } else if (msg.tipo === 'PRESENCA_ATUALIZADA') {
        // Presença não pode reverter uma promoção já recebida pelo log.
        participantes = (msg.payload.participantes || []).map(p => {
          const atual = participantes.find(a => a.id === p.id);
          return atual ? { ...p, papel: atual.papel } : p;
        });
      }
    } catch (e) {
      console.error('Erro ao processar atualização:', e);
    }
  }

  function abrirSala(quadra, participante) {
    desconectar();
    ultimoSnapshot = null;
    estadoPartida = null;
    linhaDoTempo = [];
    participantes = [];
    quadraAtual = quadra;
    eu = participante;
    erro = null;
    conexao.conectar(quadra.id);
  }

  async function handleCriarQuadraHome(dados) {
    submetendo = true;
    erro = null;
    try {
      const res = await fetch('/api/quadras', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados),
      });
      const data = await lerJson(res);
      if (!res.ok || !data) throw new Error(mensagemDeErro(data, 'Não foi possível criar o placar.'));
      abrirSala(data, data.participante);
      window.history.pushState({}, '', `/quadra/${data.id}`);
    } catch (e) { erro = e.message || 'Erro de conexão ao criar o placar.'; }
    finally { submetendo = false; }
  }

  async function handleEntrarQuadraHome({ quadraId, apelido }) {
    submetendo = true;
    erro = null;
    try {
      const res = await fetch(`/api/quadras/${quadraId}/entrar`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ apelido }),
      });
      const data = await lerJson(res);
      if (!res.ok || !data) throw new Error(mensagemDeErro(data, 'Não foi possível entrar na sala.'));
      abrirSala(data.quadra, data.participante);
      modalEntrarAberto = false;
      quadraSelecionadaParaEntrar = null;
      window.history.pushState({}, '', `/quadra/${quadraId}`);
    } catch (e) { erro = e.message || 'Erro de conexão ao entrar na sala.'; }
    finally { submetendo = false; }
  }

  async function handleEntrarQuadraModal(apelido) {
    if (quadraSelecionadaParaEntrar) await handleEntrarQuadraHome({ quadraId: quadraSelecionadaParaEntrar.id, apelido });
  }

  // Serializa os comandos: cada toque entra no fim da fila e é enviado quando o
  // anterior responde. Serializar (e não ignorar) é o que garante que o 5º toque
  // em 2 segundos vire o 5º ponto, e não um clique perdido.
  function enfileirarComando(tarefa) {
    pendentes += 1;
    operando = true;
    filaComandos = filaComandos
      .catch(() => {})
      .then(tarefa)
      .finally(() => {
        pendentes = Math.max(0, pendentes - 1);
        if (pendentes === 0) operando = false;
      });
    return filaComandos;
  }

  function executar(rota, body) {
    if (!quadraAtual) return Promise.resolve();
    if (!wsConectado) {
      // Com o socket caído os botões já estão desabilitados; se o toque vier
      // mesmo assim (teclado, leitor de tela), o motivo aparece escrito.
      erro = 'Sem conexão com a sala. Aguarde a reconexão para operar o placar.';
      return Promise.resolve();
    }
    const sala = quadraAtual;
    return enfileirarComando(async () => {
      if (quadraAtual?.id !== sala.id) return;
      erro = null;
      // A versão de controle é lida na hora do envio, não na hora do toque:
      // o comando anterior da fila pode tê-la mudado.
      const versao = String(quadraAtual.controle_versao);
      try {
        const res = await fetch(`/api/quadras/${sala.id}/${rota}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'x-control-version': versao },
          body: body ? JSON.stringify(body) : undefined,
        });
        if (quadraAtual?.id !== sala.id) return;
        if (res.status === 404 && !rota.startsWith('participantes/')) return salaExpirada();
        const data = await lerJson(res);
        if (!res.ok || !data) throw new Error(mensagemDeErro(data, 'Não foi possível realizar a ação.'));
        aplicarSnapshot(data);
      } catch (e) {
        if (quadraAtual?.id === sala.id) erro = e.message || 'Falha de conexão. Confira o placar antes de tentar novamente.';
      }
    });
  }

  const handleMarcarPonto = equipe => executar('pontos', { equipe });
  const handleDesfazerPonto = () => executar('desfazer');
  const handleIniciarNovaPartida = dados => executar('reiniciar', dados);
  const handleProximoJogo = () => executar('proximo-jogo');
  const handleConfigurarPartida = dados => executar('configurar', dados);
  const handleAssumirControle = () => executar('controle/assumir');
  const handleAutorizarAdmin = id => executar(`participantes/${id}/admin`);
  const handlePromoverControlador = id => executar(`participantes/${id}/promover`);
  const handleRevogarControlador = id => executar(`participantes/${id}/revogar`);
  const handlePassarControle = id => executar(`participantes/${id}/controle`);

  // Liberar a quadra (CV6.DS1.US8): fora da fila de comandos, porque apaga a sala
  // e não devolve snapshot. Quem liberou sai já; os outros saem pelo aviso do socket.
  async function handleLiberarQuadra() {
    const sala = quadraAtual;
    if (!sala) return;
    erro = null;
    liberandoSalaId = sala.id;
    try {
      const res = await fetch(`/api/quadras/${sala.id}/liberar`, { method: 'POST' });
      if (res.ok || res.status === 404) {
        if (quadraAtual?.id === sala.id) salaExpirada('liberada-por-mim');
        return;
      }
      throw new Error(mensagemDeErro(await lerJson(res), 'Não foi possível liberar a quadra.'));
    } catch (e) {
      if (quadraAtual?.id === sala.id) erro = e.message || 'Falha de conexão. Tente liberar de novo.';
    } finally {
      liberandoSalaId = null;
    }
  }

  async function carregarRota() {
    handleVoltarParaHome(false);
    const rota = resolverRota(window.location.pathname, { apk: noAplicativoAndroid() });
    if (rota.canonico) {
      const { search, hash } = window.location;
      window.history.replaceState({}, '', rota.canonico + search + hash);
    }
    telaJogadores = rota.tela === 'jogadores';
    telaSessao = rota.tela === 'joguinho';
    caminhoInexistente = rota.tela === 'nao_encontrada' ? window.location.pathname : null;
    if (rota.tela !== 'quadra') return;
    const quadraId = rota.quadraId;
    // O usuário pode navegar enquanto a sala carrega (a barra final conta como a mesma sala).
    const aindaNaSala = () => resolverRota(window.location.pathname).quadraId === quadraId;
    try {
      const res = await fetch(`/api/quadras/${quadraId}/eu`);
      const data = (await lerJson(res)) || {};
      if (!aindaNaSala()) return;
      if (data.participante && data.quadra) return abrirSala(data.quadra, data.participante);
      const sala = await fetch(`/api/quadras/${quadraId}`);
      if (!aindaNaSala()) return;
      if (!sala.ok) return salaExpirada();
      quadraSelecionadaParaEntrar = await sala.json();
      modalEntrarAberto = true;
    } catch { erro = 'Não foi possível carregar a sala. Confira sua conexão e tente novamente.'; }
  }

  onMount(() => {
    carregarRota();
    window.addEventListener('popstate', carregarRota);
    document.addEventListener('visibilitychange', retomarConexao);
    window.addEventListener('online', retomarConexao);
    return () => {
      window.removeEventListener('popstate', carregarRota);
      document.removeEventListener('visibilitychange', retomarConexao);
      window.removeEventListener('online', retomarConexao);
      desconectar();
    };
  });
</script>

<main>
  {#if telaSessao}
    <Sessao
      onVoltar={() => { window.history.pushState({}, '', '/'); carregarRota(); }}
      onGerenciarJogadores={() => { window.history.pushState({}, '', '/jogadores'); carregarRota(); }}
    />
  {:else if telaJogadores}
    <Jogadores onVoltar={() => { window.history.pushState({}, '', '/'); carregarRota(); }} />
  {:else if caminhoInexistente}
    <PaginaNaoEncontrada caminho={caminhoInexistente} />
  {:else if quadraAtual}
    <!-- Sala da Quadra em Tempo Real -->
    <SalaQuadra
      quadra={quadraAtual}
      {eu}
      {participantes}
      {estadoPartida}
      {linhaDoTempo}
      {wsConectado}
      onMarcarPonto={handleMarcarPonto}
      onDesfazerPonto={handleDesfazerPonto}
      onIniciarNovaPartida={handleIniciarNovaPartida}
      onProximoJogo={handleProximoJogo}
      onConfigurarPartida={handleConfigurarPartida}
      onVoltar={() => handleVoltarParaHome()}
      onAssumirControle={handleAssumirControle}
      onPromoverControlador={handlePromoverControlador}
      onRevogarControlador={handleRevogarControlador}
      onAutorizarAdmin={handleAutorizarAdmin}
      onPassarControle={handlePassarControle}
      onLiberarQuadra={handleLiberarQuadra}
      {operando}
      {pendentes}
      {erro}
    />
  {:else}
    <!-- Tela Inicial: Criar Placar ou Acompanhar com Código de 5 Dígitos -->
    <HomePlacar
      onCriarQuadra={handleCriarQuadraHome}
      onEntrarQuadra={handleEntrarQuadraHome}
      onAbrirJogadores={noAplicativoAndroid() ? null : () => { window.history.pushState({}, '', '/jogadores'); carregarRota(); }}
      onAbrirSessao={noAplicativoAndroid() ? null : () => { window.history.pushState({}, '', '/joguinho'); carregarRota(); }}
      {submetendo}
      {erro}
    />
  {/if}

  {#if modalEntrarAberto}
    <ModalEntrar
      quadra={quadraSelecionadaParaEntrar}
      onEntrar={handleEntrarQuadraModal}
      onVoltar={() => {
        modalEntrarAberto = false;
        quadraSelecionadaParaEntrar = null;
        if (!quadraAtual) {
          window.history.pushState({}, '', '/');
        }
      }}
      {submetendo}
    />
  {/if}
</main>

<style>
  main {
    flex: 1;
    display: flex;
    flex-direction: column;
  }
</style>
