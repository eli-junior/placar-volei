<script>
  import Icone from './Icone.svelte';

  // Pede o segredo do dono (CV8). Quem guarda e usa o segredo é a tela.
  let { erro = null, ocupado = false, onEntrar = () => {} } = $props();
  let digitado = $state('');

  function enviar(evento) {
    evento.preventDefault();
    const segredo = digitado.trim();
    if (!segredo) return;
    digitado = '';
    onEntrar(segredo);
  }
</script>

<form class="cartao" onsubmit={enviar}>
  <p>Esta área é protegida. Digite o segredo do dono; ele fica guardado só neste aparelho.</p>
  {#if erro}<div class="alerta" role="alert"><Icone nome="alerta" tamanho="1.1em" /><span>{erro}</span></div>{/if}
  <label for="segredo-dono">Segredo do dono</label>
  <input id="segredo-dono" type="password" autocomplete="off" bind:value={digitado} required />
  <button class="acao-principal" type="submit" disabled={!digitado.trim() || ocupado}>Entrar</button>
</form>

<style>
  .cartao { display: flex; flex-direction: column; gap: .6rem; padding: 1rem; border: 1px solid var(--borda-sutil); border-radius: var(--raio-padrao); background: var(--fundo-superficie); color: var(--texto-forte); }
  p { margin: 0; color: var(--texto-suave); font-size: var(--texto-apoio); }
  label { font-size: var(--texto-apoio); color: var(--texto-medio); }
  input { box-sizing: border-box; width: 100%; min-height: 48px; padding: .75rem .9rem; border: 1px solid var(--acao-secundaria); border-radius: 10px; outline: none; background: var(--fundo-base); color: var(--texto-forte); font: inherit; }
  input:focus-visible { border-color: var(--foco-cor); box-shadow: var(--foco-anel); }
  .acao-principal { display: flex; align-items: center; justify-content: center; min-height: 52px; padding: 0 1.1rem; border: 0; border-radius: 10px; background: var(--acao-primaria); color: var(--acao-primaria-texto); font: inherit; font-weight: 800; cursor: pointer; }
  .acao-principal:disabled { opacity: .45; cursor: not-allowed; }
  .alerta { display: flex; align-items: flex-start; gap: .6rem; padding: .75rem; border: 1px solid color-mix(in srgb, var(--estado-erro) 45%, transparent); border-radius: 10px; background: color-mix(in srgb, var(--estado-erro) 12%, transparent); color: var(--estado-erro-suave); font-size: .83rem; line-height: 1.4; }
</style>
