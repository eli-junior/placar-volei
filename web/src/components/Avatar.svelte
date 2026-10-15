<script>
  import { onMount } from 'svelte';
  import { baixarFoto, iniciais } from '../lib/jogadores.js';

  // Miniatura do jogador: baixa a foto com o segredo (o <img> não envia
  // cabeçalho) e cai nas iniciais quando não há foto.
  let { segredo, jogador, tamanho = 40 } = $props();
  let url = $state(null);
  // Número é px; texto aceita qualquer medida CSS (o cartão da Resenha usa cqw).
  const medida = $derived(typeof tamanho === 'number' ? `${tamanho}px` : tamanho);

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

{#if url}<img class="avatar" style:--tamanho={medida} src={url} alt="" />{:else}<span class="avatar" style:--tamanho={medida} aria-hidden="true">{iniciais(jogador.nome)}</span>{/if}

<style>
  .avatar { display: inline-flex; align-items: center; justify-content: center; flex: none; width: var(--tamanho, 40px); height: var(--tamanho, 40px); border-radius: var(--raio-circular); object-fit: cover; background: var(--fundo-cartao-ativo); color: var(--texto-medio); font-size: calc(var(--tamanho, 40px) * .34); font-weight: 800; }
</style>
