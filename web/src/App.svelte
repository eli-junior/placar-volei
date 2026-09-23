<script>
  import { onMount } from 'svelte';
  import HomePlacar from './components/HomePlacar.svelte';
  import ModalEntrar from './components/ModalEntrar.svelte';
  import SalaQuadra from './components/SalaQuadra.svelte';
  import { aceitarSnapshot, mensagemDeErro } from './sync.js';

  let quadraAtual = $state(null);
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
  let wsSocket = null;
  let wsReconnectTimer = null;
  let wsTentativasReconexao = 0;

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
    clearTimeout(wsReconnectTimer);
    wsTentativasReconexao = 0;
    const anterior = wsSocket;
    wsSocket = null;
    wsConectado = false;
    anterior?.close();
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

  function salaExpirada() {
    handleVoltarParaHome(false);
    window.history.replaceState({}, '', '/');
    erro = 'Esta sala expirou ou foi encerrada pelo servidor. Crie um novo placar ou entre em outra sala.';
  }

  function conectarWebSocket(quadraId) {
    desconectar();
    const protocolo = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const socket = new WebSocket(`${protocolo}//${window.location.host}/ws/${quadraId}`);
    wsSocket = socket;
    socket.onmessage = event => {
      if (wsSocket !== socket) return;
      try {
        const msg = JSON.parse(event.data);
        if (msg.tipo === 'SALA_EXPIRADA') return salaExpirada();
        if (msg.tipo === 'ESTADO_INICIAL') {
          if (!msg.payload.quadra || msg.payload.quadra.id !== quadraAtual?.id) return salaExpirada();
          aplicarSnapshot(msg.payload);
          wsConectado = true;
          wsTentativasReconexao = 0;
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
    };
    socket.onclose = event => {
      if (wsSocket !== socket) return;
      wsConectado = false;
      if (event.code === 4404) return salaExpirada();
      if (event.code === 4401) {
        handleVoltarParaHome(false);
        window.history.replaceState({}, '', '/');
        erro = 'Sua sessão não é mais válida. Entre novamente com seu apelido.';
        return;
      }
      if (quadraAtual?.id === quadraId) {
        // Backoff exponencial com jitter (CV2.DS2.TS1)
        const base = Math.min(1000 * Math.pow(1.5, wsTentativasReconexao), 15000);
        const jitter = Math.random() * 800;
        const delay = Math.round(base + jitter);
        wsTentativasReconexao += 1;
        wsReconnectTimer = setTimeout(() => conectarWebSocket(quadraId), delay);
      }
    };
    socket.onerror = () => socket.close();
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
    conectarWebSocket(quadra.id);
  }

  async function handleCriarQuadraHome(dados) {
    submetendo = true;
    erro = null;
    try {
      const res = await fetch('/api/quadras', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(mensagemDeErro(data, 'Não foi possível criar o placar.'));
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
      const data = await res.json();
      if (!res.ok) throw new Error(mensagemDeErro(data, 'Não foi possível entrar na sala.'));
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
        const data = await res.json();
        if (!res.ok) throw new Error(mensagemDeErro(data, 'Não foi possível realizar a ação.'));
        aplicarSnapshot(data);
      } catch (e) {
        if (quadraAtual?.id === sala.id) erro = e.message || 'Falha de conexão. Confira o placar antes de tentar novamente.';
      }
    });
  }

  const handleMarcarPonto = equipe => executar('pontos', { equipe });
  const handleDesfazerPonto = () => executar('desfazer');
  const handleIniciarNovaPartida = dados => executar('reiniciar', dados);
  const handleConfigurarPartida = dados => executar('configurar', dados);
  const handleAssumirControle = () => executar('controle/assumir');
  const handleAutorizarAdmin = id => executar(`participantes/${id}/admin`);
  const handlePromoverControlador = id => executar(`participantes/${id}/promover`);
  const handleRevogarControlador = id => executar(`participantes/${id}/revogar`);
  const handlePassarControle = id => executar(`participantes/${id}/controle`);

  async function carregarRota() {
    handleVoltarParaHome(false);
    const match = window.location.pathname.match(/^\/quadra\/([a-zA-Z0-9_-]+)$/);
    if (!match) return;
    const quadraId = match[1];
    try {
      const res = await fetch(`/api/quadras/${quadraId}/eu`);
      const data = await res.json();
      if (window.location.pathname !== `/quadra/${quadraId}`) return;
      if (data.participante && data.quadra) return abrirSala(data.quadra, data.participante);
      const sala = await fetch(`/api/quadras/${quadraId}`);
      if (window.location.pathname !== `/quadra/${quadraId}`) return;
      if (!sala.ok) return salaExpirada();
      quadraSelecionadaParaEntrar = await sala.json();
      modalEntrarAberto = true;
    } catch { erro = 'Não foi possível carregar a sala. Confira sua conexão e tente novamente.'; }
  }

  onMount(() => {
    carregarRota();
    window.addEventListener('popstate', carregarRota);
    return () => {
      window.removeEventListener('popstate', carregarRota);
      desconectar();
    };
  });
</script>

<main>
  {#if quadraAtual}
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
      onConfigurarPartida={handleConfigurarPartida}
      onVoltar={() => handleVoltarParaHome()}
      onAssumirControle={handleAssumirControle}
      onPromoverControlador={handlePromoverControlador}
      onRevogarControlador={handleRevogarControlador}
      onAutorizarAdmin={handleAutorizarAdmin}
      onPassarControle={handlePassarControle}
      {operando}
      {pendentes}
      {erro}
    />
  {:else}
    <!-- Tela Inicial: Criar Placar ou Acompanhar com Código de 5 Dígitos -->
    <HomePlacar
      onCriarQuadra={handleCriarQuadraHome}
      onEntrarQuadra={handleEntrarQuadraHome}
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
