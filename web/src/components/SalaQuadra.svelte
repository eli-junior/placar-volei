<script>
  import { fade, slide } from 'svelte/transition';
  import ListaPresentes from './ListaPresentes.svelte';
  import Placar from './Placar.svelte';
  import PlacarManual from './PlacarManual.svelte';
  import LinhaDoTempo from './LinhaDoTempo.svelte';

  let {
    quadra,
    eu,
    participantes = [],
    estadoPartida = null,
    linhaDoTempo = [],
    wsConectado = false,
    onMarcarPonto = () => {},
    onDesfazerPonto = () => {},
    onIniciarNovaPartida = () => {},
    onVoltar,
    onAssumirControle = () => {},
    onPromoverControlador = (id) => {},
    onRevogarControlador = (id) => {},
    onAutorizarAdmin = (id) => {},
    operando = false,
    erro = null,
  } = $props();

  const CHAVE_GIRO = 'placar:girado';

  function lerGiroSalvo() {
    if (typeof localStorage === 'undefined') return false;
    try {
      return localStorage.getItem(CHAVE_GIRO) === '1';
    } catch {
      return false;
    }
  }

  let modalLinhaDoTempoAberto = $state(false);
  let prefersReducedMotion = $state(false);
  let copiado = $state(false);

  function copiarCodigo() {
    if (typeof navigator !== 'undefined' && navigator.clipboard && quadra?.id) {
      navigator.clipboard.writeText(quadra.id);
      copiado = true;
      setTimeout(() => { copiado = false; }, 2000);
    }
  }

  // Dimensões da janela física
  let viewportW = $state(typeof window !== 'undefined' ? window.innerWidth : 390);
  let viewportH = $state(typeof window !== 'undefined' ? window.innerHeight : 720);

  // Giro por software: permite usar o celular deitado no cavalete mesmo com a
  // rotação automática travada no iOS. Só faz sentido para quem assiste e
  // enquanto o aparelho estiver fisicamente em pé (retrato).
  const giroInicial = lerGiroSalvo();
  let girado = $state(giroInicial);

  const podeControlar = $derived(
    eu?.papel === 'ADMIN' || eu?.papel === 'CONTROLADOR'
  );
  const ehAdmin = $derived(eu?.papel === 'ADMIN');

  const temControle = $derived(podeControlar && quadra?.controle_id === eu?.id);
  const operador = $derived(participantes.find(p => p.id === quadra?.controle_id)?.apelido || (temControle ? eu?.apelido : 'aguardando atualização'));

  // Se o aparelho/monitor já é fisicamente paisagem (Desktop, tablet ou celular com auto-rotate)
  const paisagemNativa = $derived(viewportW > viewportH);

  // O giro manual por software só se ativa em retrato físico
  const telaGirada = $derived(girado && !podeControlar && !paisagemNativa);

  // Dimensões úteis do placar. Quando a tela está girada por software, os eixos se invertem.
  const telaW = $derived(telaGirada ? viewportH : viewportW);
  const telaH = $derived(telaGirada ? viewportW : viewportH);
  const paisagem = $derived(telaW > 0 && telaW > telaH);

  // Modo Imersivo ativo por padrão para espectadores (US5)
  let modoImersivo = $state(true);
  let timerInatividade = null;

  $effect(() => {
    if (typeof window !== 'undefined') {
      const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
      prefersReducedMotion = mq.matches;
      const handler = (e) => {
        prefersReducedMotion = e.matches;
      };
      mq.addEventListener('change', handler);
      return () => mq.removeEventListener('change', handler);
    }
  });

  // Mede a tela e reage a rotação do aparelho, barra de endereço e giro manual
  $effect(() => {
    if (typeof window === 'undefined') return;

    const medir = () => {
      viewportW = window.innerWidth;
      viewportH = window.innerHeight;
    };

    medir();
    window.addEventListener('resize', medir);
    window.addEventListener('orientationchange', medir);
    window.visualViewport?.addEventListener('resize', medir);

    return () => {
      window.removeEventListener('resize', medir);
      window.removeEventListener('orientationchange', medir);
      window.visualViewport?.removeEventListener('resize', medir);
    };
  });

  // O placar do espectador é tela cheia: libera a largura máxima do #app e
  // trava a rolagem do documento enquanto a tela estiver girada.
  $effect(() => {
    if (typeof document === 'undefined') return;

    const corpo = document.body;
    const espectador = !podeControlar;

    corpo.classList.toggle('placar-espectador', espectador);
    corpo.classList.toggle('placar-girado', telaGirada);

    return () => {
      corpo.classList.remove('placar-espectador', 'placar-girado');
    };
  });

  // Atualiza estado imersivo caso o papel mude dinamicamente
  $effect(() => {
    if (podeControlar) {
      modoImersivo = false;
      if (timerInatividade) clearTimeout(timerInatividade);
    }
  });

  function alternarGiro() {
    girado = !girado;
    try {
      localStorage.setItem(CHAVE_GIRO, girado ? '1' : '0');
    } catch {}
  }

  // Gerencia a revelação dos controles e retorno ao modo imersivo após 3s (US5)
  function tratarInteracaoUsuario(event) {
    if (podeControlar) return;

    // Se estava em modo imersivo, sai dele
    if (modoImersivo) {
      modoImersivo = false;
    }

    // Reinicia o temporizador de 3 segundos de inatividade
    if (timerInatividade) {
      clearTimeout(timerInatividade);
    }

    timerInatividade = setTimeout(() => {
      // Retorna ao modo imersivo apenas se nenhum modal estiver aberto
      if (!modalLinhaDoTempoAberto) {
        modoImersivo = true;
      }
    }, 3000);
  }

  function handleAbrirLinhaDoTempo() {
    if (timerInatividade) {
      clearTimeout(timerInatividade);
    }
    modalLinhaDoTempoAberto = true;
  }

  function handleFecharLinhaDoTempo() {
    modalLinhaDoTempoAberto = false;
    if (!podeControlar) {
      tratarInteracaoUsuario();
    }
  }

  $effect(() => {
    return () => {
      if (timerInatividade) clearTimeout(timerInatividade);
    };
  });
</script>

<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
<!-- svelte-ignore a11y_click_events_have_key_events -->
<div
  class="sala-container"
  class:em-modo-imersivo={modoImersivo && !podeControlar}
  class:tela-girada={telaGirada}
  style="--tela-w: {telaW}px; --tela-h: {telaH}px;"
  in:fade={{ duration: prefersReducedMotion ? 0 : 200 }}
  onclick={tratarInteracaoUsuario}
  onpointerdown={tratarInteracaoUsuario}
  onkeydown={(e) => {
    if (e.key === 'Enter' || e.key === ' ' || e.key === 'Escape') {
      tratarInteracaoUsuario(e);
    }
  }}
  tabindex="-1"
  role="region"
  aria-label="Quadra de Vôlei"
>
  <!-- Top Bar com Botão Voltar e Status de Conexão -->
  {#if podeControlar || !modoImersivo}
    <header class="sala-header" in:slide={{ duration: prefersReducedMotion ? 0 : 200 }} out:slide={{ duration: prefersReducedMotion ? 0 : 200 }}>
      <button
        type="button"
        class="btn-voltar"
        onclick={onVoltar}
        aria-label="Voltar para a lista de quadras"
      >
        <span class="seta">←</span>
        <span>Quadras</span>
      </button>

      <div class="header-acoes">
        {#if !podeControlar && !paisagemNativa}
          <button
            type="button"
            class="btn-girar"
            class:ativo={girado}
            onclick={alternarGiro}
            aria-pressed={girado}
            aria-label={girado
              ? 'Voltar o placar para retrato'
              : 'Girar o placar para paisagem'}
          >
            <span class="girar-icone">⟳</span>
            <span class="girar-texto">{girado ? 'Retrato' : 'Paisagem'}</span>
          </button>
        {/if}

        <div class="ws-status">
          <span
            class="status-dot {wsConectado ? 'status-online' : 'status-offline'}"
          ></span>
          <span class="ws-text">{wsConectado ? 'Ao vivo' : 'Conectando...'}</span>
        </div>
      </div>
    </header>

    <!-- Quadra Title & Meu Perfil -->
    <section class="quadra-hero" in:slide={{ duration: prefersReducedMotion ? 0 : 200 }} out:slide={{ duration: prefersReducedMotion ? 0 : 200 }}>
      <!-- Banner com Código de 5 Dígitos da Sala -->
      <div class="codigo-sala-destaque">
        <div class="codigo-sala-info">
          <span class="codigo-sala-label">CÓDIGO DA SALA</span>
          <span class="codigo-sala-num">{quadra.id}</span>
        </div>
        <button
          type="button"
          class="btn-copiar-pin"
          onclick={copiarCodigo}
          title="Copiar código da sala"
        >
          {copiado ? '✓ Copiado!' : '📋 Copiar'}
        </button>
      </div>

      <div class="quadra-title-row">
        <h2 class="quadra-title">{quadra.nome}</h2>
        <span class="quadra-tag">
          🏟️ {quadra.arena_nome ? quadra.arena_nome + ' • ' : ''}Ativa
        </span>
      </div>

      <div class="meu-perfil-card">
        <div class="meu-perfil-info">
          <span class="label-voce">Você está conectado como:</span>
          <span class="meu-apelido">{eu?.apelido || 'Participante'}</span>
        </div>
        <span class="badge {eu?.papel === 'ADMIN' ? 'badge-admin' : eu?.papel === 'CONTROLADOR' ? 'badge-controlador' : 'badge-espectador'}">
          {eu?.papel || 'ESPECTADOR'}
        </span>
      </div>
    </section>
  {/if}

  <div class="controle-painel" aria-live="polite">
    {#key quadra?.controle_id}
      <span in:fade={{ duration: prefersReducedMotion ? 0 : 180 }}>Controle: <strong>{operador}</strong>{temControle ? ' (você)' : ''}</span>
    {/key}
    {#if podeControlar && !temControle}
      <button class="btn-assumir" disabled={!wsConectado || operando} onclick={onAssumirControle}>Assumir o controle</button>
    {/if}
    {#if !wsConectado}<span role="status">Reconectando… aguarde a atualização.</span>{/if}
    {#if erro}<p role="alert">{erro}</p>{/if}
  </div>

  <!-- Exibição do Placar -->
  {#if !estadoPartida}
    <p role="status">Carregando placar…</p>
  {:else if podeControlar}
    <!-- Placar do Controlador com Botões Grandes de Marcação e Desfazer -->
    <Placar
      {estadoPartida}
      podeControlar={temControle}
      desabilitado={!wsConectado || operando}
      {onMarcarPonto}
      {onDesfazerPonto}
      {onIniciarNovaPartida}
      onAbrirLinhaDoTempo={handleAbrirLinhaDoTempo}
    />
  {:else}
    <!-- Placar Dobrável Manual Retrô do Espectador (US5) -->
    <PlacarManual
      {estadoPartida}
      {quadra}
      {prefersReducedMotion}
      {modoImersivo}
      {paisagem}
      onAbrirLinhaDoTempo={handleAbrirLinhaDoTempo}
    />
  {/if}

  <!-- Modal/Gaveta da Linha do Tempo (CV1.DS4.US1) -->
  {#if modalLinhaDoTempoAberto}
    <LinhaDoTempo
      {prefersReducedMotion}
      itens={linhaDoTempo}
      equipeA={estadoPartida?.equipe_a || 'Equipe A'}
      equipeB={estadoPartida?.equipe_b || 'Equipe B'}
      pontosA={estadoPartida?.pontos_a ?? 0}
      pontosB={estadoPartida?.pontos_b ?? 0}
      onFechar={handleFecharLinhaDoTempo}
    />
  {/if}

  <!-- Lista de Participantes em Tempo Real (oculta em modo imersivo) -->
  {#if podeControlar || !modoImersivo}
    <div in:slide={{ duration: prefersReducedMotion ? 0 : 200 }} out:slide={{ duration: prefersReducedMotion ? 0 : 200 }}>
      <ListaPresentes
        {prefersReducedMotion}
        {participantes}
        euId={eu?.id}
        podeAutorizar={ehAdmin}
        desabilitado={!wsConectado || operando}
        {onPromoverControlador}
        {onRevogarControlador}
        {onAutorizarAdmin}
      />
    </div>
  {/if}
</div>

<style>
  .controle-painel { display: flex; align-items: center; justify-content: center; flex-wrap: wrap; gap: 12px; padding: 10px; color: var(--text-primary); }
  .controle-painel p { color: #fca5a5; width: 100%; text-align: center; }
  .btn-assumir { min-height: 48px; padding: 10px 20px; border: 0; border-radius: 10px; color: white; background: #0369a1; font-weight: 700; cursor: pointer; }
  .btn-assumir:disabled { opacity: .5; cursor: not-allowed; }

  .sala-container {
    padding: max(18px, env(safe-area-inset-top))
      max(20px, env(safe-area-inset-right))
      max(32px, env(safe-area-inset-bottom))
      max(20px, env(safe-area-inset-left));
    display: flex;
    flex-direction: column;
    gap: 22px;
    min-height: 100vh;
    min-height: 100dvh;
    transition: padding 0.25s ease;
  }

  /*
   * Giro por software: o quadro inteiro vira 90°, então o celular pode ficar
   * deitado no cavalete mesmo com a rotação do iOS travada. As medidas vêm do
   * SalaQuadra já com os eixos invertidos.
   */
  .sala-container.tela-girada {
    position: fixed;
    top: 0;
    left: 0;
    width: var(--tela-w);
    height: var(--tela-h);
    min-height: 0;
    transform-origin: 0 0;
    transform: rotate(90deg) translate(0, -100%);
    overflow-y: auto;
    overflow-x: hidden;
    z-index: 5;
  }

  .sala-container.em-modo-imersivo {
    padding: max(8px, env(safe-area-inset-top))
      max(6px, env(safe-area-inset-right))
      max(8px, env(safe-area-inset-bottom))
      max(6px, env(safe-area-inset-left));
    justify-content: center;
    cursor: pointer;
    gap: 0;
    height: var(--tela-h);
    min-height: 0;
    overflow: hidden;
  }

  .sala-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    flex: 0 0 auto;
  }

  .header-acoes {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .btn-voltar {
    background: transparent;
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.95rem;
    padding: 8px 10px;
    border-radius: var(--radius-sm);
  }

  .btn-voltar:hover {
    color: var(--text-primary);
    background: var(--bg-surface);
  }

  .seta {
    font-size: 1.1rem;
  }

  /* Alternador de orientação do placar */
  .btn-girar {
    display: flex;
    align-items: center;
    gap: 6px;
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    touch-action: manipulation;
    transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
  }

  .btn-girar:hover {
    color: var(--text-primary);
    border-color: rgba(255, 255, 255, 0.2);
  }

  .btn-girar.ativo {
    color: var(--accent-orange);
    border-color: var(--border-active);
    background: rgba(249, 115, 22, 0.12);
  }

  .girar-icone {
    font-size: 0.95rem;
    line-height: 1;
  }

  .ws-status {
    display: flex;
    align-items: center;
    gap: 6px;
    background: var(--bg-surface);
    padding: 6px 12px;
    border-radius: 999px;
    border: 1px solid var(--border-color);
  }

  .ws-text {
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--text-secondary);
  }

  .quadra-hero {
    display: flex;
    flex-direction: column;
    gap: 14px;
    flex: 0 0 auto;
  }

  .codigo-sala-destaque {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #0f172a;
    border: 2px solid #0284c7;
    border-radius: 14px;
    padding: 10px 16px;
    box-shadow: 0 4px 14px rgba(2, 132, 199, 0.25);
  }

  .codigo-sala-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .codigo-sala-label {
    font-size: 0.65rem;
    font-weight: 700;
    color: #94a3b8;
    letter-spacing: 0.08em;
  }

  .codigo-sala-num {
    font-size: 1.6rem;
    font-weight: 900;
    color: #38bdf8;
    letter-spacing: 0.15em;
    line-height: 1;
  }

  .btn-copiar-pin {
    background: #1e293b;
    border: 1px solid #334155;
    color: #f1f5f9;
    padding: 0.45rem 0.85rem;
    font-size: 0.85rem;
    font-weight: 600;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .btn-copiar-pin:hover {
    background: #0284c7;
    border-color: #0284c7;
    color: #ffffff;
  }

  .quadra-tag {
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--accent-orange);
    letter-spacing: 0.05em;
  }

  .quadra-title {
    font-size: 1.7rem;
    font-weight: 800;
    color: #ffffff;
    line-height: 1.2;
  }

  .meu-perfil-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 14px 18px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .meu-perfil-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .label-voce {
    font-size: 0.78rem;
    color: var(--text-muted);
  }

  .meu-apelido {
    font-size: 1.15rem;
    font-weight: 700;
    color: #ffffff;
  }

  /* Com a tela girada o espaço vertical é curto: enxuga o cabeçalho revelado */
  .tela-girada .quadra-title {
    font-size: 1.25rem;
  }

  .tela-girada .meu-perfil-card {
    padding: 8px 14px;
  }

  .tela-girada:not(.em-modo-imersivo) {
    gap: 12px;
    padding: 10px 16px 20px 16px;
  }

  @media (max-height: 460px) and (orientation: landscape) {
    .sala-container:not(.em-modo-imersivo) {
      gap: 12px;
      padding: 10px 16px 20px 16px;
    }

    .quadra-title {
      font-size: 1.25rem;
    }

    .meu-perfil-card {
      padding: 8px 14px;
    }
  }
</style>
