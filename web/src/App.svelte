<script>
  import { onMount } from 'svelte';
  import HomePlacar from './components/HomePlacar.svelte';
  import ModalEntrar from './components/ModalEntrar.svelte';
  import SalaQuadra from './components/SalaQuadra.svelte';

  // Svelte 5 Runes de Estado
  let quadraAtual = $state(null);
  let eu = $state(null);
  let participantes = $state([]);
  let estadoPartida = $state(null);
  let linhaDoTempo = $state([]);
  let submetendo = $state(false);
  let erro = $state(null);

  let modalEntrarAberto = $state(false);
  let quadraSelecionadaParaEntrar = $state(null);

  let wsConectado = $state(false);
  let wsSocket = null;
  let wsReconnectTimer = null;

  async function tentarRestaurarSessao(quadraId) {
    try {
      const resEu = await fetch(`/api/quadras/${quadraId}/eu`);
      if (resEu.ok) {
        const data = await resEu.json();
        if (data.participante && data.quadra) {
          eu = data.participante;
          quadraAtual = data.quadra;
          conectarWebSocket(quadraId);
          return true;
        }
      }
    } catch (err) {
      console.error('Erro ao restaurar sessão:', err);
    }
    return false;
  }

  function conectarWebSocket(quadraId) {
    if (wsSocket) {
      wsSocket.close();
    }
    if (wsReconnectTimer) {
      clearTimeout(wsReconnectTimer);
    }

    const protocolo = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocolo}//${host}/ws/${quadraId}`;

    wsSocket = new WebSocket(wsUrl);

    wsSocket.onopen = () => {
      wsConectado = true;
    };

    wsSocket.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.tipo === 'ESTADO_INICIAL') {
          participantes = msg.payload.participantes || [];
          if (msg.payload.estado_partida) {
            estadoPartida = msg.payload.estado_partida;
          }
          if (msg.payload.linha_do_tempo) {
            linhaDoTempo = msg.payload.linha_do_tempo;
          }
        } else if (msg.tipo === 'PRESENCA_ATUALIZADA') {
          participantes = msg.payload.participantes || [];
        } else if (msg.tipo === 'PLACAR_ATUALIZADO') {
          if (msg.payload.estado_partida) {
            estadoPartida = msg.payload.estado_partida;
          }
          if (msg.payload.linha_do_tempo) {
            linhaDoTempo = msg.payload.linha_do_tempo;
          }
        }
      } catch (e) {
        console.error('Erro ao processar mensagem WS:', e);
      }
    };

    wsSocket.onclose = () => {
      wsConectado = false;
      if (quadraAtual && quadraAtual.id === quadraId) {
        wsReconnectTimer = setTimeout(() => {
          conectarWebSocket(quadraId);
        }, 2500);
      }
    };

    wsSocket.onerror = (err) => {
      console.error('Erro no WebSocket:', err);
      wsSocket?.close();
    };
  }

  // --- AÇÕES DO HOME ---

  async function handleCriarQuadraHome({ apelido, nome }) {
    try {
      submetendo = true;
      erro = null;
      const res = await fetch('/api/quadras', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ apelido, nome }),
      });

      if (res.ok) {
        const data = await res.json();
        eu = data.participante;
        quadraAtual = data;
        window.history.pushState({}, '', `/quadra/${data.id}`);
        conectarWebSocket(data.id);
      } else {
        const errData = await res.json().catch(() => ({}));
        erro = errData.detail || 'Não foi possível criar o placar.';
      }
    } catch (e) {
      console.error('Erro ao criar quadra:', e);
      erro = 'Erro de conexão ao criar a quadra. Verifique sua rede.';
    } finally {
      submetendo = false;
    }
  }

  async function handleEntrarQuadraHome({ quadraId, apelido }) {
    try {
      submetendo = true;
      erro = null;
      const res = await fetch(`/api/quadras/${quadraId}/entrar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ apelido }),
      });

      if (res.ok) {
        const data = await res.json();
        eu = data.participante;
        quadraAtual = data.quadra;
        window.history.pushState({}, '', `/quadra/${quadraId}`);
        conectarWebSocket(quadraId);
      } else {
        const errData = await res.json().catch(() => ({}));
        erro = errData.detail || 'Código de quadra inválido ou sala já expirou por inatividade.';
      }
    } catch (e) {
      console.error('Erro ao entrar na quadra:', e);
      erro = 'Erro de conexão ao entrar na quadra. Verifique sua rede.';
    } finally {
      submetendo = false;
    }
  }

  async function handleEntrarQuadraModal(apelido) {
    if (!quadraSelecionadaParaEntrar) return;
    const quadraId = quadraSelecionadaParaEntrar.id;
    await handleEntrarQuadraHome({ quadraId, apelido });
    if (quadraAtual) {
      modalEntrarAberto = false;
      quadraSelecionadaParaEntrar = null;
    }
  }

  async function handleMarcarPonto(equipe) {
    if (!quadraAtual) return;
    try {
      const res = await fetch(`/api/quadras/${quadraAtual.id}/pontos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ equipe }),
      });
      if (res.ok) {
        const data = await res.json();
        if (data.estado_partida) {
          estadoPartida = data.estado_partida;
        }
        if (data.linha_do_tempo) {
          linhaDoTempo = data.linha_do_tempo;
        }
      } else {
        const err = await res.json().catch(() => ({}));
        console.warn('Erro ao marcar ponto:', err.detail);
      }
    } catch (e) {
      console.error('Erro de rede ao marcar ponto:', e);
    }
  }

  async function handleDesfazerPonto() {
    if (!quadraAtual) return;
    try {
      const res = await fetch(`/api/quadras/${quadraAtual.id}/desfazer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      if (res.ok) {
        const data = await res.json();
        if (data.estado_partida) {
          estadoPartida = data.estado_partida;
        }
        if (data.linha_do_tempo) {
          linhaDoTempo = data.linha_do_tempo;
        }
      } else {
        const err = await res.json().catch(() => ({}));
        console.warn('Erro ao desfazer ponto:', err.detail);
      }
    } catch (e) {
      console.error('Erro de rede ao desfazer ponto:', e);
    }
  }

  function handleVoltarParaHome() {
    if (wsSocket) {
      wsSocket.close();
      wsSocket = null;
    }
    if (wsReconnectTimer) {
      clearTimeout(wsReconnectTimer);
    }
    quadraAtual = null;
    eu = null;
    participantes = [];
    estadoPartida = null;
    linhaDoTempo = [];
    erro = null;
    window.history.pushState({}, '', '/');
  }

  onMount(async () => {
    // 1. Rota direta de quadra: /quadra/:id
    const quadraMatch = window.location.pathname.match(/\/quadra\/([a-zA-Z0-9_-]+)/);
    if (quadraMatch && quadraMatch[1]) {
      const quadraId = quadraMatch[1];
      const restaurou = await tentarRestaurarSessao(quadraId);
      if (!restaurou) {
        try {
          const res = await fetch(`/api/quadras/${quadraId}`);
          if (res.ok) {
            quadraSelecionadaParaEntrar = await res.json();
            modalEntrarAberto = true;
          } else {
            window.history.replaceState({}, '', '/');
            erro = 'Quadra não encontrada ou já expirou por inatividade.';
          }
        } catch {
          window.history.replaceState({}, '', '/');
        }
      }
    }

    window.addEventListener('popstate', async () => {
      const qMatch = window.location.pathname.match(/\/quadra\/([a-zA-Z0-9_-]+)/);
      if (qMatch && qMatch[1]) {
        await tentarRestaurarSessao(qMatch[1]);
        return;
      }
      handleVoltarParaHome();
    });
  });
</script>

<main>
  {#if quadraAtual}
    <!-- Sala da Quadra com Placar e Presença ao Vivo -->
    <SalaQuadra
      quadra={quadraAtual}
      {eu}
      {participantes}
      {estadoPartida}
      {linhaDoTempo}
      {wsConectado}
      onMarcarPonto={handleMarcarPonto}
      onDesfazerPonto={handleDesfazerPonto}
      onVoltar={handleVoltarParaHome}
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
