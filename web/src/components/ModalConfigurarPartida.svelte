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
    /** `tudo` (⚙), `regras` ou `equipe-a`/`equipe-b` — atalhos do placar (CV6.DS1.US6).
        A seção curta só mostra uma parte, mas salva todos os campos atuais. */
    secao = 'tudo',
    /** Só o admin, no ⚙ completo: libera a quadra para todos (CV6.DS1.US8). */
    podeLiberar = false,
    // Quadra local (CV7.US1): "liberar" vira apagar a quadra deste aparelho.
    modoLocal = false,
    onLiberar = () => {},
  } = $props();

  // Slider de 6 a 20; fora disso, ou marcando Personalizado, vale o número digitado (CV6.DS1.US7).
  const SLIDER_MIN = 6;
  const SLIDER_MAX = 20;
  const cabeNoSlider = n => Number.isInteger(n) && n >= SLIDER_MIN && n <= SLIDER_MAX;
  let alvoPersonalizado = $state(false);
  let confirmandoLiberar = $state(false);

  const mostraRegras = $derived(secao === 'tudo' || secao === 'regras');
  const mostraA = $derived(secao === 'tudo' || secao === 'equipe-a');
  const mostraB = $derived(secao === 'tudo' || secao === 'equipe-b');
  const titulo = $derived(
    isReinicio ? 'Próxima Partida: Duplas & Regras'
    : secao === 'regras' ? 'Pontuação e Vantagem'
    : secao === 'equipe-a' ? 'Jogadores da Equipe A'
    : secao === 'equipe-b' ? 'Jogadores da Equipe B'
    : 'Configurações da Partida'
  );

  let timeAJogador1 = $state('');
  let timeAJogador2 = $state('');
  let timeBJogador1 = $state('');
  let timeBJogador2 = $state('');

  let regraAlvo = $state(10);
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
      const alvo = estadoPartida.alvo ?? 10;
      regraAlvo = alvo;
      alvoPersonalizado = !cabeNoSlider(alvo);
      regraVantagem = estadoPartida.vantagem ?? true;
      regraTeto = estadoPartida.teto !== null && estadoPartida.teto !== undefined ? String(estadoPartida.teto) : '';
    }
  });

  const tetoNumerico = $derived(
    regraTeto !== '' && regraTeto !== null && regraTeto !== undefined
      ? Number(regraTeto)
      : null
  );

  const alvoInvalido = $derived(
    alvoPersonalizado && !(Number.isInteger(Number(regraAlvo)) && regraAlvo >= 1 && regraAlvo <= 100)
  );

  function alternarPersonalizado() {
    // Voltar ao slider traz o alvo para dentro da faixa.
    if (!alvoPersonalizado && !cabeNoSlider(Number(regraAlvo))) {
      regraAlvo = Math.min(SLIDER_MAX, Math.max(SLIDER_MIN, Math.round(Number(regraAlvo)) || 10));
    }
  }

  const tetoInvalido = $derived(
    regraVantagem && tetoNumerico !== null && tetoNumerico < regraAlvo
  );

  let limpouA = $state(false);
  let limpouB = $state(false);

  function limparA() { timeAJogador1 = ''; timeAJogador2 = ''; limpouA = true; }
  function limparB() { timeBJogador1 = ''; timeBJogador2 = ''; limpouB = true; }

  function handleSubmit(e) {
    e.preventDefault();
    if (tetoInvalido || alvoInvalido || submetendo) return;

    const vazioA = !timeAJogador1.trim() && !timeAJogador2.trim();
    const vazioB = !timeBJogador1.trim() && !timeBJogador2.trim();
    onSalvar({
      time_a_jogador1: timeAJogador1.trim() || undefined,
      time_a_jogador2: timeAJogador2.trim() || undefined,
      time_b_jogador1: timeBJogador1.trim() || undefined,
      time_b_jogador2: timeBJogador2.trim() || undefined,
      // Campo omitido mantém o nome atual; após "Limpar", o nome padrão vai explícito.
      equipe_a: limpouA && vazioA ? 'Equipe A' : undefined,
      equipe_b: limpouB && vazioB ? 'Equipe B' : undefined,
      alvo: Number(regraAlvo) || 10,
      vantagem: Boolean(regraVantagem),
      teto: regraVantagem && tetoNumerico !== null ? tetoNumerico : null,
      tema_placar: temaVisual,
    });
  }
</script>

<Dialogo
  rotuladoPor="titulo-config-partida"
  variante="centro"
  largura={secao === 'tudo' ? '680px' : '440px'}
  {movimentoReduzido}
  {onFechar}
>
  <div class="modal-config">
    <header class="modal-header">
      <div class="header-titulo-grupo">
        <Icone nome="regras" tamanho="1.2em" />
        <h3 id="titulo-config-partida">
          {titulo}
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
      <!-- Pontuação primeiro: é a regra que mais muda entre rodadas (CV6.DS1.US5). -->
      {#if mostraRegras}
      <div class="secao-bloco">
        {#if secao === 'tudo'}<span class="secao-rotulo">Pontuação e Vantagem</span>{/if}
        <div class="campo-alvo">
          <label for="alvo-slider" class="rotulo-alvo">
            Pontos para vencer <strong class="valor-alvo">{regraAlvo} pts</strong>
          </label>
          <input
            id="alvo-slider"
            class="slider-alvo"
            type="range"
            min={SLIDER_MIN}
            max={SLIDER_MAX}
            step="1"
            value={cabeNoSlider(Number(regraAlvo)) ? regraAlvo : SLIDER_MAX}
            oninput={e => { regraAlvo = Number(e.currentTarget.value); }}
            disabled={submetendo || alvoPersonalizado}
          />
          <div class="linha-personalizado">
            <label class="check-label">
              <input
                type="checkbox"
                bind:checked={alvoPersonalizado}
                onchange={alternarPersonalizado}
                disabled={submetendo}
              />
              <span>Personalizado</span>
            </label>
            {#if alvoPersonalizado}
              <input
                id="alvo-custom"
                class="input-personalizado"
                type="number"
                inputmode="numeric"
                min="1"
                max="100"
                step="1"
                aria-label="Pontos para vencer (personalizado)"
                bind:value={regraAlvo}
                disabled={submetendo}
                required
              />
            {/if}
          </div>
          {#if alvoInvalido}
            <p class="aviso-erro">⚠️ Use um número inteiro de 1 a 100.</p>
          {/if}
        </div>

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

      {/if}

      <!-- Seção Duplas / Equipes -->
      {#if mostraA || mostraB}
      <div class="secao-bloco">
        {#if secao === 'tudo'}<span class="secao-rotulo">Equipes e Duplas da Rodada</span>{/if}
        <div class="grid-equipes" class:uma-equipe={secao !== 'tudo'}>
          <!-- Time A -->
          {#if mostraA}
          <div class="equipe-card time-a-card">
            <div class="card-topo">
              <span class="badge-time time-a-badge">Time A</span>
              <button type="button" class="btn-limpar" onclick={limparA} disabled={submetendo} aria-label="Limpar nomes da Equipe A">Limpar</button>
            </div>
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
          {/if}

          <!-- Time B -->
          {#if mostraB}
          <div class="equipe-card time-b-card">
            <div class="card-topo">
              <span class="badge-time time-b-badge">Time B</span>
              <button type="button" class="btn-limpar" onclick={limparB} disabled={submetendo} aria-label="Limpar nomes da Equipe B">Limpar</button>
            </div>
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
          {/if}
        </div>
      </div>
      {/if}

      {#if secao === 'tudo'}
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
      {/if}

      {#if podeLiberar}
      <div class="secao-bloco zona-perigo">
        <span class="secao-rotulo">Quadra</span>
        {#if confirmandoLiberar}
          <p class="aviso-liberar" role="alert">
            {#if modoLocal}
              Isso apaga a quadra local deste aparelho, agora. Placar e histórico somem. Não dá para desfazer.
            {:else}
              Isso encerra a quadra para todos, agora. Placar e histórico somem e o código deixa de valer. Não dá para desfazer.
            {/if}
          </p>
          <div class="acoes-liberar">
            <button type="button" class="btn-cancelar" onclick={() => { confirmandoLiberar = false; }} disabled={submetendo}>
              Manter quadra
            </button>
            <button type="button" class="btn-liberar" onclick={onLiberar} disabled={submetendo}>
              {modoLocal ? 'Apagar agora' : 'Liberar agora'}
            </button>
          </div>
        {:else}
          <button type="button" class="btn-liberar" onclick={() => { confirmandoLiberar = true; }} disabled={submetendo}>
            {modoLocal ? 'Apagar quadra local' : 'Liberar quadra'}
          </button>
        {/if}
      </div>
      {/if}

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
          disabled={submetendo || tetoInvalido || alvoInvalido}
        >
          {submetendo ? 'Salvando...' : isReinicio ? 'Iniciar Rodada' : 'Salvar Alterações'}
        </button>
      </div>
    </form>
  </div>
</Dialogo>

<style>
  /* Margem interna própria (CV6.DS1.US5): a caixa do Dialogo não tem padding.
     Cabeçalho e ações ficam presos às bordas enquanto só o conteúdo rola. */
  .modal-config {
    display: flex;
    flex-direction: column;
    gap: 20px;
    padding: 0 24px;
  }

  .modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid var(--border-color);
    position: sticky;
    top: 0;
    z-index: 1;
    margin: 0 -24px;
    padding: 18px 24px 14px;
    background: var(--fundo-superficie);
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
    gap: 24px;
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

  .grid-equipes.uma-equipe { grid-template-columns: 1fr; }

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

  .card-topo {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .btn-limpar {
    background: transparent;
    border: 1px solid var(--border-color);
    border-radius: var(--radius-sm);
    color: var(--text-secondary);
    padding: 4px 10px;
    font-size: var(--texto-legenda);
    font-weight: 600;
    cursor: pointer;
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

  .campo-alvo {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .rotulo-alvo {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    color: var(--text-primary);
    font-size: var(--texto-apoio);
  }

  .valor-alvo {
    font-size: 1.25rem;
    font-variant-numeric: tabular-nums;
  }

  .slider-alvo {
    width: 100%;
    min-height: 44px;
    margin: 0;
    accent-color: var(--acento-info-forte);
    touch-action: pan-y;
  }

  .slider-alvo:disabled {
    opacity: 0.4;
  }

  .linha-personalizado {
    display: flex;
    align-items: center;
    gap: 12px;
    min-height: 44px;
  }

  .input-personalizado {
    width: 6em;
    min-height: 44px;
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-sm);
    color: var(--text-primary);
    padding: 8px 10px;
    font-size: var(--texto-apoio);
    box-sizing: border-box;
  }

  .aviso-liberar {
    margin: 0;
    color: var(--text-primary);
    font-size: var(--texto-apoio);
  }

  .acoes-liberar {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
  }

  .btn-liberar {
    align-self: flex-start;
    min-height: 44px;
    background: transparent;
    border: 1px solid var(--estado-erro);
    border-radius: var(--radius-md);
    color: var(--estado-erro);
    padding: 10px 18px;
    font-size: var(--texto-apoio);
    font-weight: 700;
    cursor: pointer;
  }

  .acoes-liberar .btn-liberar {
    background: var(--estado-erro);
    color: var(--fundo-superficie);
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
    position: sticky;
    bottom: 0;
    margin: 0 -24px;
    padding: 14px 24px max(16px, env(safe-area-inset-bottom));
    border-top: 1px solid var(--border-color);
    background: var(--fundo-superficie);
  }

  @media (max-width: 480px) {
    .modal-config { gap: 16px; padding: 0 16px; }
    .modal-header { margin: 0 -16px; padding: 14px 16px 12px; }
    .modal-acoes { margin: 0 -16px; padding-inline: 16px; }
    .modal-acoes .btn-salvar { flex: 1 1 auto; white-space: nowrap; }
    .header-titulo-grupo h3 { font-size: 1.05rem; }
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
