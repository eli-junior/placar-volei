<script>
  // Tela inicial do APK (CV7.TS1): escolhe a quadra online do servidor.
  // A quadra local (sem internet) chega na CV7.US1.
  import { untrack } from 'svelte';
  import Icone from './Icone.svelte';
  import { lerServidor, normalizarServidor, salvarServidor } from '../lib/casca.js';

  let { servidorPadrao = '' } = $props();

  // Só o valor inicial: depois vale o que a pessoa digitar.
  let endereco = $state(lerServidor(undefined, untrack(() => servidorPadrao)));
  let erro = $state('');

  function abrirOnline(evento) {
    evento.preventDefault();
    const origem = normalizarServidor(endereco);
    if (!origem) {
      erro = 'Endereço inválido. Use o domínio do servidor, por exemplo placar.seudominio.com.';
      return;
    }
    erro = '';
    salvarServidor(origem);
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
    <label for="servidor">Servidor</label>
    <input
      id="servidor"
      type="url"
      inputmode="url"
      autocomplete="url"
      placeholder="placar.seudominio.com"
      bind:value={endereco}
      aria-invalid={erro ? 'true' : undefined}
      aria-describedby={erro ? 'erro-servidor' : undefined}
    />
    {#if erro}<p id="erro-servidor" class="erro" role="alert">{erro}</p>{/if}
    <button type="submit">Abrir quadras online</button>
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
  label { font-weight: 700; font-size: .9rem; }
  input {
    min-height: 48px;
    padding: 0 12px;
    border-radius: var(--radius-md);
    border: 1px solid rgba(var(--veu), 0.3);
    background: var(--fundo-base);
    color: var(--texto-forte);
    font-size: 1rem;
  }
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
  .erro { color: var(--estado-erro); font-weight: 600; }
  .em-breve { border-style: dashed; }
</style>
