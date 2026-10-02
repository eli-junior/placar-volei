<script>
  // Interface embarcada do APK (CV7.US1): a tela inicial e a quadra local.
  // A quadra online é o servidor aberto no WebView, não passa por aqui.
  import { onMount } from 'svelte';
  import InicioApp from './components/InicioApp.svelte';
  import SalaQuadra from './components/SalaQuadra.svelte';
  import { QuadraLocal, armazenamentoPadrao } from './lib/quadraLocal.js';
  import { lerApelido } from './lib/preferencias.js';
  import { criarPonteRelogio, pluginRelogio } from './lib/ponteRelogio.js';

  let { servidorPadrao = '' } = $props();

  let armazenamento = null;
  let quadraLocal = $state(null);
  let ilegivel = $state(false);
  let carregando = $state(true);
  let erro = $state('');
  // Tela: 'inicio' ou 'sala' (quadra local aberta).
  let tela = $state('inicio');
  let snapshot = $state(null);
  let pendentes = $state(0);
  // Ponte com o relógio (CV7.TS3): só no APK e só com a sala local aberta.
  let ponte = null;

  function apelidoSalvo() {
    try {
      return lerApelido() || null;
    } catch {
      return null;
    }
  }

  async function carregar() {
    carregando = true;
    erro = '';
    try {
      armazenamento ??= await armazenamentoPadrao();
      const aberta = await QuadraLocal.abrir(armazenamento, { apelido: apelidoSalvo() });
      quadraLocal = aberta.quadra;
      ilegivel = aberta.ilegivel;
      atualizarResumo();
    } catch {
      erro = 'Não foi possível ler a quadra local deste aparelho.';
    } finally {
      carregando = false;
    }
  }

  onMount(carregar);

  // A `QuadraLocal` muda por dentro (não é reativa): o resumo da tela inicial é
  // refeito sempre que a quadra nasce, some ou a pessoa volta da sala.
  let resumoLocal = $state({ existe: false, emAndamento: false });
  function atualizarResumo() {
    resumoLocal = { existe: Boolean(quadraLocal), emAndamento: Boolean(quadraLocal?.emAndamento) };
  }

  async function abrirLocal() {
    erro = '';
    try {
      quadraLocal ??= await QuadraLocal.criar(armazenamento, { apelido: apelidoSalvo() });
      snapshot = quadraLocal.snapshot();
      tela = 'sala';
      ligarPonte();
    } catch (e) {
      erro = e.message || 'Não foi possível abrir a quadra local.';
    }
  }

  // O relógio é um extra: sem ele (ou fora do APK) a quadra local segue igual.
  async function ligarPonte() {
    try {
      const plugin = await pluginRelogio();
      if (!plugin || tela !== 'sala') return;
      ponte = criarPonteRelogio({ plugin, quadra: quadraLocal, aoMudar: (s) => { snapshot = s; } });
      await ponte.iniciar();
    } catch {
      ponte = null;
    }
  }

  async function desligarPonte() {
    const atual = ponte;
    ponte = null;
    try { await atual?.parar(); } catch {}
  }

  async function descartarIlegivel() {
    try {
      await QuadraLocal.descartarIlegivel(armazenamento);
      ilegivel = false;
    } catch (e) {
      erro = e.message || 'Não foi possível descartar os dados ilegíveis.';
    }
  }

  let erroSala = $state(null);

  // Cada toque entra na fila da própria quadra local; aqui só a tela reage.
  async function executar(comando) {
    if (!quadraLocal) return;
    pendentes += 1;
    erroSala = null;
    try {
      snapshot = await comando(quadraLocal);
      ponte?.publicar();
    } catch (e) {
      erroSala = e.message || 'Não foi possível realizar a ação.';
    } finally {
      pendentes = Math.max(0, pendentes - 1);
    }
  }

  async function apagarQuadraLocal() {
    erroSala = null;
    await desligarPonte();
    try {
      await quadraLocal.apagar();
    } catch (e) {
      erroSala = e.message || 'Não foi possível apagar a quadra local.';
      return;
    }
    quadraLocal = null;
    snapshot = null;
    atualizarResumo();
    tela = 'inicio';
  }

  function voltar() {
    desligarPonte();
    atualizarResumo();
    tela = 'inicio';
    snapshot = null;
  }
</script>

<main>
  {#if carregando}
    <p role="status" class="carregando">Carregando…</p>
  {:else if tela === 'sala' && snapshot}
    <SalaQuadra
      quadra={snapshot.quadra}
      eu={quadraLocal.eu}
      participantes={snapshot.participantes}
      estadoPartida={snapshot.estado_partida}
      linhaDoTempo={snapshot.linha_do_tempo}
      wsConectado={true}
      modoLocal={true}
      onMarcarPonto={(equipe) => executar((q) => q.marcarPonto(equipe))}
      onDesfazerPonto={() => executar((q) => q.desfazer())}
      onIniciarNovaPartida={(dados) => executar((q) => q.reiniciar(dados ?? {}))}
      onConfigurarPartida={(dados) => executar((q) => q.configurar(dados ?? {}))}
      onLiberarQuadra={apagarQuadraLocal}
      onVoltar={voltar}
      operando={pendentes > 0}
      {pendentes}
      erro={erroSala}
    />
  {:else}
    <InicioApp
      {servidorPadrao}
      local={resumoLocal}
      {ilegivel}
      {erro}
      onAbrirLocal={abrirLocal}
      onDescartarIlegivel={descartarIlegivel}
    />
    {#if erro && !quadraLocal && !ilegivel}
      <button type="button" class="tentar" onclick={carregar}>Tentar de novo</button>
    {/if}
  {/if}
</main>

<style>
  main { flex: 1; display: flex; flex-direction: column; }
  .carregando { margin: auto; color: var(--texto-suave); }
  .tentar { margin: 0 auto 24px; min-height: 48px; padding: 0 20px; }
</style>
