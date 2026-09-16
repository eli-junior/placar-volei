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
    const apelido = apelidoEspectador.trim() || apelidoCriador.trim();
    if (apelido) {
      try {
        localStorage.setItem(CHAVE_APELIDO, apelido);
      } catch {}
      onEntrarQuadra({
        quadraId: q.id,
        apelido,
      });
    } else {
      abaAtiva = 'acompanhar';
      if (typeof document !== 'undefined') {
        setTimeout(() => {
          document.getElementById('apelido-espectador')?.focus();
        }, 60);
      }
    }
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

  <div class="home-layout-grid">
    <div class="coluna-acao">
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
          aria-label="Atualizar lista de quadras em andamento"
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
              aria-label="Entrar na quadra {q.nome}, código {q.id}{q.partida ? `, placar ${q.partida.pontos_a} a ${q.partida.pontos_b}` : ''}"
            >
              <div class="sala-pin">
                <span class="pin-label">CÓDIGO</span>
                <span class="pin-numero">{q.id}</span>
              </div>

              <div class="sala-detalhes">
                <div class="sala-cabecalho-linha">
                  <h4 class="sala-nome">{q.nome}</h4>
                  {#if q.partida && !q.partida.encerrada}
                    <span class="badge-ao-vivo">
                      <span class="dot-ao-vivo" aria-hidden="true"></span>
                      AO VIVO
                    </span>
                  {:else if q.partida && q.partida.encerrada}
                    <span class="badge-finalizada">FINALIZADA</span>
                  {/if}
                </div>

                {#if q.partida}
                  <div class="sala-placar-resumo">
                    <span class="placar-times">
                      <span class="time-rotulo">{q.partida.equipe_a}</span>
                      <strong class="placar-numeros">{q.partida.pontos_a} × {q.partida.pontos_b}</strong>
                      <span class="time-rotulo">{q.partida.equipe_b}</span>
                    </span>
                  </div>
                {:else}
                  <span class="sala-aguardando">Aguardando início</span>
                {/if}

                <span class="sala-participantes">
                  👥 {q.participantes_count || 0}/20 pessoas
                </span>
              </div>

              <div class="sala-acao">
                <span class="sala-entrar-label">{apelidoEspectador.trim() || apelidoCriador.trim() ? 'Entrar' : 'Acompanhar'}</span>
                <span class="sala-seta" aria-hidden="true">→</span>
              </div>
            </button>
          {/each}
        </div>
      {/if}
    </section>
  </div>
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
    overflow-x: hidden;
  }

  .home-layout-grid {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    width: 100%;
  }

  .coluna-acao {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    width: 100%;
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
    min-height: 44px;
    box-sizing: border-box;
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
    min-height: 44px;
    box-sizing: border-box;
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
    border: 1px solid rgba(56, 189, 248, 0.25);
    color: #38bdf8;
    font-size: 0.82rem;
    font-weight: 600;
    cursor: pointer;
    padding: 6px 12px;
    min-height: 44px;
    box-sizing: border-box;
    border-radius: 8px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    transition: all 0.15s ease;
  }

  .btn-recarregar:hover:not(:disabled) {
    background: rgba(56, 189, 248, 0.15);
    border-color: #38bdf8;
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
    gap: 0.75rem;
  }

  .item-sala {
    display: flex;
    align-items: center;
    gap: 0.85rem;
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 0.85rem 1rem;
    min-height: 64px;
    box-sizing: border-box;
    text-align: left;
    color: inherit;
    cursor: pointer;
    transition: all 0.18s ease;
  }

  .item-sala:hover {
    border-color: #38bdf8;
    background: #24344d;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
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
    flex-shrink: 0;
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
    gap: 0.25rem;
    min-width: 0;
  }

  .sala-cabecalho-linha {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 6px;
    flex-wrap: wrap;
  }

  .sala-nome {
    font-size: 0.95rem;
    font-weight: 700;
    color: #f8fafc;
    margin: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 170px;
  }

  .badge-ao-vivo {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 0.65rem;
    font-weight: 800;
    color: #f87171;
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid rgba(239, 68, 68, 0.4);
    padding: 2px 7px;
    border-radius: 999px;
    letter-spacing: 0.05em;
  }

  .dot-ao-vivo {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: #ef4444;
    box-shadow: 0 0 6px #ef4444;
    animation: pulso-dot 1.2s ease-in-out infinite;
  }

  @keyframes pulso-dot {
    0%, 100% { opacity: 0.35; transform: scale(0.85); }
    50% { opacity: 1; transform: scale(1.15); }
  }

  @media (prefers-reduced-motion: reduce) {
    .dot-ao-vivo {
      animation: none;
    }
  }

  .badge-finalizada {
    font-size: 0.65rem;
    font-weight: 700;
    color: #94a3b8;
    background: #334155;
    padding: 2px 7px;
    border-radius: 999px;
  }

  .sala-placar-resumo {
    display: flex;
    align-items: center;
    margin: 1px 0;
  }

  .placar-times {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.82rem;
    color: #cbd5e1;
    flex-wrap: wrap;
  }

  .time-rotulo {
    max-width: 80px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .placar-numeros {
    font-family: var(--fonte-placar, 'Teko', sans-serif);
    font-size: 1.35rem;
    color: #38bdf8;
    letter-spacing: 0.04em;
    line-height: 1;
    font-weight: 700;
  }

  .sala-aguardando {
    font-size: 0.78rem;
    color: #64748b;
    font-style: italic;
  }

  .sala-participantes {
    font-size: 0.78rem;
    color: #94a3b8;
  }

  .sala-acao {
    display: flex;
    align-items: center;
    gap: 4px;
    color: #38bdf8;
    font-size: 0.82rem;
    font-weight: 700;
    flex-shrink: 0;
  }

  .sala-entrar-label {
    letter-spacing: 0.02em;
  }

  .sala-seta {
    color: #38bdf8;
    font-size: 1.1rem;
    font-weight: bold;
    transition: transform 0.15s ease;
  }

  .item-sala:hover .sala-seta {
    transform: translateX(3px);
  }

  @media (min-width: 960px) {
    .home-container {
      max-width: 1060px;
      padding: 2.5rem 2rem 4rem;
      gap: 2rem;
    }

    .home-layout-grid {
      display: grid;
      grid-template-columns: 460px 1fr;
      gap: 2.5rem;
      align-items: start;
    }

    .grade-salas {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
      gap: 0.85rem;
    }
  }
</style>
