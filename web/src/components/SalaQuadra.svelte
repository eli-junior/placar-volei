<script>
  import { aplicarTema, guardarTema, lerTemaSol } from '../lib/tema.js';
  import { seloDoPapel, lerTamanhoNumeros, guardarTamanhoNumeros, proximoTamanhoNumeros, TAMANHOS_NUMEROS } from '../lib/preferencias.js';
  import { fade, slide } from 'svelte/transition';
  import ModalRelogio from './ModalRelogio.svelte';
  import ListaPresentes from './ListaPresentes.svelte';
  import Placar from './Placar.svelte';
  import PlacarManual from './PlacarManual.svelte';
  import LinhaDoTempo from './LinhaDoTempo.svelte';
  import Icone from './Icone.svelte';
  import Dialogo from './Dialogo.svelte';
  import ModalCompartilhar from './ModalCompartilhar.svelte';
  import ModalConfigurarPartida from './ModalConfigurarPartida.svelte';
  import ModalCelebracaoVitoria from './ModalCelebracaoVitoria.svelte';
  import { ehDonoDoRelogio } from '../lib/relogio.js';
  import { ultimoPontoDesfazivel, sequenciaDePontos, descreverPosse, resumirRegras, resumirRegrasCurto } from '../lib/controle.js';
  import MenuSala from './MenuSala.svelte';
  import FilaEReis from './FilaEReis.svelte';
  import { estadoConexao } from '../lib/conexao.js';
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
    exibicao = null,
    wsConectado = false,
    // Quadra local do APK (CV7.US1): sem servidor, espectadores, presença nem relógio.
    modoLocal = false,
    onMarcarPonto = () => {},
    onDesfazerPonto = () => {},
    onIniciarNovaPartida = () => {},
    onConfigurarPartida = () => {},
    onVoltar,
    onAssumirControle = () => {},
    onPromoverControlador = (id) => {},
    onRevogarControlador = (id) => {},
    onAutorizarAdmin = (id) => {},
    onLiberarQuadra = () => {},
    onPassarControle = (id) => {},
    operando = false,
    pendentes = 0,
    erro = null,
  } = $props();

  const CHAVE_GIRO = 'placar:girado';
  const CHAVE_INVERSAO_BASE = 'placar:lados_invertidos:';
  // Já aplicado em `main.js` antes do mount; aqui só o estado do botão.
  let temaSol = $state(lerTemaSol());

  function alternarTema() {
    temaSol = !temaSol;
    aplicarTema(temaSol);
    guardarTema(temaSol);
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
  // Parte do modal de configurações aberta pelo atalho (CV6.DS1.US6); `tudo` no ⚙.
  let secaoConfig = $state('tudo');
  // Dica do selo de papel no topo (CV6.DS1.US7): aparece ao tocar e some sozinha.
  let dicaSeloAberta = $state(false);
  let timerDicaSelo;
  function mostrarDicaSelo() {
    dicaSeloAberta = !dicaSeloAberta;
    clearTimeout(timerDicaSelo);
    if (dicaSeloAberta) timerDicaSelo = setTimeout(() => { dicaSeloAberta = false; }, 2500);
  }
  function abrirConfig(secao = 'tudo') {
    secaoConfig = secao;
    isReinicioConfig = false;
    modalConfigAberto = true;
  }
  let isReinicioConfig = $state(false);
  // Reiniciar no meio da partida: zera pontos e linha do tempo, mantém regras e nomes.
  let confirmandoReiniciar = $state(false);
  let modalCelebracaoAberto = $state(false);
  let celebracaoExibidaPartidaId = $state(null);
  let prefersReducedMotion = $state(false);

  // Celebração de Vitória Automática (CV2.DS4.US1)
  $effect(() => {
    if (estadoPartida?.encerrada && estadoPartida?.vencedor && quadra?.partida_id) {
      if (celebracaoExibidaPartidaId !== quadra.partida_id) {
        celebracaoExibidaPartidaId = quadra.partida_id;
        modalCelebracaoAberto = true;
      }
    }
  });

  // Wake Lock API (CV2.DS2.US3): tela acesa enquanto a sala estiver aberta,
  // inclusive entre partidas, para não perder a conexão com o relógio.
  let wakeLockSentinel = null;

  async function requisitarWakeLock() {
    if (typeof navigator === 'undefined' || !navigator.wakeLock) return;
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

    requisitarWakeLock();

    const onVisibilityChange = () => {
      if (document.visibilityState === 'visible') requisitarWakeLock();
    };

    document.addEventListener('visibilitychange', onVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', onVisibilityChange);
      liberarWakeLock();
    };
  });

  let timerClique;
  // Timers de aviso não sobrevivem à saída da sala.
  $effect(() => () => { clearTimeout(timerClique); });


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
  const selo = $derived(seloDoPapel(eu?.papel));

  const temControle = $derived(podeControlar && quadra?.controle_id === eu?.id);
  const posse = $derived(
    descreverPosse({ temControle, ehAdmin, operador: participantes.find(p => p.id === quadra?.controle_id)?.apelido, conectado: wsConectado })
  );
  const ultimoPonto = $derived(ultimoPontoDesfazivel(linhaDoTempo));
  const sequencia = $derived(sequenciaDePontos(linhaDoTempo));
  let menuAberto = $state(false);

  // Tamanho dos números, só neste aparelho (CV6.DS1.US3).
  let tamanhoNumeros = $state(lerTamanhoNumeros());
  function alternarTamanhoNumeros() {
    tamanhoNumeros = proximoTamanhoNumeros(tamanhoNumeros);
    guardarTamanhoNumeros(tamanhoNumeros);
  }

  // Local único das ações secundárias (CV4.DS3.US1/US2). Cada papel vê só o
  // que pode fazer; o que já tem lugar próprio na tela não se repete aqui.
  // Em ordem de prioridade (Navigator): as primeiras sobem para o topo
  // quando há espaço; o ⋯ fica só com o que não coube.
  const acoesSecundarias = $derived([
    // Ajustes e inversão vêm primeiro: saem do topo por último (Navigator).
    ...(podeControlar
      ? [{ rotulo: 'Duplas e regras', dica: 'Duplas e regras da partida', icone: 'engrenagem', acao: () => abrirConfig() }]
      : []),
    { rotulo: 'Inverter lados', dica: 'Inverter lados das equipes', icone: 'inverter', acao: alternarLados, pressionado: ladosInvertidos, fechaMenu: false },
    { rotulo: temaSol ? 'Modo escuro' : 'Modo sol', icone: temaSol ? 'lua' : 'sol', acao: alternarTema, pressionado: temaSol, fechaMenu: false },
    ...(podeControlar
      ? [
          // O relógio na quadra local chega com a CV7.US2.
          ...(modoLocal ? [] : [{ rotulo: 'Relógio', icone: 'relogio', acao: abrirRelogio }]),
          { rotulo: 'Linha do tempo', icone: 'linhaDoTempo', acao: handleAbrirLinhaDoTempo },
        ]
      : []),
    { rotulo: `Números: ${tamanhoNumeros}`, icone: 'expandir', acao: alternarTamanhoNumeros, fechaMenu: false },
    ...(!podeControlar && !paisagemNativa
      ? [{ rotulo: girado ? 'Placar em retrato' : 'Girar para paisagem', icone: 'atualizar', acao: alternarGiro, pressionado: girado, fechaMenu: false }]
      : []),
    // Destrutivo: por último, sobe ao topo só se sobrar espaço depois de tudo.
    ...(podeControlar && temControle && ehAdmin
      ? [{ rotulo: 'Reiniciar partida', icone: 'atualizar', acao: () => { confirmandoReiniciar = true; } }]
      : []),
  ]);

  // Quantos atalhos cabem no topo: sobra da barra depois dos itens fixos.
  let larguraBarra = $state(0);
  let larguraCodigo = $state(0);
  const PASSO_BOTAO = 52; // 44px de alvo + 8px de espaço
  const atalhosNoTopo = $derived.by(() => {
    if (!larguraBarra) return 0;
    // Voltar, ⋯, selo e tela cheia nunca saem; o status entra como o passo extra abaixo.
    const fixos = 2 + (podeControlar && selo ? 1 : 0) + (!podeControlar && telaCheiaDisponivel ? 1 : 0);
    // A faixa das regras divide a linha só em tela larga; estreita, ela desce.
    // Mínimo para "10 pts (V)"; o texto longo só aparece com a sobra.
    const faixa = podeControlar && viewportW >= 600 ? 120 : 0;
    // O chip precisa ao menos do código inteiro (o nome encolhe com reticências).
    const sobra = larguraBarra - 12 - (larguraCodigo + 34) - fixos * PASSO_BOTAO - PASSO_BOTAO - faixa;
    return Math.max(0, Math.min(acoesSecundarias.length, Math.floor(sobra / PASSO_BOTAO)));
  });
  let larguraFaixa = $state(0);
  // "10 pts com vantagem" → "10 pontos Ⓥ" → "10 pts Ⓥ", conforme o espaço.
  const nivelRegras = $derived(larguraFaixa >= 240 ? 'longo' : larguraFaixa >= 150 ? 'medio' : 'curto');
  const acoesNoTopo = $derived(acoesSecundarias.slice(0, atalhosNoTopo));
  const acoesDoMenu = $derived(acoesSecundarias.slice(atalhosNoTopo));

  // Nome padrão ("Quadra #código") não acrescenta nada ao código.
  const nomeProprio = $derived(quadra?.nome && quadra.nome !== `Quadra #${quadra.id}` ? quadra.nome : '');

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

  // Rede do aparelho: separa "sem internet" (vermelho) de "reconectando" (amarelo).
  let online = $state(typeof navigator === 'undefined' ? true : navigator.onLine);
  $effect(() => {
    const atualizar = () => { online = navigator.onLine; };
    window.addEventListener('online', atualizar);
    window.addEventListener('offline', atualizar);
    return () => {
      window.removeEventListener('online', atualizar);
      window.removeEventListener('offline', atualizar);
    };
  });
  const conexaoVisivel = $derived(
    modoLocal
      ? { chave: 'conectado', rotulo: 'Quadra local: placar guardado neste aparelho, sem internet', pendentes: 0 }
      : estadoConexao(wsConectado, online, pendentes)
  );

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
        clearTimeout(timerClique);
        timerClique = setTimeout(() => { engolirClique = false; }, 500);
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
  style="--tela-w: {telaW}px; --tela-h: {telaH}px; --escala-numeros: {TAMANHOS_NUMEROS[tamanhoNumeros]};"
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
  <!-- Cabeçalho em uma linha (CV6.DS1.US1): voltar, quadra, status, ajustes,
       inverter lados e menu; a posse ocupa o meio e desce para a segunda
       linha só em tela estreita. Espectador imersivo esconde a linha. -->
  {#if podeControlar || !modoImersivo}
    <header class="barra-sala" bind:clientWidth={larguraBarra} in:slide={{ duration: prefersReducedMotion || podeControlar ? 0 : 200 }} out:slide={{ duration: prefersReducedMotion || podeControlar ? 0 : 200 }}>
      <button type="button" class="btn-topo btn-voltar" onclick={onVoltar} aria-label={modoLocal ? 'Voltar ao início' : 'Voltar para a lista de quadras'} title="Voltar">
        <svg aria-hidden="true" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5l-7 7 7 7" /></svg>
      </button>
      <!-- O código abre o compartilhamento (link, QR e cópia). -->
      {#if modoLocal}
        <span class="chip-codigo" role="img" aria-label="Quadra local, sem internet">
          <strong bind:clientWidth={larguraCodigo}>Local</strong>
        </span>
      {:else}
        <button type="button" class="chip-codigo" onclick={() => { modalCompartilharAberto = true; }} aria-haspopup="dialog" title="Compartilhar a sala" aria-label="Compartilhar a sala {quadra.id}">
          <strong bind:clientWidth={larguraCodigo}>#{quadra.id}</strong>
          {#if nomeProprio}<span>{nomeProprio}</span>{/if}
        </button>
      {/if}
      {#if podeControlar}
        <div class="faixa-posse" bind:clientWidth={larguraFaixa} class:minha={temControle}>
          <!-- Anúncio da posse fora do {#key}: a região viva não pode nascer a
               cada troca, e só o texto da posse é lido (CV5.DS4.US2). -->
          <span class="sr-only" aria-live="polite">{posse.titulo}. {posse.detalhe}</span>
          <!-- Na tela, as regras da partida valem mais que a posse (Navigator, CV6.DS1.US1). -->
          <button type="button" class="regras-topo" onclick={() => abrirConfig('regras')} title="Ajustar pontuação e vantagem: {resumirRegras(estadoPartida)}"><span class="sr-only">Ajustar regras: {resumirRegras(estadoPartida)}</span><span aria-hidden="true">{resumirRegrasCurto(estadoPartida, nivelRegras)}</span>{#if nivelRegras !== 'longo'}<span class="selo-vantagem" class:acesa={estadoPartida?.vantagem ?? true} aria-hidden="true">V</span>{/if}</button>
          {#if posse.podeAssumir}
            <button class="btn-assumir" disabled={!wsConectado || operando} onclick={onAssumirControle}>Assumir</button>
          {/if}
        </div>
        {#if selo}
          <span class="selo-papel-ancora">
            <button type="button" class="btn-topo selo-papel" onclick={mostrarDicaSelo} aria-label={selo.dica} aria-expanded={dicaSeloAberta} title={selo.dica}>
              <span class="letra-circulada" aria-hidden="true">{selo.letra}</span>
            </button>
            {#if dicaSeloAberta}<span class="dica-selo" role="status">{selo.dica}</span>{/if}
          </span>
        {/if}
{/if}
      {#if !podeControlar && telaCheiaDisponivel}
        <button
          type="button"
          class="btn-topo"
          class:ativo={telaCheia}
          onclick={alternarTelaCheia}
          aria-pressed={telaCheia}
          aria-label={telaCheia ? 'Sair da tela cheia' : 'Tela cheia'}
          title={telaCheia ? 'Sair da tela cheia' : 'Tela cheia'}
        >
          <Icone nome={telaCheia ? 'recolher' : 'expandir'} tamanho="1.15em" />
        </button>
      {/if}
      {#each acoesNoTopo as item (item.rotulo)}
        <button
          type="button"
          class="btn-topo"
          class:ativo={item.pressionado}
          onclick={item.acao}
          aria-pressed={item.pressionado === undefined ? undefined : item.pressionado}
          aria-label={item.dica ?? item.rotulo}
          title={item.dica ?? item.rotulo}
        ><Icone nome={item.icone} tamanho="1.15em" /></button>
      {/each}
      <button
        type="button"
        class="btn-topo"
        onclick={() => { menuAberto = true; }}
        aria-haspopup="dialog"
        aria-label="Mais ações"
        title="Mais ações"
      ><span aria-hidden="true">⋯</span></button>
      <span class="caixa-status" title={conexaoVisivel.rotulo}>
        <span
          class="status-dot status-topo {conexaoVisivel.chave === 'conectado' ? 'status-online' : conexaoVisivel.chave === 'offline' ? 'status-sem-rede' : 'status-reconectando'}"
          class:com-fila={conexaoVisivel.pendentes > 0}
          role="img"
          aria-label={conexaoVisivel.rotulo}
        >{#if conexaoVisivel.pendentes > 0}<span aria-hidden="true">{conexaoVisivel.pendentes > 99 ? '99+' : conexaoVisivel.pendentes}</span>{/if}</span>
      </span>
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
        Reconectando… Os controles do placar voltam sozinhos.
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
      {ladosInvertidos}
      {onMarcarPonto}
      {onDesfazerPonto}
      onIniciarNovaPartida={() => {
        secaoConfig = 'tudo';
        modalConfigAberto = true;
        isReinicioConfig = true;
      }}
      onEditarEquipe={(equipe) => abrirConfig(equipe === 'A' ? 'equipe-a' : 'equipe-b')}
      {ultimoPonto}
      {sequencia}
      onAbrirCompartilhar={() => { modalCompartilharAberto = true; }}
      semCompartilhar={modoLocal}
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
      {ultimoPonto}
      {sequencia}
      onAbrirLinhaDoTempo={handleAbrirLinhaDoTempo}
    />
    </div>
  {/if}

  <FilaEReis {exibicao} compacto={modoImersivo || podeControlar} />

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
      secao={isReinicioConfig ? 'tudo' : secaoConfig}
      podeLiberar={ehAdmin && !isReinicioConfig && secaoConfig === 'tudo'}
      {modoLocal}
      onLiberar={() => { modalConfigAberto = false; onLiberarQuadra(); }}
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
      onReinicioRapido={() => {
        modalCelebracaoAberto = false;
        onIniciarNovaPartida();
      }}
      onFechar={() => { modalCelebracaoAberto = false; }}
    />
  {/if}

  {#if confirmandoReiniciar}
    <Dialogo rotulo="Reiniciar partida" movimentoReduzido={prefersReducedMotion} onFechar={() => { confirmandoReiniciar = false; }}>
      <div class="confirma-reiniciar">
        <p>Reiniciar a partida? Pontos e linha do tempo serão apagados. Regras e nomes ficam.</p>
        <div class="confirma-acoes">
          <button type="button" onclick={() => { confirmandoReiniciar = false; }}>Cancelar</button>
          <button type="button" class="perigo" disabled={operando} onclick={() => { confirmandoReiniciar = false; modalCelebracaoAberto = false; onIniciarNovaPartida({ zerar: true }); }}>Reiniciar</button>
        </div>
      </div>
    </Dialogo>
  {/if}

  {#if menuAberto}
    <MenuSala acoes={acoesDoMenu} movimentoReduzido={prefersReducedMotion} onFechar={() => { menuAberto = false; }}>
      {#if !modoLocal}
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
      {/if}
    </MenuSala>
  {/if}
</div>

<style>
  .confirma-reiniciar { display: flex; flex-direction: column; gap: 14px; padding: 18px; color: var(--text-primary); }
  .confirma-reiniciar p { margin: 0; }
  .confirma-acoes { display: flex; gap: 8px; justify-content: flex-end; }
  .confirma-acoes button { min-height: 44px; padding: 0 16px; border: 1px solid var(--border-color); border-radius: 12px; background: var(--bg-surface); color: var(--text-primary); font: inherit; font-weight: 650; cursor: pointer; }
  .confirma-acoes .perigo { border-color: #c62828; background: #c62828; color: #fff; }
  /* Operação sem rolagem (CV4.DS3.US1). */
  .sala-container.operador {
    height: 100vh;
    height: 100dvh;
    min-height: 0;
    gap: 8px;
    padding: max(8px, var(--sa-topo))
      max(8px, var(--sa-direita))
      max(8px, var(--sa-baixo))
      max(8px, var(--sa-esquerda));
    overflow: hidden;
  }

  .barra-sala { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; min-width: 0; flex: 0 0 auto; }
  .btn-topo,
  .chip-codigo {
    min-height: 44px;
    box-sizing: border-box;
    border: 1px solid var(--border-color);
    border-radius: 12px;
    background: var(--bg-surface);
    color: var(--text-secondary);
    cursor: pointer;
    touch-action: manipulation;
  }
  /* Alvo de toque fixo: o nome da quadra encolhe, os botões nunca. */
  .btn-topo {
    display: grid;
    place-items: center;
    width: 44px;
    flex: 0 0 44px;
    padding: 0;
    font-size: 1.2rem;
    line-height: 1;
  }
  .btn-topo:hover { color: var(--text-primary); background: var(--bg-card); }
  .btn-topo.ativo { color: var(--text-primary); border-color: var(--acento-info-ativo); }
  .caixa-status {
    display: grid;
    place-items: center;
    width: 44px;
    height: 44px;
    flex: 0 0 44px;
    box-sizing: border-box;
    border: 1px solid var(--border-color);
    border-radius: 12px;
    background: var(--bg-surface);
  }
  /* Voltar e status redondos: saída e sinal de vida, distintos das ações. */
  .btn-voltar { color: var(--text-primary); }
  .btn-voltar,
  .caixa-status { border-radius: 50%; }
  .status-topo { position: relative; width: 24px; height: 24px; }
  /* Conectado: onda que vaza da bolinha e some; movimento reduzido global a desliga. */
  .status-topo.status-online::after {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: inherit;
    background: inherit;
    animation: vazar-status 1.8s ease-out infinite;
    pointer-events: none;
  }
  @keyframes vazar-status {
    0% { transform: scale(1); opacity: .7; }
    100% { transform: scale(2.1); opacity: 0; }
  }
  /* Lances a sincronizar: número dentro da bolinha, como o ↑N do relógio. */
  .status-topo.com-fila {
    display: grid;
    place-items: center;
    width: auto;
    min-width: 28px;
    height: 28px;
    padding: 0 6px;
    box-sizing: border-box;
    border-radius: 14px;
    color: #06140c;
    font: 800 .9rem/1 var(--fonte-numeros, inherit);
    font-variant-numeric: tabular-nums;
  }
  .status-topo.com-fila > span { position: relative; z-index: 1; }
  .chip-codigo {
    min-height: 44px;
    box-sizing: border-box;
    border: 1px solid var(--border-color);
    border-radius: 12px;
    background: var(--bg-surface);
    color: var(--text-secondary);
    cursor: pointer;
    touch-action: manipulation;
  }
  /* Alvo de toque fixo: o nome da quadra encolhe, os botões nunca. */
  .btn-topo {
    display: grid;
    place-items: center;
    width: 44px;
    flex: 0 0 44px;
    padding: 0;
    font-size: 1.2rem;
    line-height: 1;
  }
  .btn-topo:hover { color: var(--text-primary); background: var(--bg-card); }
  .btn-topo.ativo { color: var(--text-primary); border-color: var(--acento-info-ativo); }
  .caixa-status {
    display: grid;
    place-items: center;
    width: 44px;
    height: 44px;
    flex: 0 0 44px;
    box-sizing: border-box;
    border: 1px solid var(--border-color);
    border-radius: 12px;
    background: var(--bg-surface);
  }
  /* Voltar e status redondos: saída e sinal de vida, distintos das ações. */
  .btn-voltar { color: var(--text-primary); }
  .btn-voltar,
  .caixa-status { border-radius: 50%; }
  .status-topo { width: 18px; height: 18px; }
  /* Lances a sincronizar: número dentro da bolinha, como o ↑N do relógio. */
  .status-topo.com-fila {
    display: grid;
    place-items: center;
    width: auto;
    min-width: 24px;
    height: 24px;
    padding: 0 5px;
    box-sizing: border-box;
    border-radius: 12px;
    color: #06140c;
    font: 800 .8rem/1 var(--fonte-numeros, inherit);
    font-variant-numeric: tabular-nums;
  }
  /* Pulso só quando ao vivo; movimento reduzido global o desliga. */
  .status-topo.status-online { animation: pulso-status 2s ease-in-out infinite; }
  @keyframes pulso-status {
    0%, 100% { box-shadow: 0 0 0 0 var(--estado-sucesso-brilho); }
    50% { box-shadow: 0 0 0 6px transparent; }
  }
  .chip-codigo { display: flex; flex-direction: column; align-items: flex-start; justify-content: center; gap: 1px; flex: 0 1 auto; min-width: 0; max-width: 40%; padding: 2px 12px; line-height: 1.1; }
  .chip-codigo strong { font-family: var(--fonte-numeros); font-size: 1.35rem; letter-spacing: .04em; color: var(--text-primary); }
  span.chip-codigo { cursor: default; }
  .chip-codigo span { max-width: 100%; overflow: hidden; font-size: .72rem; text-overflow: ellipsis; white-space: nowrap; }

  .faixa-posse {
    display: flex;
    align-items: center;
    gap: 10px;
    min-height: 44px;
    box-sizing: border-box;
    padding: 0 6px 0 12px;
    border: 1px solid var(--border-color);
    border-radius: 12px;
    background: var(--bg-surface);
    flex: 1 1 0;
    min-width: 0;
  }
  /* Tela estreita: a posse vira a segunda linha inteira, os botões ficam em cima. */
  @media (max-width: 599px) {
    .barra-sala { gap: 6px; }
    .barra-sala .chip-codigo { flex: 1 1 0; max-width: none; justify-content: center; padding: 0 6px; overflow: hidden; }
    .barra-sala .chip-codigo strong { font-size: 1.1rem; }
    .barra-sala .chip-codigo span { display: none; }
    .barra-sala .faixa-posse { order: 1; flex-basis: 100%; }
  }
  .regras-topo { min-height: 36px; padding: 0 4px; border: 0; border-radius: 8px; background: none; cursor: pointer; font-family: inherit; text-align: left; text-decoration: underline dotted color-mix(in srgb, currentColor 45%, transparent); text-underline-offset: 4px; }
  .regras-topo:hover { background: rgba(var(--veu), .06); }
  .regras-topo { overflow: hidden; min-width: 0; color: var(--text-primary); font-weight: 700; font-size: .9rem; text-overflow: ellipsis; white-space: nowrap; }
  .regras-topo { display: inline-flex; align-items: center; gap: 6px; }
  /* Ⓥ: acesa com vantagem, apagada sem. */
  .selo-vantagem { display: inline-grid; place-items: center; flex: 0 0 auto; width: 1.45em; height: 1.45em; border: 2px solid currentColor; border-radius: 50%; font-size: .75rem; font-weight: 900; opacity: .3; }
  .selo-vantagem.acesa { opacity: 1; color: var(--estado-sucesso, #22c55e); box-shadow: 0 0 8px color-mix(in srgb, currentColor 55%, transparent); }
  .selo-papel-ancora { position: relative; flex: 0 0 auto; }
  .selo-papel { color: var(--text-secondary); }
  .letra-circulada {
    display: grid;
    place-items: center;
    width: 1.5em;
    height: 1.5em;
    border: 2px solid currentColor;
    border-radius: 50%;
    font-size: .8rem;
    font-weight: 900;
  }
  .dica-selo {
    position: absolute;
    top: calc(100% + 6px);
    right: 0;
    z-index: 30;
    padding: 6px 10px;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    background: var(--bg-card);
    color: var(--text-primary);
    font-size: .85rem;
    font-weight: 700;
    white-space: nowrap;
    box-shadow: 0 6px 18px rgba(0, 0, 0, .18);
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
    padding: max(18px, var(--sa-topo))
      max(20px, var(--sa-direita))
      max(32px, var(--sa-baixo))
      max(20px, var(--sa-esquerda));
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
    padding: max(8px, var(--sa-topo))
      max(6px, var(--sa-direita))
      max(8px, var(--sa-baixo))
      max(6px, var(--sa-esquerda));
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

  .em-modo-imersivo > .barra-sala {
    position: absolute;
    z-index: 6;
    top: max(8px, var(--sa-topo));
    left: max(6px, var(--sa-esquerda));
    right: max(6px, var(--sa-direita));
    padding: 6px 8px;
    border: 1px solid var(--border-color);
    border-radius: 12px;
    background: color-mix(in srgb, var(--bg-surface) 92%, transparent);
    backdrop-filter: blur(6px);
  }

  .em-modo-imersivo .placar-espectador-wrapper {
    flex: 1 1 auto;
    height: 100%;
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
