<script>
  import { onMount } from 'svelte';
  import ListaArenas from './components/ListaArenas.svelte';
  import ListaQuadras from './components/ListaQuadras.svelte';
  import ModalCriarArena from './components/ModalCriarArena.svelte';
  import ModalCriarQuadra from './components/ModalCriarQuadra.svelte';
  import ModalEntrar from './components/ModalEntrar.svelte';
  import SalaQuadra from './components/SalaQuadra.svelte';

  // Svelte 5 Runes de Estado
  let arenas = $state([]);
  let arenaAtual = $state(null);
  let quadras = $state([]);
  let quadraAtual = $state(null);
  let eu = $state(null);
  let participantes = $state([]);
  let estadoPartida = $state(null);
  let loading = $state(true);
  let submetendo = $state(false);

  let modalCriarArenaAberto = $state(false);
  let modalCriarQuadraAberto = $state(false);
  let modalEntrarAberto = $state(false);
  let quadraSelecionadaParaEntrar = $state(null);

  let wsConectado = $state(false);
  let wsSocket = null;
  let wsReconnectTimer = null;

  async function fetchArenas() {
    try {
      loading = true;
      const res = await fetch('/api/arenas');
      if (res.ok) {
        const data = await res.json();
        arenas = data.arenas || [];
      }
    } catch (err) {
      console.error('Erro ao buscar arenas:', err);
    } finally {
      loading = false;
    }
  }

  async function fetchQuadrasDaArena(arenaId) {
    try {
      loading = true;
      const res = await fetch(`/api/arenas/${arenaId}/quadras`);
      if (res.ok) {
        const data = await res.json();
        arenaAtual = data.arena;
        quadras = data.quadras || [];
      }
    } catch (err) {
      console.error('Erro ao buscar quadras da arena:', err);
    } finally {
      loading = false;
    }
  }

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
        } else if (msg.tipo === 'PRESENCA_ATUALIZADA') {
          participantes = msg.payload.participantes || [];
        } else if (msg.tipo === 'PLACAR_ATUALIZADO') {
          if (msg.payload.estado_partida) {
            estadoPartida = msg.payload.estado_partida;
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

  // --- NAVEGAÇÃO E AÇÕES ---

  async function handleSelecionarArena(arena) {
    arenaAtual = arena;
    window.history.pushState({}, '', `/arena/${arena.id}`);
    await fetchQuadrasDaArena(arena.id);
  }

  function handleVoltarParaArenas() {
    arenaAtual = null;
    quadras = [];
    window.history.pushState({}, '', '/');
    fetchArenas();
  }

  async function handleCriarArena(nome) {
    try {
      submetendo = true;
      const res = await fetch('/api/arenas', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nome }),
      });
      if (res.ok) {
        const novaArena = await res.json();
        modalCriarArenaAberto = false;
        await handleSelecionarArena(novaArena);
      }
    } catch (err) {
      console.error('Erro ao criar arena:', err);
    } finally {
      submetendo = false;
    }
  }

  async function handleSelecionarQuadra(quadra) {
    const restaurou = await tentarRestaurarSessao(quadra.id);
    if (!restaurou) {
      quadraSelecionadaParaEntrar = quadra;
      modalEntrarAberto = true;
    } else {
      window.history.pushState({}, '', `/quadra/${quadra.id}`);
    }
  }

  async function handleCriarQuadra(nome) {
    if (!arenaAtual) return;
    try {
      submetendo = true;
      const res = await fetch(`/api/arenas/${arenaAtual.id}/quadras`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nome }),
      });
      if (res.ok) {
        const novaQuadra = await res.json();
        modalCriarQuadraAberto = false;
        // Abre modal para criador informar apelido e virar ADMIN
        quadraSelecionadaParaEntrar = novaQuadra;
        modalEntrarAberto = true;
        await fetchQuadrasDaArena(arenaAtual.id);
      }
    } catch (err) {
      console.error('Erro ao criar quadra:', err);
    } finally {
      submetendo = false;
    }
  }

  async function handleEntrarQuadra(apelido) {
    if (!quadraSelecionadaParaEntrar) return;
    const quadraId = quadraSelecionadaParaEntrar.id;

    try {
      submetendo = true;
      const res = await fetch(`/api/quadras/${quadraId}/entrar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ apelido }),
      });

      if (res.ok) {
        const data = await res.json();
        eu = data.participante;
        quadraAtual = data.quadra;
        modalEntrarAberto = false;
        quadraSelecionadaParaEntrar = null;

        window.history.pushState({}, '', `/quadra/${quadraId}`);
        conectarWebSocket(quadraId);
      }
    } catch (err) {
      console.error('Erro ao entrar na quadra:', err);
    } finally {
      submetendo = false;
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
      } else {
        const err = await res.json();
        console.warn('Erro ao marcar ponto:', err.detail);
      }
    } catch (e) {
      console.error('Erro de rede ao marcar ponto:', e);
    }
  }

  function handleVoltarParaQuadras() {
    if (wsSocket) {
      wsSocket.close();
      wsSocket = null;
    }
    if (wsReconnectTimer) {
      clearTimeout(wsReconnectTimer);
    }
    const arenaId = quadraAtual?.arena_id || arenaAtual?.id;
    quadraAtual = null;
    eu = null;
    participantes = [];
    estadoPartida = null;

    if (arenaId) {
      window.history.pushState({}, '', `/arena/${arenaId}`);
      fetchQuadrasDaArena(arenaId);
    } else {
      handleVoltarParaArenas();
    }
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
            await fetchArenas();
          }
        } catch {
          window.history.replaceState({}, '', '/');
          await fetchArenas();
        }
      }
      return;
    }

    // 2. Rota de arena: /arena/:id
    const arenaMatch = window.location.pathname.match(/\/arena\/([a-zA-Z0-9_-]+)/);
    if (arenaMatch && arenaMatch[1]) {
      await fetchQuadrasDaArena(arenaMatch[1]);
      return;
    }

    // 3. Raiz: lista de arenas
    await fetchArenas();

    window.addEventListener('popstate', async () => {
      const qMatch = window.location.pathname.match(/\/quadra\/([a-zA-Z0-9_-]+)/);
      if (qMatch && qMatch[1]) {
        await tentarRestaurarSessao(qMatch[1]);
        return;
      }
      const aMatch = window.location.pathname.match(/\/arena\/([a-zA-Z0-9_-]+)/);
      if (aMatch && aMatch[1]) {
        if (wsSocket) wsSocket.close();
        quadraAtual = null;
        await fetchQuadrasDaArena(aMatch[1]);
        return;
      }
      handleVoltarParaArenas();
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
      {wsConectado}
      onMarcarPonto={handleMarcarPonto}
      onVoltar={handleVoltarParaQuadras}
    />
  {:else if arenaAtual}
    <!-- Quadras da Arena Selecionada -->
    <ListaQuadras
      arena={arenaAtual}
      {quadras}
      {loading}
      onSelectQuadra={handleSelecionarQuadra}
      onAbrirCriar={() => { modalCriarQuadraAberto = true; }}
      onVoltarArenas={handleVoltarParaArenas}
    />
  {:else}
    <!-- Lista de Arenas / Clubes -->
    <ListaArenas
      {arenas}
      {loading}
      onSelectArena={handleSelecionarArena}
      onAbrirCriar={() => { modalCriarArenaAberto = true; }}
    />
  {/if}

  {#if modalCriarArenaAberto}
    <ModalCriarArena
      onCriar={handleCriarArena}
      onFechar={() => { modalCriarArenaAberto = false; }}
      {submetendo}
    />
  {/if}

  {#if modalCriarQuadraAberto}
    <ModalCriarQuadra
      onCriar={handleCriarQuadra}
      onFechar={() => { modalCriarQuadraAberto = false; }}
      {submetendo}
    />
  {/if}

  {#if modalEntrarAberto}
    <ModalEntrar
      quadra={quadraSelecionadaParaEntrar}
      onEntrar={handleEntrarQuadra}
      onVoltar={() => {
        modalEntrarAberto = false;
        quadraSelecionadaParaEntrar = null;
        if (!quadraAtual && !arenaAtual) {
          window.history.pushState({}, '', '/');
          fetchArenas();
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
