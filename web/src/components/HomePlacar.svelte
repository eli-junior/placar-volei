<script>
  import { onMount } from 'svelte';
  import { slide, fade } from 'svelte/transition';
  import Icone from './Icone.svelte';

  let {
    onCriarQuadra = () => {},
    onEntrarQuadra = () => {},
    submetendo = false,
    erro = null,
  } = $props();

  const CHAVE_APELIDO = 'placar:apelido';
  const CHAVE_TEMA = 'placar:tema';

  let abaAtiva = $state('criar'); // 'criar' | 'acompanhar'
  let apelidoCriador = $state('');
  let nomeQuadra = $state('');
  let temaSol = $state(false);

  let timeAJogador1 = $state('');
  let timeAJogador2 = $state('');
  let timeBJogador1 = $state('');
  let timeBJogador2 = $state('');

  let codigoQuadra = $state('');
  let apelidoEspectador = $state('');

  let quadrasAtivas = $state([]);
  let carregandoQuadras = $state(false);

  onMount(() => {
    try {
      const salvo = localStorage.getItem(CHAVE_APELIDO);
      if (salvo) {
        apelidoCriador = salvo;
        apelidoEspectador = salvo;
      }
      const salvoTema = localStorage.getItem(CHAVE_TEMA);
      if (salvoTema === 'sol') {
        temaSol = true;
        document.documentElement.setAttribute('data-tema', 'sol');
      }
    } catch {}

    carregarQuadrasAtivas();
  });

  function alternarTema() {
    temaSol = !temaSol;
    try {
      localStorage.setItem(CHAVE_TEMA, temaSol ? 'sol' : 'padrao');
    } catch {}
    if (temaSol) {
      document.documentElement.setAttribute('data-tema', 'sol');
    } else {
      document.documentElement.removeAttribute('data-tema');
    }
  }

  async function carregarQuadrasAtivas() {
    try {
      carregandoQuadras = true;
      const res = await fetch('/api/quadras');
      if (res.ok) {
        const data = await res.json();
        quadrasAtivas = data.quadras || [];
      }
    } catch (e) {
      console.warn('Erro ao carregar quadras ativas:', e);
    } finally {
      carregandoQuadras = false;
    }
  }

  let regraAlvo = $state(12);
  let regraVantagem = $state(true);
  let regraTeto = $state('');

  const tetoNumerico = $derived(
    regraTeto !== '' && regraTeto !== null && regraTeto !== undefined
      ? Number(regraTeto)
      : null
  );

  const tetoInvalido = $derived(
    regraVantagem && tetoNumerico !== null && tetoNumerico < regraAlvo
  );

  function handleSubmeterCriar(e) {
    e.preventDefault();
    const apelido = apelidoCriador.trim();
    if (!apelido) return;

    try {
      localStorage.setItem(CHAVE_APELIDO, apelido);
    } catch {}

    onCriarQuadra({
      apelido,
      nome: nomeQuadra.trim() || undefined,
    });
  }

  function handleSubmeterAcompanhar(e) {
    e.preventDefault();
    const codigo = codigoQuadra.trim();
    const apelido = apelidoEspectador.trim();
    if (!codigo || !apelido) return;

    try {
      localStorage.setItem(CHAVE_APELIDO, apelido);
    } catch {}

    onEntrarQuadra({
      quadraId: codigo,
      apelido,
    });
  }

  function selecionarQuadraAtiva(q) {
    codigoQuadra = q.id;
    abaAtiva = 'acompanhar';
  }
</script>

<div class="home-container" in:fade={{ duration: 200 }}>
  <div class="barra-superior-home">
    <button
      type="button"
      class="btn-toggle-sol"
      onclick={alternarTema}
      aria-label={temaSol ? 'Ativar Modo Noite' : 'Ativar Modo Sol'}
      title={temaSol ? 'Modo Noite' : 'Modo Sol (Alto Contraste)'}
    >
      <Icone nome={temaSol ? 'lua' : 'sol'} tamanho="1.15em" />
      <span>{temaSol ? 'Modo Noite' : 'Modo Sol'}</span>
    </button>
  </div>

  <header class="home-header">
    <div class="logo-badge">🏐</div>
    <h1 class="app-title">Placar de Vôlei</h1>
    <p class="app-subtitle">Placar em tempo real para voleibol e beach tennis</p>
  </header>

  {#if erro}
    <div class="alerta-erro" in:slide={{ duration: 200 }}>
      <span class="alerta-icone">⚠️</span>
      <span class="alerta-texto">{erro}</span>
    </div>
  {/if}

  <!-- Seletor de Abas -->
  <div class="abas-navegacao" role="tablist">
    <button
      type="button"
      role="tab"
      aria-selected={abaAtiva === 'criar'}
      class="aba-btn"
      class:ativa={abaAtiva === 'criar'}
      onclick={() => { abaAtiva = 'criar'; }}
    >
      <span class="aba-icone">⚡</span>
      <span class="aba-label">Criar Placar</span>
    </button>

    <button
      type="button"
      role="tab"
      aria-selected={abaAtiva === 'acompanhar'}
      class="aba-btn"
      class:ativa={abaAtiva === 'acompanhar'}
      onclick={() => { abaAtiva = 'acompanhar'; }}
    >
      <span class="aba-icone">👁️</span>
      <span class="aba-label">Acompanhar</span>
    </button>
  </div>

  <!-- Cartão de Ação -->
  <div class="cartao-acao">
    {#if abaAtiva === 'criar'}
      <form class="form-acao" onsubmit={handleSubmeterCriar} in:fade={{ duration: 150 }}>
        <div class="card-intro">
          <h2 class="card-titulo">Criar Nova Sala</h2>
          <p class="card-desc">
            Você será o <strong>Administrador</strong> da sala e controlará a pontuação. Um código de 5 dígitos será gerado.
          </p>
        </div>

        <div class="campo-grupo">
          <label for="apelido-criador">Seu nome ou apelido <span class="obrigatorio">*</span></label>
          <input
            id="apelido-criador"
            type="text"
            bind:value={apelidoCriador}
            placeholder="Ex: Carlos, Ana, Juiz"
            maxlength="30"
            required
            disabled={submetendo}
          />
        </div>

        <div class="campo-grupo">
          <label for="nome-quadra">Nome da quadra (opcional)</label>
          <input
            id="nome-quadra"
            type="text"
            bind:value={nomeQuadra}
            placeholder="Ex: Quadra Central, Areia 1"
            maxlength="50"
            disabled={submetendo}
          />
        </div>

        <div class="card-info-box">
          <Icone nome="informacao" tamanho="1.1em" class="info-icone" />
          <span>Você poderá definir e trocar as duplas e regras da partida a qualquer momento dentro da sala.</span>
        </div>

        <button
          type="submit"
          class="btn-principal"
          disabled={submetendo || !apelidoCriador.trim()}
        >
          {submetendo ? 'Criando sala...' : 'Criar Placar e Iniciar'}
        </button>
      </form>
    {:else}
      <form class="form-acao" onsubmit={handleSubmeterAcompanhar} in:fade={{ duration: 150 }}>
        <div class="card-intro">
          <h2 class="card-titulo">Acompanhar Sala</h2>
          <p class="card-desc">
            Digite o número de 5 dígitos da quadra para acompanhar a pontuação ao vivo como <strong>Espectador</strong>.
          </p>
        </div>

        <div class="campo-grupo">
          <label for="codigo-quadra">Código da Quadra (5 dígitos) <span class="obrigatorio">*</span></label>
          <input
            id="codigo-quadra"
            class="input-codigo"
            type="text"
            inputmode="numeric"
            pattern="[0-9]*"
            maxlength="5"
            bind:value={codigoQuadra}
            placeholder="Ex: 12345"
            required
            disabled={submetendo}
          />
        </div>

        <div class="campo-grupo">
          <label for="apelido-espectador">Seu nome ou apelido <span class="obrigatorio">*</span></label>
          <input
            id="apelido-espectador"
            type="text"
            bind:value={apelidoEspectador}
            placeholder="Ex: Torcedor, Bia"
            maxlength="30"
            required
            disabled={submetendo}
          />
        </div>

        <button
          type="submit"
          class="btn-principal"
          disabled={submetendo || !codigoQuadra.trim() || !apelidoEspectador.trim()}
        >
          {submetendo ? 'Entrando...' : 'Entrar como Espectador'}
        </button>
      </form>
    {/if}
  </div>

  <!-- Salas Ativas Disponíveis -->
  <section class="secao-salas-ativas">
    <div class="salas-header">
      <h3 class="salas-titulo">
        Quadras em Andamento
        <span class="badge-contagem">{quadrasAtivas.length}/20</span>
      </h3>
      <button
        type="button"
        class="btn-recarregar"
        onclick={carregarQuadrasAtivas}
        disabled={carregandoQuadras}
        title="Atualizar lista"
      >
        {carregandoQuadras ? '...' : '↻ Atualizar'}
      </button>
    </div>

    {#if carregandoQuadras && quadrasAtivas.length === 0}
      <p class="salas-vazio">Verificando salas ativas...</p>
    {:else if quadrasAtivas.length === 0}
      <div class="salas-card-vazio">
        <p>Nenhuma quadra ativa no momento.</p>
        <p class="sub-vazio">Crie uma nova sala acima para começar!</p>
      </div>
    {:else}
      <div class="grade-salas">
        {#each quadrasAtivas as q (q.id)}
          <button
            type="button"
            class="item-sala"
            onclick={() => selecionarQuadraAtiva(q)}
          >
            <div class="sala-pin">
              <span class="pin-label">CÓDIGO</span>
              <span class="pin-numero">{q.id}</span>
            </div>
            <div class="sala-detalhes">
              <h4 class="sala-nome">{q.nome}</h4>
              <span class="sala-participantes">
                👥 {q.participantes_count || 0}/20 pessoas
              </span>
            </div>
            <span class="sala-seta">→</span>
          </button>
        {/each}
      </div>
    {/if}
  </section>
</div>

<style>
  .home-container {
    display: flex;
    flex-direction: column;
    width: 100%;
    max-width: 480px;
    margin: 0 auto;
    padding: 1.5rem 1rem 3rem;
    gap: 1.5rem;
    box-sizing: border-box;
  }

  .barra-superior-home {
    display: flex;
    justify-content: flex-end;
    width: 100%;
  }

  .btn-toggle-sol {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-circular);
    color: var(--text-primary);
    padding: 6px 14px;
    font-size: var(--texto-legenda);
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: all 0.15s ease;
  }

  .btn-toggle-sol:hover {
    background: var(--bg-card-hover);
    border-color: rgba(255, 255, 255, 0.2);
  }

  .home-header {
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.35rem;
  }

  .logo-badge {
    font-size: 2.75rem;
    line-height: 1;
    margin-bottom: 0.25rem;
  }

  .app-title {
    font-size: 1.75rem;
    font-weight: 800;
    color: #f8fafc;
    margin: 0;
    letter-spacing: -0.02em;
  }

  .app-subtitle {
    font-size: 0.95rem;
    color: #94a3b8;
    margin: 0;
  }

  .alerta-erro {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid rgba(239, 68, 68, 0.35);
    color: #fca5a5;
    padding: 0.85rem 1rem;
    border-radius: 12px;
    font-size: 0.9rem;
    line-height: 1.35;
  }

  .alerta-icone {
    font-size: 1.25rem;
    flex-shrink: 0;
  }

  .abas-navegacao {
    display: flex;
    background: #1e293b;
    padding: 0.3rem;
    border-radius: 14px;
    gap: 0.3rem;
    border: 1px solid #334155;
  }

  .aba-btn {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    background: transparent;
    border: none;
    color: #94a3b8;
    padding: 0.75rem 0.5rem;
    font-size: 0.95rem;
    font-weight: 600;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .aba-btn.ativa {
    background: #0284c7;
    color: #ffffff;
    box-shadow: 0 2px 8px rgba(2, 132, 199, 0.35);
  }

  .aba-btn:hover:not(.ativa) {
    color: #f1f5f9;
    background: rgba(255, 255, 255, 0.04);
  }

  .cartao-acao {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
  }

  .form-acao {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
  }

  .card-intro {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .card-titulo {
    font-size: 1.2rem;
    font-weight: 700;
    color: #f1f5f9;
    margin: 0;
  }

  .card-desc {
    font-size: 0.85rem;
    color: #94a3b8;
    margin: 0;
    line-height: 1.4;
  }

  .campo-grupo {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
  }

  .campo-grupo label {
    font-size: 0.85rem;
    font-weight: 600;
    color: #cbd5e1;
  }

  .obrigatorio {
    color: #f87171;
  }

  .campo-grupo input {
    background: #0f172a;
    border: 1px solid #334155;
    color: #ffffff;
    padding: 0.8rem 1rem;
    font-size: 1rem;
    border-radius: 10px;
    outline: none;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
  }

  .campo-grupo input:focus {
    border-color: #38bdf8;
    box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2);
  }

  .input-codigo {
    font-size: 1.5rem !important;
    font-weight: 800;
    letter-spacing: 0.25em;
    text-align: center;
    color: #38bdf8 !important;
  }

  .input-codigo::placeholder {
    letter-spacing: normal;
    font-size: 1rem;
    font-weight: normal;
    color: #64748b;
  }

  .card-info-box {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid #334155;
    padding: 0.65rem 0.85rem;
    border-radius: 8px;
    font-size: 0.78rem;
    color: #94a3b8;
    line-height: 1.35;
  }

  :global(.info-icone) {
    flex-shrink: 0;
  }

  .btn-principal {
    background: #0284c7;
    color: #ffffff;
    border: none;
    padding: 0.95rem 1.25rem;
    font-size: 1rem;
    font-weight: 700;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .btn-principal:hover:not(:disabled) {
    background: #0369a1;
    box-shadow: 0 4px 14px rgba(2, 132, 199, 0.4);
    transform: translateY(-1px);
  }

  .btn-principal:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* Seção Salas Ativas */
  .secao-salas-ativas {
    display: flex;
    flex-direction: column;
    gap: 0.85rem;
  }

  .salas-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .salas-titulo {
    font-size: 1rem;
    font-weight: 700;
    color: #cbd5e1;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .badge-contagem {
    font-size: 0.75rem;
    font-weight: 600;
    background: #334155;
    color: #94a3b8;
    padding: 0.15rem 0.45rem;
    border-radius: 6px;
  }

  .btn-recarregar {
    background: transparent;
    border: none;
    color: #38bdf8;
    font-size: 0.8rem;
    cursor: pointer;
    padding: 0.25rem 0.5rem;
    border-radius: 6px;
  }

  .btn-recarregar:hover:not(:disabled) {
    background: rgba(56, 189, 248, 0.1);
  }

  .salas-vazio, .salas-card-vazio {
    background: #1e293b;
    border: 1px dashed #334155;
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    color: #94a3b8;
    font-size: 0.9rem;
    margin: 0;
  }

  .sub-vazio {
    font-size: 0.8rem;
    color: #64748b;
    margin-top: 0.25rem;
  }

  .grade-salas {
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
  }

  .item-sala {
    display: flex;
    align-items: center;
    gap: 0.85rem;
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 0.85rem 1rem;
    text-align: left;
    color: inherit;
    cursor: pointer;
    transition: all 0.18s ease;
  }

  .item-sala:hover {
    border-color: #38bdf8;
    background: #24344d;
    transform: translateX(2px);
  }

  .sala-pin {
    display: flex;
    flex-direction: column;
    align-items: center;
    background: #0f172a;
    border: 1px solid #38bdf8;
    border-radius: 8px;
    padding: 0.35rem 0.55rem;
    min-width: 54px;
  }

  .pin-label {
    font-size: 0.6rem;
    font-weight: 700;
    color: #94a3b8;
    letter-spacing: 0.05em;
  }

  .pin-numero {
    font-size: 1.05rem;
    font-weight: 800;
    color: #38bdf8;
    letter-spacing: 0.05em;
  }

  .sala-detalhes {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
  }

  .sala-nome {
    font-size: 0.95rem;
    font-weight: 700;
    color: #f8fafc;
    margin: 0;
  }

  .sala-participantes {
    font-size: 0.78rem;
    color: #94a3b8;
  }

  .sala-seta {
    color: #64748b;
    font-size: 1.1rem;
    font-weight: bold;
  }
</style>
