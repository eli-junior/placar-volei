<script>
  import { onMount } from 'svelte';
  import Dialogo from './Dialogo.svelte';
  import { mensagemDeErro } from '../sync.js';

  let { quadra, onFechar = () => {}, movimentoReduzido = false } = $props();
  let codigo = $state('');
  let dispositivos = $state([]);
  let habilitado = $state(false);
  let ocupado = $state(true);
  let mensagem = $state('');
  let erro = $state('');

  async function requisitar(caminho = '', options = {}) {
    const resposta = await fetch(`/api/quadras/${quadra.id}/watch${caminho}`, options);
    const dados = await resposta.json();
    if (!resposta.ok) throw new Error(mensagemDeErro(dados));
    return dados;
  }

  async function atualizar() {
    const dados = await requisitar();
    habilitado = dados.enabled;
    dispositivos = dados.devices;
  }

  onMount(() => {
    atualizar().catch(e => { erro = e.message; }).finally(() => { ocupado = false; });
  });

  async function vincular(event) {
    event.preventDefault();
    ocupado = true;
    erro = '';
    mensagem = '';
    try {
      await requisitar('/approve', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: codigo }),
      });
      codigo = '';
      mensagem = 'Relógio vinculado. Você aparece como eli para os outros.';
      await atualizar();
    } catch (e) { erro = e.message; }
    finally { ocupado = false; }
  }

  async function revogar(id) {
    ocupado = true;
    erro = '';
    mensagem = '';
    try {
      await requisitar(`/${id}`, { method: 'DELETE' });
      mensagem = 'Acesso do relógio revogado. Seu telefone continua conectado.';
      await atualizar();
    } catch (e) { erro = e.message; }
    finally { ocupado = false; }
  }
</script>

<Dialogo rotuladoPor="titulo-relogio" {onFechar} {movimentoReduzido}>
  <div class="conteudo">
    <header>
      <h2 id="titulo-relogio">Meu relógio</h2>
      <button type="button" onclick={onFechar} aria-label="Fechar relógio">×</button>
    </header>
    {#if habilitado}
      <p>Abra o Placar Vôlei no relógio e digite o código exibido nele. Confira que o código veio do seu relógio antes de autorizar.</p>
      <form onsubmit={vincular}>
        <label for="codigo-relogio">Código do relógio</label>
        <input id="codigo-relogio" bind:value={codigo} inputmode="numeric" pattern={'[0-9]{8}'} minlength="8" maxlength="8" autocomplete="off" required disabled={ocupado} />
        <button type="submit" disabled={ocupado || !/^[0-9]{8}$/.test(codigo)}>Vincular à sala {quadra.id}</button>
      </form>
      {#if dispositivos.length}
        <p>Vincular outro relógio revoga o acesso do anterior.</p>
      {/if}
    {:else if !ocupado && !erro}
      <p>O acesso de teste ao relógio ainda não foi habilitado para você nesta sala.</p>
    {/if}
    {#each dispositivos as dispositivo (dispositivo.id)}
      <div class="dispositivo">
        <span>Meu Galaxy Watch</span>
        <button type="button" disabled={ocupado} onclick={() => revogar(dispositivo.id)}>Revogar acesso</button>
      </div>
    {/each}
    <p role="status">{ocupado ? 'Aguarde…' : mensagem}</p>
    {#if erro}<p role="alert">{erro}</p>{/if}
  </div>
</Dialogo>

<style>
  .conteudo { padding: 24px; }
  header, .dispositivo { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
  h2 { font-size: 1.25rem; }
  p { margin: 16px 0; line-height: 1.5; }
  form { display: grid; gap: 12px; }
  input, button { min-height: 44px; border: 1px solid var(--borda-sutil); border-radius: var(--raio-padrao, 8px); background: var(--fundo-superficie); color: var(--texto-forte); padding: 10px 14px; }
  input { width: 100%; box-sizing: border-box; font-size: 1.5rem; letter-spacing: 0.15em; }
  button { cursor: pointer; }
  button:disabled { opacity: 0.5; cursor: default; }
  .dispositivo { flex-wrap: wrap; margin-top: 20px; }
  [role='alert'] { color: var(--estado-erro); }
</style>
