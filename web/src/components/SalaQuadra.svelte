<script>
  import { copiarTexto } from '../lib/areaDeTransferencia.js';
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
  import { ultimoPontoDesfazivel, descreverPosse } from '../lib/controle.js';
  import MenuSala from './MenuSala.svelte';
  import {
    suportaTelaCheia,
    estaEmTelaCheia,
    solicitarTelaCheia,
    sairDaTelaCheia,
    observarTelaCheia,
    podeOcultarControles,
    MENSAGEM_TELA_CHEIA,
  } from '../lib/telaCheia.js';

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
  // '' | 'ok' | 'falhou': só diz "copiado" quando a cópia deu certo.
  let copiado = $state('');

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

  async function copiarCodigo() {
    if (!quadra?.id) return;
    copiado = (await copiarTexto(quadra.id)) ? 'ok' : 'falhou';
    setTimeout(() => { copiado = ''; }, 2000);
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
  const posse = $derived(
    descreverPosse({ temControle, ehAdmin, operador: participantes.find(p => p.id === quadra?.controle_id)?.apelido, conectado: wsConectado })
  );
  const ultimoPonto = $derived(ultimoPontoDesfazivel(linhaDoTempo));
  let menuAberto = $state(false);

  // Local único das ações secundárias (CV4.DS3.US1/US2). Cada papel vê só o
  // que pode fazer; o que já tem lugar próprio na tela não se repete aqui.
  const acoesDoMenu = $derived([
    { rotulo: 'Compartilhar e QR', icone: 'compartilhar', acao: () => { modalCompartilharAberto = true; } },
    ...(podeControlar
      ? [
          { rotulo: 'Duplas e regras', icone: 'engrenagem', acao: () => { modalConfigAberto = true; isReinicioConfig = false; } },
          { rotulo: 'Linha do tempo', icone: 'linhaDoTempo', acao: handleAbrirLinhaDoTempo },
          { rotulo: 'Relógio', icone: 'relogio', acao: abrirRelogio },
        ]
      : []),
    ...(!podeControlar && !paisagemNativa
      ? [{ rotulo: girado ? 'Placar em retrato' : 'Girar para paisagem', icone: 'atualizar', acao: alternarGiro, pressionado: girado, fechaMenu: false }]
      : []),
    { rotulo: temaSol ? 'Modo escuro' : 'Modo sol', icone: temaSol ? 'lua' : 'sol', acao: alternarTema, pressionado: temaSol, fechaMenu: false },
  ]);

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
    corpo.classList.toggle('placar-operador', !espectador);
    corpo.classList.toggle('placar-girado', telaGirada);

    return () => {
      corpo.classList.remove('placar-espectador', 'placar-operador', 'placar-girado');
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

  // Tela cheia do navegador (CV4.DS2.US2): independente da imersão. O estado
  // vem sempre do navegador; nunca presumimos que o pedido deu certo.
  const telaCheiaDisponivel = suportaTelaCheia();
  let telaCheia = $state(estaEmTelaCheia());
  let avisoTelaCheia = $state(null);
  let avisoTelaCheiaTimer = null;

  $effect(() => observarTelaCheia((ativa) => { telaCheia = ativa; }));

  // Sair da sala não deixa a Home presa em tela cheia.
  $effect(() => () => { sairDaTelaCheia(); });

  function avisarTelaCheia(motivo) {
    avisoTelaCheia = MENSAGEM_TELA_CHEIA[motivo];
    clearTimeout(avisoTelaCheiaTimer);
    avisoTelaCheiaTimer = setTimeout(() => { avisoTelaCheia = null; }, 4000);
  }

  // Chamado direto no clique: nenhum `await` antes do pedido, senão o
  // navegador perde a ativação do usuário e recusa.
  function alternarTelaCheia() {
    if (telaCheia) {
      sairDaTelaCheia();
      return;
    }
    solicitarTelaCheia().then((r) => {
      if (!r.ok) avisarTelaCheia(r.motivo);
    });
  }

  function algumModalAberto() {
    return (
      modalRelogioAberto ||
      modalLinhaDoTempoAberto ||
      modalCompartilharAberto ||
      modalConfigAberto ||
      modalCelebracaoAberto ||
      menuAberto
    );
  }

  function focoDeTecladoEmControle() {
    const ativo = typeof document === 'undefined' ? null : document.activeElement;
    if (!ativo || ativo === document.body) return false;
    try {
      return ativo.matches(':focus-visible') && ativo.matches('button, input, select, textarea, a[href]');
    } catch {
      return false;
    }
  }

  function agendarOcultacao() {
    if (timerInatividade) clearTimeout(timerInatividade);
    timerInatividade = setTimeout(() => {
      const livre = podeOcultarControles({
        modalAberto: algumModalAberto(),
        focoDeTeclado: focoDeTecladoEmControle(),
        erroPendente: Boolean(erro) || Boolean(avisoTelaCheia),
      });
      // Algo ainda precisa dos controles: tenta de novo em vez de esconder.
      if (livre) modoImersivo = true;
      else agendarOcultacao();
    }, 3000);
  }

  // O toque que revela os controles não pode acionar o botão que surge sob
  // o dedo: o clique seguinte à revelação é descartado.
  let engolirClique = false;

  function engolirCliqueDeRevelacao(event) {
    if (!engolirClique) return;
    engolirClique = false;
    event.stopPropagation();
    event.preventDefault();
  }

  // Gerencia a revelação dos controles e retorno ao modo imersivo após 3s (US5)
  function tratarInteracaoUsuario(event) {
    if (podeControlar) return;

    if (modoImersivo) {
      modoImersivo = false;
      if (event?.type === 'pointerdown') {
        engolirClique = true;
        setTimeout(() => { engolirClique = false; }, 500);
      }
    }

    agendarOcultacao();
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
  class:em-modo-imersivo={!podeControlar}
  class:operador={podeControlar}
  class:controles-ocultos={modoImersivo && !podeControlar}
  class:tela-girada={telaGirada}
  style="--tela-w: {telaW}px; --tela-h: {telaH}px;"
  in:fade={{ duration: prefersReducedMotion ? 0 : 200 }}
  onclickcapture={engolirCliqueDeRevelacao}
  onclick={tratarInteracaoUsuario}
  onpointerdown={tratarInteracaoUsuario}
  onkeydown={(e) => {
    if (e.key === 'Enter' || e.key === ' ' || e.key === 'Escape' || e.key === 'Tab') {
      tratarInteracaoUsuario(e);
    }
  }}
  tabindex="-1"
  role="region"
  aria-label="Quadra de Vôlei"
>
  <!-- Top Bar com Botão Voltar e Status de Conexão -->
  {#if podeControlar}
    <!-- Operação (CV4.DS3.US1): barra compacta e faixa de posse; o resto das
         ações fica no menu ⋯ para o placar caber sem rolagem. -->
    <header class="barra-operador">
      <button type="button" class="btn-voltar-compacto" onclick={onVoltar} aria-label="Voltar para a lista de quadras">←</button>
      <button type="button" class="chip-codigo" onclick={copiarCodigo} title="Copiar código da sala" aria-label="Copiar código da sala {quadra.id}">
        <strong>#{quadra.id}</strong>
        <span>{copiado === 'ok' ? 'Copiado!' : copiado === 'falhou' ? `Código ${quadra.id}` : quadra.nome}</span>
      </button>
      <div class="ws-status">
        <span class="status-dot {wsConectado ? 'status-online' : 'status-offline'}" aria-hidden="true"></span>
        <span class="ws-text">{wsConectado ? 'Ao vivo' : 'Conectando...'}</span>
      </div>
    </header>

    <div class="faixa-posse" class:minha={temControle}>
      <span class="pino" aria-hidden="true"></span>
      <!-- Anúncio da posse fora do {#key}: a região viva não pode nascer a
           cada troca, e só o texto da posse é lido (CV5.DS4.US2). -->
      <span class="sr-only" aria-live="polite">{posse.titulo}. {posse.detalhe}</span>
      {#key quadra?.controle_id}
        <div class="posse-texto" aria-hidden="true" in:fade={{ duration: prefersReducedMotion ? 0 : 180 }}>
          <strong>{posse.titulo}</strong>
          <small>{posse.detalhe}</small>
        </div>
      {/key}
      <span class="selo-papel">{eu?.papel}</span>
      {#if posse.podeAssumir}
        <button class="btn-assumir" disabled={!wsConectado || operando} onclick={onAssumirControle}>Assumir</button>
      {/if}
    </div>
  {:else if !modoImersivo}
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
        {#if !podeControlar && telaCheiaDisponivel}
          <button
            type="button"
            class="btn-tela-cheia"
            class:ativo={telaCheia}
            onclick={alternarTelaCheia}
            aria-pressed={telaCheia}
            aria-label={telaCheia ? 'Sair da tela cheia' : 'Tela cheia'}
            title={telaCheia ? 'Sair da tela cheia' : 'Tela cheia'}
          >
            <Icone nome={telaCheia ? 'recolher' : 'expandir'} tamanho="1.15em" />
          </button>
        {/if}

        <button
          type="button"
          class="btn-tela-cheia"
          onclick={() => { menuAberto = true; }}
          aria-haspopup="dialog"
          aria-label="Mais ações: compartilhar, girar, tema e presentes"
          title="Mais ações"
        >
          <span aria-hidden="true">⋯</span>
        </button>

        <div class="ws-status">
          <span
            class="status-dot {wsConectado ? 'status-online' : 'status-offline'}"
            aria-hidden="true"
          ></span>
          <span class="ws-text">{wsConectado ? 'Ao vivo' : 'Conectando...'}</span>
        </div>
      </div>
    </header>

  {/if}

  <!-- Sempre montado (CV5.DS4.US2): região viva que nasce já preenchida
       costuma não ser anunciada pelo leitor de tela. -->
  <div class="controle-painel" class:vazio={!(avisoRelogio || avisoTelaCheia || !wsConectado || erro)} aria-live="polite">
    {#if avisoTelaCheia}
      <span class="aviso-em-breve" role="status" transition:fade={{ duration: prefersReducedMotion ? 0 : 150 }}>{avisoTelaCheia}</span>
    {/if}
    {#if avisoRelogio}
      <span class="aviso-em-breve" role="status" transition:fade={{ duration: prefersReducedMotion ? 0 : 150 }}>Em breve…</span>
    {/if}
    {#if !wsConectado}
      <span class="chip-reconectando" role="status">
        <span class="chip-girando" aria-hidden="true">⟳</span>
        Sem conexão — reconectando. Os controles do placar voltam sozinhos.
      </span>
    {/if}
    {#if erro}<p role="alert">{erro}</p>{/if}
  </div>

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
      temaPlacar={quadra?.tema_placar || 'esportivo'}
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
      {ultimoPonto}
      onAbrirMenu={() => { menuAberto = true; }}
      onAbrirCompartilhar={() => { modalCompartilharAberto = true; }}
    />
  {:else}
    <!-- Painel esportivo responsivo do espectador -->
    <div class="placar-espectador-wrapper">
    <PlacarManual
      {estadoPartida}
      {quadra}
      temaPlacar={quadra?.tema_placar || 'esportivo'}
      {prefersReducedMotion}
      modoImersivo={true}
      controlesOcultos={modoImersivo}
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
      temaPlacar={quadra?.tema_placar || 'esportivo'}
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

  {#if menuAberto}
    <MenuSala acoes={acoesDoMenu} movimentoReduzido={prefersReducedMotion} onFechar={() => { menuAberto = false; }}>
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
    </MenuSala>
  {/if}
</div>

<style>
  /* Operação sem rolagem (CV4.DS3.US1). */
  .sala-container.operador {
    height: 100vh;
    height: 100dvh;
    min-height: 0;
    gap: 8px;
    padding: max(8px, env(safe-area-inset-top))
      max(8px, env(safe-area-inset-right))
      max(8px, env(safe-area-inset-bottom))
      max(8px, env(safe-area-inset-left));
    overflow: hidden;
  }

  .barra-operador { display: flex; align-items: center; gap: 8px; min-width: 0; flex: 0 0 auto; }
  .btn-voltar-compacto,
  .chip-codigo {
    min-height: 44px;
    border: 1px solid var(--border-color);
    border-radius: 12px;
    background: var(--bg-surface);
    color: var(--text-secondary);
    cursor: pointer;
  }
  .btn-voltar-compacto { width: 44px; flex: 0 0 44px; font-size: 1.1rem; }
  .chip-codigo { display: flex; align-items: baseline; gap: 8px; min-width: 0; padding: 0 12px; }
  .chip-codigo strong { font-family: var(--fonte-numeros); font-size: 1.35rem; letter-spacing: .04em; color: var(--text-primary); }
  .chip-codigo span { overflow: hidden; font-size: .78rem; text-overflow: ellipsis; white-space: nowrap; }
  .barra-operador .ws-status { margin-left: auto; }

  .faixa-posse {
    display: flex;
    align-items: center;
    gap: 10px;
    min-height: 52px;
    padding: 6px 8px 6px 12px;
    border: 1px solid var(--border-color);
    border-radius: 12px;
    background: var(--bg-surface);
    flex: 0 0 auto;
  }
  .faixa-posse .pino { width: 10px; height: 10px; flex: 0 0 10px; border-radius: 50%; background: var(--text-secondary); }
  .faixa-posse.minha .pino { background: var(--estado-sucesso, #34d399); }
  .posse-texto { display: flex; flex-direction: column; min-width: 0; line-height: 1.25; color: var(--text-primary); }
  .posse-texto small { color: var(--text-secondary); font-size: .75rem; }
  .selo-papel {
    margin-left: auto;
    padding: 3px 8px;
    border: 1px solid var(--border-color);
    border-radius: 999px;
    color: var(--text-secondary);
    font-size: .68rem;
    font-weight: 800;
    letter-spacing: .06em;
  }
  .faixa-posse .btn-assumir { min-height: 44px; padding: 0 14px; }

  .controle-painel { display: flex; align-items: center; justify-content: center; flex-wrap: wrap; gap: 12px; padding: 10px; color: var(--text-primary); }
  .controle-painel.vazio { padding: 0; }
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

  /*
   * Espectador (CV4.DS2.US2): o palco do placar é fixo. Cabeçalho e presentes
   * aparecem sobre ele, para que revelar ou esconder os controles não mova os
   * pontos.
   */
  .sala-container.em-modo-imersivo {
    position: relative;
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

  .em-modo-imersivo:not(.controles-ocultos) {
    cursor: auto;
  }

  .em-modo-imersivo > .sala-header {
    position: absolute;
    z-index: 6;
    top: max(8px, env(safe-area-inset-top));
    left: max(6px, env(safe-area-inset-left));
    right: max(6px, env(safe-area-inset-right));
    padding: 6px 8px;
    border: 1px solid var(--border-color);
    border-radius: 12px;
    background: color-mix(in srgb, var(--bg-surface) 92%, transparent);
    backdrop-filter: blur(6px);
  }

  .em-modo-imersivo > .sala-header .header-acoes {
    flex-wrap: wrap;
    justify-content: flex-end;
    min-width: 0;
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

  .btn-tela-cheia {
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

  .btn-tela-cheia:hover {
    color: var(--text-primary);
    border-color: rgba(var(--veu), 0.25);
    background: var(--bg-card);
  }

  .btn-tela-cheia.ativo {
    color: var(--text-primary);
    border-color: var(--acento-info-ativo);
  }


  .ws-status {
    box-sizing: border-box;
    min-height: 44px;
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

  .tela-girada:not(.em-modo-imersivo) {
    gap: 12px;
    padding: 10px 16px 20px 16px;
  }

  @media (max-height: 460px) and (orientation: landscape) {
    .sala-container:not(.em-modo-imersivo) {
      gap: 12px;
      padding: 10px 16px 20px 16px;
    }

  }
</style>
