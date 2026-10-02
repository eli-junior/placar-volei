<script>
  // Tela inicial do APK (CV7.TS1, US1): a quadra online do servidor fixo do
  // build, ou a quadra local quando não há comunicação com ele. A conexão
  // decide qual das duas está habilitada.
  import { onMount, untrack } from 'svelte';
  import Icone from './Icone.svelte';
  import { modosDisponiveis, normalizarServidor, servidorDisponivel } from '../lib/casca.js';

  let {
    servidorPadrao = '',
    // { existe, emAndamento } da quadra local guardada neste aparelho.
    local = { existe: false, emAndamento: false },
    ilegivel = false,
    onAbrirLocal = () => {},
    onDescartarIlegivel = () => {},
    erro = '',
  } = $props();

  // O servidor é o do build (`PLACAR_SERVIDOR`) e não é editável.
  const origem = untrack(() => normalizarServidor(servidorPadrao));
  // 'testando' | 'disponivel' | 'indisponivel'
  let estado = $state(origem ? 'testando' : 'indisponivel');
  const modos = $derived(modosDisponiveis({ servidor: estado, configurado: Boolean(origem), local }));

  async function testar() {
    if (!origem) return;
    estado = 'testando';
    estado = (await servidorDisponivel(origem)) ? 'disponivel' : 'indisponivel';
  }

  onMount(testar);

  function abrirOnline(evento) {
    evento.preventDefault();
    if (!modos.online) return;
    window.location.href = `${origem}/`;
  }

  function abrirLocal(evento) {
    evento.preventDefault();
    if (modos.local) onAbrirLocal();
  }
</script>

<main class="inicio-app">
  <header class="marca">
    <Icone nome="bola" tamanho="2.2em" />
    <h1>Placar Vôlei</h1>
  </header>

  {#if erro}<p class="erro" role="alert">{erro}</p>{/if}

  <form class="cartao" onsubmit={abrirOnline}>
    <h2>Quadra online</h2>
    <p>Placar compartilhado pelo servidor: espectadores pelo link e relógio pela internet.</p>
    <p class="servidor">{origem ?? 'Servidor não configurado neste APK.'}</p>
    <p class="estado" class:erro={estado === 'indisponivel'} role="status">
      {#if estado === 'testando'}Testando a conexão…
      {:else if estado === 'disponivel'}Servidor disponível.
      {:else}Sem comunicação com o servidor.{/if}
    </p>
    <button type="submit" disabled={!modos.online}>Abrir quadras online</button>
    {#if estado === 'indisponivel' && origem}
      <button type="button" class="secundario" onclick={testar}>Testar de novo</button>
    {/if}
  </form>

  <form class="cartao" class:inativo={!modos.local} onsubmit={abrirLocal} aria-labelledby="titulo-local">
    <h2 id="titulo-local">Quadra local</h2>
    <p>Sem internet nem servidor: o placar fica guardado neste aparelho.</p>
    {#if ilegivel}
      <p class="erro" role="alert">Os dados da quadra local estavam ilegíveis e não foram usados.</p>
      <button type="button" class="secundario" onclick={onDescartarIlegivel}>Começar do zero</button>
    {/if}
    {#if modos.aviso}<p class="estado" role="status">{modos.aviso}</p>{/if}
    {#if local.existe && local.emAndamento && estado === 'disponivel'}
      <p class="estado" role="status">Há uma partida em andamento nesta quadra.</p>
    {/if}
    <button type="submit" disabled={!modos.local}>
      {modos.acaoLocal === 'continuar' ? 'Continuar quadra local' : 'Criar quadra local'}
    </button>
  </form>
</main>

<style>
  .inicio-app {
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    gap: 16px;
    max-width: 480px;
    min-height: 100vh;
    margin: 0 auto;
    padding: 32px 16px;
    color: var(--texto-forte);
  }
  .marca { display: flex; align-items: center; gap: 12px; color: var(--time-b); }
  h1 { margin: 0; font-size: 1.6rem; color: var(--texto-forte); }
  h2 { margin: 0; font-size: 1.1rem; }
  p { margin: 0; color: var(--texto-suave); line-height: 1.4; }
  .cartao {
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 18px;
    border-radius: var(--radius-md);
    background: var(--fundo-superficie);
    border: 1px solid rgba(var(--veu), 0.12);
  }
  .servidor { font-weight: 700; color: var(--texto-forte); word-break: break-all; }
  button {
    min-height: 52px;
    border: 0;
    border-radius: var(--radius-md);
    background: var(--acao-primaria);
    color: var(--acao-primaria-texto);
    font-size: 1rem;
    font-weight: 800;
    cursor: pointer;
  }
  button:disabled { opacity: .5; cursor: not-allowed; }
  .secundario { background: transparent; color: var(--texto-forte); border: 1px solid rgba(var(--veu), 0.3); }
  .erro { color: var(--estado-erro); font-weight: 600; }
  .inativo { border-style: dashed; }
</style>
