<script>
  // Tela inicial do APK (CV7.TS1): abre a quadra online do servidor fixo do build.
  // A quadra local (sem internet) chega na CV7.US1.
  import { onMount, untrack } from 'svelte';
  import Icone from './Icone.svelte';
  import { normalizarServidor, servidorDisponivel } from '../lib/casca.js';

  let { servidorPadrao = '' } = $props();

  // O servidor é o do build (`PLACAR_SERVIDOR`) e não é editável.
  const origem = untrack(() => normalizarServidor(servidorPadrao));
  // 'testando' | 'disponivel' | 'indisponivel'
  let estado = $state(origem ? 'testando' : 'indisponivel');

  async function testar() {
    if (!origem) return;
    estado = 'testando';
    estado = (await servidorDisponivel(origem)) ? 'disponivel' : 'indisponivel';
  }

  onMount(testar);

  function abrirOnline(evento) {
    evento.preventDefault();
    if (estado !== 'disponivel') return;
    window.location.href = `${origem}/`;
  }
</script>

<main class="inicio-app">
  <header class="marca">
    <Icone nome="bola" tamanho="2.2em" />
    <h1>Placar Vôlei</h1>
  </header>

  <form class="cartao" onsubmit={abrirOnline}>
    <h2>Quadra online</h2>
    <p>Placar compartilhado pelo servidor: espectadores pelo link e relógio pela internet.</p>
    <p class="servidor">{origem ?? 'Servidor não configurado neste APK.'}</p>
    <p class="estado" class:erro={estado === 'indisponivel'} role="status">
      {#if estado === 'testando'}Testando a conexão…
      {:else if estado === 'disponivel'}Servidor disponível.
      {:else}Servidor indisponível. Verifique a internet e tente de novo.{/if}
    </p>
    <button type="submit" disabled={estado !== 'disponivel'}>Abrir quadras online</button>
    {#if estado === 'indisponivel' && origem}
      <button type="button" class="secundario" onclick={testar}>Testar de novo</button>
    {/if}
  </form>

  <section class="cartao em-breve" aria-labelledby="titulo-local">
    <h2 id="titulo-local">Quadra local</h2>
    <p>Sem internet, com o relógio por Bluetooth. Em breve.</p>
  </section>
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
  .em-breve { border-style: dashed; }
</style>
