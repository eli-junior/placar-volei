<script>
  import { fade, slide } from 'svelte/transition';
  import ModalRelogio from './ModalRelogio.svelte';
  import ListaPresentes from './ListaPresentes.svelte';
  import Placar from './Placar.svelte';
  import PlacarManual from './PlacarManual.svelte';
  import LinhaDoTempo from './LinhaDoTempo.svelte';
  import Icone from './Icone.svelte';
  import ModalCompartilhar from './ModalCompartilhar.svelte';
  import ModalConfigurarPartida from './ModalConfigurarPartida.svelte';
  import ModalCelebracaoVitoria from './ModalCelebracaoVitoria.svelte';
  import { ehDonoDoRelogio } from '../lib/relogio.js';

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
    onConfigurarPartida = () => {},
    onVoltar,
    onAssumirControle = () => {},
    onPromoverControlador = (id) => {},
    onRevogarControlador = (id) => {},
    onAutorizarAdmin = (id) => {},
    onPassarControle = (id) => {},
    operando = false,
    pendentes = 0,
    erro = null,
  } = $props();

  const CHAVE_GIRO = 'placar:girado';
  const CHAVE_INVERSAO_BASE = 'placar:lados_invertidos:';
  const CHAVE_TEMA = 'placar:tema';

  function lerTemaSalvo() {
    if (typeof localStorage === 'undefined') return false;
    try {
      return localStorage.getItem(CHAVE_TEMA) === 'sol';
    } catch {
      return false;
    }
  }

  let temaSol = $state(false);

  $effect(() => {
    temaSol = lerTemaSalvo();
    if (typeof document !== 'undefined') {
      if (temaSol) {
        document.documentElement.setAttribute('data-tema', 'sol');
      } else {
        document.documentElement.removeAttribute('data-tema');
      }
    }
  });

  function alternarTema() {
    temaSol = !temaSol;
    if (typeof document !== 'undefined') {
      if (temaSol) {
        document.documentElement.setAttribute('data-tema', 'sol');
      } else {
        document.documentElement.removeAttribute('data-tema');
      }
    }
    if (typeof localStorage !== 'undefined') {
      try {
        localStorage.setItem(CHAVE_TEMA, temaSol ? 'sol' : 'padrao');
      } catch {}
    }
  }

  function lerGiroSalvo() {
    if (typeof localStorage === 'undefined') return false;
    try {
      return localStorage.getItem(CHAVE_GIRO) === '1';
    } catch {
      return false;
    }
  }

  function lerInversaoSalva(quadraId) {
    if (typeof localStorage === 'undefined' || !quadraId) return false;
    try {
      return localStorage.getItem(CHAVE_INVERSAO_BASE + quadraId) === '1';
    } catch {
      return false;
    }
  }

  let ladosInvertidos = $state(false);

  $effect(() => {
    if (quadra?.id) {
      ladosInvertidos = lerInversaoSalva(quadra.id);
    }
  });

  function alternarLados() {
    ladosInvertidos = !ladosInvertidos;
    if (quadra?.id && typeof localStorage !== 'undefined') {
      try {
        localStorage.setItem(CHAVE_INVERSAO_BASE + quadra.id, ladosInvertidos ? '1' : '0');
      } catch {}
    }
  }

  let modalRelogioAberto = $state(false);
  let modalLinhaDoTempoAberto = $state(false);
  let modalCompartilharAberto = $state(false);
  let modalConfigAberto = $state(false);
  let isReinicioConfig = $state(false);
  let modalCelebracaoAberto = $state(false);
  let celebracaoExibidaPartidaId = $state(null);
  let prefersReducedMotion = $state(false);
  let copiado = $state(false);

  // Celebração de Vitória Automática (CV2.DS4.US1)
  $effect(() => {
    if (estadoPartida?.encerrada && estadoPartida?.vencedor && quadra?.partida_id) {
      if (celebracaoExibidaPartidaId !== quadra.partida_id) {
        celebracaoExibidaPartidaId = quadra.partida_id;
        modalCelebracaoAberto = true;
      }
    }
  });

  // Wake Lock API (CV2.DS2.US3)
  let wakeLockSentinel = null;

  async function requisitarWakeLock() {
    if (typeof navigator === 'undefined' || !navigator.wakeLock || estadoPartida?.encerrada) return;
    try {
      if (!wakeLockSentinel || wakeLockSentinel.released) {
        wakeLockSentinel = await navigator.wakeLock.request('screen');
      }
    } catch {
      // Navegadores podem recusar Wake Lock se bateria baixa ou sem foco
    }
  }

  function liberarWakeLock() {
    if (wakeLockSentinel && !wakeLockSentinel.released) {
      wakeLockSentinel.release().catch(() => {});
      wakeLockSentinel = null;
    }
  }

  $effect(() => {
    if (typeof document === 'undefined') return;

    if (!estadoPartida?.encerrada) {
      requisitarWakeLock();
    } else {
      liberarWakeLock();
    }

    const onVisibilityChange = () => {
      if (document.visibilityState === 'visible' && !estadoPartida?.encerrada) {
        requisitarWakeLock();
      }
    };

    document.addEventListener('visibilitychange', onVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', onVisibilityChange);
      liberarWakeLock();
    };
  });

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
  // O relógio é pessoal do eli nesta fase; para os demais, só um aviso.
  let avisoRelogio = $state(false);
  let avisoRelogioTimer = null;
  function abrirRelogio() {
    if (ehDonoDoRelogio(eu?.apelido)) {
      modalRelogioAberto = true;
      return;
    }
    avisoRelogio = true;
    clearTimeout(avisoRelogioTimer);
    avisoRelogioTimer = setTimeout(() => { avisoRelogio = false; }, 2500);
  }

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
      if (
        !modalRelogioAberto &&
        !modalLinhaDoTempoAberto &&
        !modalCompartilharAberto &&
        !modalConfigAberto &&
        !modalCelebracaoAberto
      ) {
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
        <button
          type="button"
          class="btn-tema-header"
          onclick={alternarTema}
          aria-label={temaSol ? 'Ativar modo escuro' : 'Ativar modo sol de alto contraste'}
          title={temaSol ? 'Modo Escuro' : 'Modo Sol (Alto Contraste)'}
        >
          <Icone nome={temaSol ? 'lua' : 'sol'} tamanho="1.15em" />
        </button>

        <button
          type="button"
          class="btn-compartilhar-header"
          onclick={() => { modalCompartilharAberto = true; }}
          aria-label="Compartilhar sala"
          title="Compartilhar sala e QR Code"
        >
          <Icone nome="compartilhar" tamanho="1.1em" />
        </button>

        {#if podeControlar}
          <button
            type="button"
            class="btn-config-header"
            onclick={abrirRelogio}
            aria-label="Vincular ou revogar meu relógio"
            title="Relógio"
          >
            <Icone nome="relogio" tamanho="1.15em" />
          </button>
          <button
            type="button"
            class="btn-config-header"
            onclick={() => { modalConfigAberto = true; isReinicioConfig = false; }}
            aria-label="Configurar duplas e regras da partida"
            title="Configurações da partida"
          >
            <Icone nome="engrenagem" tamanho="1.15em" />
          </button>
        {/if}

        <button
          type="button"
          class="btn-inverter-lados-header"
          class:ativo={ladosInvertidos}
          onclick={alternarLados}
          aria-pressed={ladosInvertidos}
          title="Inverter lados das equipes na sua tela"
          aria-label="Inverter lados das equipes"
        >
          <span class="inverter-icone">⇄</span>
          <span class="inverter-texto">{ladosInvertidos ? 'Lados Invertidos' : 'Inverter Lados'}</span>
        </button>

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

    <!-- O controlador mantém os dados operacionais; o espectador recebe
         contexto compacto dentro do próprio placar. -->
    {#if podeControlar}
    <section class="quadra-hero" in:slide={{ duration: prefersReducedMotion ? 0 : 200 }} out:slide={{ duration: prefersReducedMotion ? 0 : 200 }}>
      <!-- Banner com Código de 5 Dígitos da Sala -->
      <div class="codigo-sala-destaque">
        <div class="codigo-sala-info">
          <span class="codigo-sala-label">CÓDIGO DA SALA</span>
          <span class="codigo-sala-num">{quadra.id}</span>
        </div>
        <div class="codigo-sala-botoes">
          <button
            type="button"
            class="btn-copiar-pin"
            onclick={copiarCodigo}
            title="Copiar código da sala"
          >
            {copiado ? '✓ Copiado!' : '📋 Copiar'}
          </button>
          <button
            type="button"
            class="btn-compartilhar-pin"
            onclick={() => { modalCompartilharAberto = true; }}
            title="Abrir QR Code e Compartilhar"
          >
            <Icone nome="compartilhar" tamanho="1em" />
            <span>QR</span>
          </button>
        </div>
      </div>

      <div class="quadra-title-row">
        <h2 class="quadra-title">{quadra.nome}</h2>
        <div class="quadra-tags-group">
          {#if estadoPartida}
            <span class="regra-tag">
              🎯 Até {estadoPartida.alvo} pts • {estadoPartida.vantagem ? 'Vantagem' : 'Sem vantagem'}{estadoPartida.teto ? ` • Teto ${estadoPartida.teto}` : ''}
            </span>
          {/if}
          {#if podeControlar}
            <button
              type="button"
              class="btn-ajustar-regras"
              onclick={() => { modalConfigAberto = true; isReinicioConfig = false; }}
              title="Ajustar duplas e regras da partida"
            >
              <Icone nome="regras" tamanho="0.95em" />
              <span>Duplas & Regras</span>
            </button>
          {/if}
          <span class="quadra-tag">
            🏟️ Sala Ativa
          </span>
        </div>
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
  {/if}

  {#if podeControlar || avisoRelogio || !wsConectado || erro}
  <div class="controle-painel" aria-live="polite">
    {#if avisoRelogio}
      <span class="aviso-em-breve" role="status" transition:fade={{ duration: prefersReducedMotion ? 0 : 150 }}>Em breve…</span>
    {/if}
    {#key quadra?.controle_id}
      <span in:fade={{ duration: prefersReducedMotion ? 0 : 180 }}>Controle: <strong>{operador}</strong>{temControle ? ' (você)' : ''}</span>
    {/key}
    {#if podeControlar && !temControle}
      <button class="btn-assumir" disabled={!wsConectado || operando} onclick={onAssumirControle}>Assumir o controle</button>
    {/if}
    {#if !wsConectado}
      <span class="chip-reconectando" role="status">
        <span class="chip-girando" aria-hidden="true">⟳</span>
        Sem conexão — reconectando. Os controles do placar voltam sozinhos.
      </span>
    {/if}
    {#if erro}<p role="alert">{erro}</p>{/if}
  </div>
  {/if}

  <!-- Exibição do Placar -->
  {#if !estadoPartida}
    <p role="status">Carregando placar…</p>
  {:else if podeControlar}
    <!-- Placar do Controlador com Botões Grandes de Marcação e Desfazer -->
    <!--
      `desabilitado` significa "não dá para agir" (socket caído) e não "tem
      comando em voo": enquanto há envio pendente os botões continuam ativos
      para que o toque seguinte entre na fila em vez de ser descartado.
    -->
    <Placar
      {estadoPartida}
      podeControlar={temControle}
      desabilitado={!wsConectado}
      enviando={operando}
      {pendentes}
      {ladosInvertidos}
      onAlternarLados={alternarLados}
      {onMarcarPonto}
      {onDesfazerPonto}
      onIniciarNovaPartida={() => {
        modalConfigAberto = true;
        isReinicioConfig = true;
      }}
      onAbrirConfiguracao={() => {
        modalConfigAberto = true;
        isReinicioConfig = false;
      }}
      onAbrirLinhaDoTempo={handleAbrirLinhaDoTempo}
      onAbrirCompartilhar={() => { modalCompartilharAberto = true; }}
    />
  {:else}
    <!-- Painel esportivo responsivo do espectador -->
    <div class="placar-espectador-wrapper">
    <PlacarManual
      {estadoPartida}
      {quadra}
      {prefersReducedMotion}
      {modoImersivo}
      {paisagem}
      {ladosInvertidos}
      onAlternarLados={alternarLados}
      onAbrirLinhaDoTempo={handleAbrirLinhaDoTempo}
    />
    </div>
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

  <!-- Modal de Compartilhamento com QR Code SVG Nativo (CV2.DS4.US2) -->
  {#if modalRelogioAberto}
    <ModalRelogio {quadra} movimentoReduzido={prefersReducedMotion} onFechar={() => { modalRelogioAberto = false; }} />
  {/if}

  {#if modalCompartilharAberto}
    <ModalCompartilhar
      {quadra}
      movimentoReduzido={prefersReducedMotion}
      onFechar={() => { modalCompartilharAberto = false; }}
    />
  {/if}

  <!-- Modal de Configurar Duplas & Regras da Partida (Admin / In-Game / Reinício) -->
  {#if modalConfigAberto}
    <ModalConfigurarPartida
      {estadoPartida}
      isReinicio={isReinicioConfig}
      movimentoReduzido={prefersReducedMotion}
      submetendo={operando}
      onFechar={() => { modalConfigAberto = false; }}
      onSalvar={(dados) => {
        if (isReinicioConfig) {
          onIniciarNovaPartida(dados);
        } else {
          onConfigurarPartida(dados);
        }
        modalConfigAberto = false;
        modalCelebracaoAberto = false;
      }}
    />
  {/if}

  <!-- Modal de Celebração de Vitória Memorável (CV2.DS4.US1) -->
  {#if modalCelebracaoAberto && estadoPartida?.encerrada && estadoPartida?.vencedor}
    <ModalCelebracaoVitoria
      {estadoPartida}
      podeControlar={temControle}
      movimentoReduzido={prefersReducedMotion}
      onNovaPartida={() => {
        modalCelebracaoAberto = false;
        modalConfigAberto = true;
        isReinicioConfig = true;
      }}
      onCompartilhar={() => {
        modalCelebracaoAberto = false;
        modalCompartilharAberto = true;
      }}
      onFechar={() => { modalCelebracaoAberto = false; }}
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
        controleId={quadra?.controle_id}
        {onPassarControle}
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
  .controle-painel p { color: var(--estado-erro-suave); width: 100%; text-align: center; }
  .aviso-em-breve {
    padding: 4px 10px;
    border-radius: 999px;
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    font-weight: 600;
  }

  .chip-reconectando {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 700;
    color: #fde68a;
    background: rgba(245, 158, 11, 0.14);
    border: 1px solid rgba(245, 158, 11, 0.45);
  }
  .chip-girando { display: inline-block; animation: girar-reconexao 1.1s linear infinite; }
  @keyframes girar-reconexao { to { transform: rotate(360deg); } }
  @media (prefers-reduced-motion: reduce) {
    .chip-girando { animation: none; }
  }
  .btn-assumir { min-height: 48px; padding: 10px 20px; border: 0; border-radius: 10px; color: white; background: var(--acento-info-ativo); font-weight: 700; cursor: pointer; }
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

  .placar-espectador-wrapper {
    display: flex;
    width: 100%;
    min-height: 0;
  }

  .em-modo-imersivo .placar-espectador-wrapper {
    flex: 1 1 auto;
    height: 100%;
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

  .btn-tema-header,
  .btn-compartilhar-header,
  .btn-config-header {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    min-width: 44px;
    min-height: 44px;
    box-sizing: border-box;
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    border-radius: var(--radius-circular);
    cursor: pointer;
    touch-action: manipulation;
    transition: all 0.15s ease;
  }

  .btn-tema-header:hover,
  .btn-compartilhar-header:hover,
  .btn-config-header:hover {
    color: var(--text-primary);
    border-color: rgba(var(--veu), 0.25);
    background: var(--bg-card);
  }

  /* Alternador de inversão de lados e orientação */
  .btn-inverter-lados-header,
  .btn-girar {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    padding: 6px 14px;
    min-height: 44px;
    box-sizing: border-box;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    touch-action: manipulation;
    transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
  }

  .btn-inverter-lados-header:hover,
  .btn-girar:hover {
    color: var(--text-primary);
    border-color: rgba(var(--veu), 0.2);
  }

  .btn-inverter-lados-header.ativo,
  .btn-girar.ativo {
    color: var(--accent-orange);
    border-color: var(--border-active);
    background: rgba(249, 115, 22, 0.12);
  }

  .inverter-icone,
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
    background: var(--fundo-base);
    border: 2px solid var(--acento-info-forte);
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
    color: var(--texto-suave);
    letter-spacing: 0.08em;
  }

  .codigo-sala-num {
    font-size: 1.6rem;
    font-weight: 900;
    color: var(--acento-info);
    letter-spacing: 0.15em;
    line-height: 1;
  }

  .codigo-sala-botoes {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .btn-copiar-pin {
    background: var(--fundo-superficie);
    border: 1px solid var(--acao-secundaria);
    color: var(--texto-forte);
    padding: 0.5rem 1rem;
    min-height: 44px;
    box-sizing: border-box;
    font-size: 0.85rem;
    font-weight: 600;
    border-radius: 8px;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    transition: all 0.15s ease;
  }

  .btn-copiar-pin:hover {
    background: var(--acento-info-forte);
    border-color: var(--acento-info-forte);
    color: #ffffff;
  }

  .btn-compartilhar-pin {
    background: rgba(2, 132, 199, 0.2);
    border: 1px solid var(--acento-info-forte);
    color: var(--acento-info);
    padding: 0.5rem 1rem;
    min-height: 44px;
    box-sizing: border-box;
    font-size: 0.85rem;
    font-weight: 600;
    border-radius: 8px;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    transition: all 0.15s ease;
  }

  .btn-compartilhar-pin:hover {
    background: var(--acento-info-forte);
    color: #ffffff;
  }

  .quadra-tags-group {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }

  .regra-tag {
    font-size: 0.78rem;
    font-weight: 700;
    color: var(--acento-info);
    background: rgba(56, 189, 248, 0.12);
    border: 1px solid rgba(56, 189, 248, 0.3);
    padding: 4px 8px;
    border-radius: 6px;
    letter-spacing: 0.02em;
  }

  .btn-ajustar-regras {
    background: rgba(14, 165, 233, 0.15);
    border: 1px solid rgba(56, 189, 248, 0.4);
    color: var(--acento-info);
    padding: 6px 12px;
    min-height: 40px;
    box-sizing: border-box;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 700;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    transition: all 0.15s ease;
  }

  .btn-ajustar-regras:hover {
    background: rgba(14, 165, 233, 0.3);
    border-color: var(--acento-info);
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
    color: var(--texto-contraste);
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
    color: var(--texto-contraste);
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
