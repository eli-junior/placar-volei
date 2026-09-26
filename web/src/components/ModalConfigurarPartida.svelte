<script>
  import Dialogo from './Dialogo.svelte';
  import Icone from './Icone.svelte';

  let {
    estadoPartida = null,
    temaPlacar = 'esportivo',
    isReinicio = false,
    onSalvar = () => {},
    onFechar = () => {},
    movimentoReduzido = false,
    submetendo = false,
  } = $props();

  let timeAJogador1 = $state('');
  let timeAJogador2 = $state('');
  let timeBJogador1 = $state('');
  let timeBJogador2 = $state('');

  let regraAlvo = $state(12);
  let regraVantagem = $state(true);
  let regraTeto = $state('');
  let temaVisual = $state('esportivo');

  $effect(() => {
    temaVisual = temaPlacar === 'classico' ? 'classico' : 'esportivo';
  });

  $effect(() => {
    if (estadoPartida) {
      timeAJogador1 = estadoPartida.jogadores_a?.[0] || '';
      timeAJogador2 = estadoPartida.jogadores_a?.[1] || '';
      timeBJogador1 = estadoPartida.jogadores_b?.[0] || '';
      timeBJogador2 = estadoPartida.jogadores_b?.[1] || '';
      regraAlvo = estadoPartida.alvo ?? 12;
      regraVantagem = estadoPartida.vantagem ?? true;
      regraTeto = estadoPartida.teto !== null && estadoPartida.teto !== undefined ? String(estadoPartida.teto) : '';
    }
  });

  const tetoNumerico = $derived(
    regraTeto !== '' && regraTeto !== null && regraTeto !== undefined
      ? Number(regraTeto)
      : null
  );

  const tetoInvalido = $derived(
    regraVantagem && tetoNumerico !== null && tetoNumerico < regraAlvo
  );

  function handleSubmit(e) {
    e.preventDefault();
    if (tetoInvalido || submetendo) return;

    onSalvar({
      time_a_jogador1: timeAJogador1.trim() || undefined,
      time_a_jogador2: timeAJogador2.trim() || undefined,
      time_b_jogador1: timeBJogador1.trim() || undefined,
      time_b_jogador2: timeBJogador2.trim() || undefined,
      alvo: Number(regraAlvo) || 12,
      vantagem: Boolean(regraVantagem),
      teto: regraVantagem && tetoNumerico !== null ? tetoNumerico : null,
      tema_placar: temaVisual,
    });
  }
</script>

<Dialogo
  rotuladoPor="titulo-config-partida"
  variante="centro"
  largura="480px"
  {movimentoReduzido}
  {onFechar}
>
  <div class="modal-config">
    <header class="modal-header">
      <div class="header-titulo-grupo">
        <Icone nome="regras" tamanho="1.2em" />
        <h3 id="titulo-config-partida">
          {isReinicio ? 'Próxima Partida: Duplas & Regras' : 'Configurações da Partida'}
        </h3>
      </div>
      <button
        type="button"
        class="btn-fechar"
        onclick={onFechar}
        aria-label="Fechar configurações da partida"
      >
        <Icone nome="fechar" tamanho="1.1em" />
      </button>
    </header>

    <form onsubmit={handleSubmit} class="form-config">
      <div class="secao-bloco">
        <span class="secao-rotulo">Visual do placar</span>
        <div class="seletor-tema" role="radiogroup" aria-label="Tema do placar para todos na quadra">
          <button
            type="button"
            class="tema-opcao"
            class:selecionado={temaVisual === 'esportivo'}
            role="radio"
            aria-checked={temaVisual === 'esportivo'}
            onclick={() => { temaVisual = 'esportivo'; }}
            disabled={submetendo}
          >
            <strong>Esportivo</strong>
            <span>Números grandes e leitura à distância</span>
          </button>
          <button
            type="button"
            class="tema-opcao"
            class:selecionado={temaVisual === 'classico'}
            role="radio"
            aria-checked={temaVisual === 'classico'}
            onclick={() => { temaVisual = 'classico'; }}
            disabled={submetendo}
          >
            <strong>Clássico</strong>
            <span>Cartões mecânicos com efeito de virada</span>
          </button>
        </div>
      </div>

      <!-- Seção Duplas / Equipes -->
      <div class="secao-bloco">
        <span class="secao-rotulo">Equipes e Duplas da Rodada</span>
        <div class="grid-equipes">
          <!-- Time A -->
          <div class="equipe-card time-a-card">
            <span class="badge-time time-a-badge">Time A</span>
            <div class="campo">
              <label for="cfg-time-a-j1">Jogador 1</label>
              <input
                id="cfg-time-a-j1"
                type="text"
                bind:value={timeAJogador1}
                placeholder="Ex: Carlos"
                maxlength="30"
                disabled={submetendo}
              />
            </div>
            <div class="campo">
              <label for="cfg-time-a-j2">Jogador 2</label>
              <input
                id="cfg-time-a-j2"
                type="text"
                bind:value={timeAJogador2}
                placeholder="Ex: Daniel"
                maxlength="30"
                disabled={submetendo}
              />
            </div>
          </div>

          <!-- Time B -->
          <div class="equipe-card time-b-card">
            <span class="badge-time time-b-badge">Time B</span>
            <div class="campo">
              <label for="cfg-time-b-j1">Jogador 1</label>
              <input
                id="cfg-time-b-j1"
                type="text"
                bind:value={timeBJogador1}
                placeholder="Ex: Roberto"
                maxlength="30"
                disabled={submetendo}
              />
            </div>
            <div class="campo">
              <label for="cfg-time-b-j2">Jogador 2</label>
              <input
                id="cfg-time-b-j2"
                type="text"
                bind:value={timeBJogador2}
                placeholder="Ex: Eduardo"
                maxlength="30"
                disabled={submetendo}
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Seção Regras de Pontuação -->
      <div class="secao-bloco">
        <span class="secao-rotulo">Pontuação e Vantagem</span>
        <div class="pills-alvo">
          {#each [12, 15, 21, 25] as preset}
            <button
              type="button"
              class="btn-pill"
              class:selecionado={regraAlvo === preset}
              onclick={() => { regraAlvo = preset; }}
              disabled={submetendo}
            >
              {preset} pts
            </button>
          {/each}
          <button
            type="button"
            class="btn-pill"
            class:selecionado={![12, 15, 21, 25].includes(regraAlvo)}
            onclick={() => {
              if ([12, 15, 21, 25].includes(regraAlvo)) regraAlvo = 18;
            }}
            disabled={submetendo}
          >
            Personalizado
          </button>
        </div>

        {#if ![12, 15, 21, 25].includes(regraAlvo)}
          <div class="campo campo-personalizado">
            <label for="alvo-custom">Pontos para vencer</label>
            <input
              id="alvo-custom"
              type="number"
              min="1"
              max="100"
              bind:value={regraAlvo}
              disabled={submetendo}
              required
            />
          </div>
        {/if}

        <div class="campo-check">
          <label class="check-label">
            <input
              type="checkbox"
              bind:checked={regraVantagem}
              disabled={submetendo}
            />
            <span>Exigir vantagem de 2 pontos</span>
          </label>
        </div>

        {#if regraVantagem}
          <div class="campo">
            <label for="cfg-teto">Teto de pontos (opcional)</label>
            <input
              id="cfg-teto"
              type="number"
              min={regraAlvo}
              max="200"
              bind:value={regraTeto}
              placeholder="Ex: {regraAlvo + 3} (vazio para sem teto)"
              disabled={submetendo}
            />
            {#if tetoInvalido}
              <p class="aviso-erro">⚠️ O teto não pode ser menor que o alvo ({regraAlvo} pts).</p>
            {/if}
          </div>
        {/if}
      </div>

      <div class="modal-acoes">
        <button
          type="button"
          class="btn-cancelar"
          onclick={onFechar}
          disabled={submetendo}
        >
          Cancelar
        </button>
        <button
          type="submit"
          class="btn-salvar"
          disabled={submetendo || tetoInvalido}
        >
          {submetendo ? 'Salvando...' : isReinicio ? 'Iniciar Rodada' : 'Salvar Alterações'}
        </button>
      </div>
    </form>
  </div>
</Dialogo>

<style>
  .modal-config {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 12px;
  }

  .header-titulo-grupo {
    display: flex;
    align-items: center;
    gap: 10px;
    color: var(--text-primary);
  }

  .header-titulo-grupo h3 {
    margin: 0;
    font-size: var(--texto-titulo);
    font-weight: 700;
  }

  .btn-fechar {
    background: transparent;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    padding: 6px;
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .form-config {
    display: flex;
    flex-direction: column;
    gap: 18px;
  }

  .secao-bloco {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .secao-rotulo {
    font-size: var(--texto-apoio);
    font-weight: 700;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .grid-equipes {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }

  .seletor-tema {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }

  .tema-opcao {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
    min-height: 78px;
    padding: 12px;
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    background: var(--bg-card);
    color: var(--text-primary);
    text-align: left;
    cursor: pointer;
  }

  .tema-opcao span {
    color: var(--text-muted);
    font-size: var(--texto-legenda);
    line-height: 1.35;
  }

  .tema-opcao.selecionado {
    border-color: var(--acento-info);
    background: color-mix(in srgb, var(--acento-info-forte) 12%, var(--bg-card));
    box-shadow: inset 0 0 0 1px var(--acento-info);
  }

  @media (max-width: 480px) {
    .grid-equipes, .seletor-tema {
      grid-template-columns: 1fr;
    }
  }

  .equipe-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 12px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .time-a-card {
    border-left: 3px solid var(--time-a);
  }

  .time-b-card {
    border-left: 3px solid var(--time-b);
  }

  .badge-time {
    font-size: var(--texto-micro);
    font-weight: 700;
    text-transform: uppercase;
  }

  .time-a-badge { color: var(--time-a); }
  .time-b-badge { color: var(--time-b); }

  .campo {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .campo label {
    font-size: var(--texto-legenda);
    color: var(--text-muted);
  }

  .campo input {
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-sm);
    color: var(--text-primary);
    padding: 8px 10px;
    font-size: var(--texto-apoio);
    box-sizing: border-box;
    width: 100%;
  }

  .pills-alvo {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }

  .btn-pill {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-circular);
    color: var(--text-secondary);
    padding: 6px 14px;
    font-size: var(--texto-apoio);
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .btn-pill.selecionado {
    background: var(--acento-info-forte);
    color: #ffffff;
    border-color: var(--acento-info);
  }

  .campo-check {
    margin-top: 4px;
  }

  .check-label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: var(--texto-apoio);
    color: var(--text-primary);
    cursor: pointer;
  }

  .aviso-erro {
    margin: 4px 0 0 0;
    color: var(--estado-erro);
    font-size: var(--texto-legenda);
  }

  .modal-acoes {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 8px;
  }

  .btn-cancelar {
    background: transparent;
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    color: var(--text-secondary);
    padding: 10px 18px;
    font-size: var(--texto-apoio);
    font-weight: 600;
    cursor: pointer;
  }

  .btn-salvar {
    background: var(--acento-info-forte);
    border: none;
    border-radius: var(--radius-md);
    color: #ffffff;
    padding: 10px 20px;
    font-size: var(--texto-apoio);
    font-weight: 700;
    cursor: pointer;
    transition: background 0.15s ease;
  }

  .btn-salvar:hover {
    background: var(--acento-info-ativo);
  }

  .btn-salvar:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
</style>
