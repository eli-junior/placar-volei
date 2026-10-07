<script>
  import { onMount } from 'svelte';
  import { baixarFoto, iniciais } from '../lib/jogadores.js';

  // Miniatura do jogador: baixa a foto com o segredo (o <img> não envia
  // cabeçalho) e cai nas iniciais quando não há foto.
  let { segredo, jogador } = $props();
  let url = $state(null);

  onMount(() => {
    let vivo = true;
    let criada = null;
    if (jogador.tem_foto) {
      baixarFoto(segredo, jogador.id).then((u) => {
        if (!u) return;
        if (vivo) { criada = u; url = u; } else URL.revokeObjectURL(u);
      }).catch(() => {});
    }
    return () => { vivo = false; if (criada) URL.revokeObjectURL(criada); };
  });
</script>

{#if url}<img class="avatar" src={url} alt="" />{:else}<span class="avatar" aria-hidden="true">{iniciais(jogador.nome)}</span>{/if}

<style>
  .avatar { display: inline-flex; align-items: center; justify-content: center; flex: none; width: 40px; height: 40px; border-radius: var(--raio-circular); object-fit: cover; background: var(--fundo-cartao-ativo); color: var(--texto-medio); font-size: var(--texto-legenda); font-weight: 800; }
</style>
