<script>
  // Endereço que não existe (CV8.DS7.US18). O servidor devolve o app para
  // qualquer caminho; sem este aviso, um erro de digitação parecia a home.
  let { caminho = '' } = $props();
</script>

<section class="nao-encontrada" aria-labelledby="titulo-nao-encontrada">
  <h1 id="titulo-nao-encontrada">Página não encontrada</h1>
  <p>O endereço <code>{caminho}</code> não existe neste app.</p>
  <a class="acao" href="/">Voltar ao início</a>
</section>

<style>
  .nao-encontrada { box-sizing: border-box; max-width: 640px; margin: 0 auto; padding: calc(var(--sa-topo) + 2rem) 1rem calc(var(--sa-baixo) + 2rem); display: flex; flex-direction: column; align-items: flex-start; gap: 1rem; color: var(--texto-forte); }
  h1 { margin: 0; font-size: var(--texto-titulo-forte); }
  p { margin: 0; color: var(--texto-medio); overflow-wrap: anywhere; }
  code { color: var(--texto-forte); }
  .acao { display: inline-flex; align-items: center; justify-content: center; min-height: 52px; padding: 0 1.1rem; border-radius: 10px; background: var(--acao-primaria); color: var(--acao-primaria-texto); font-weight: 800; text-decoration: none; }
  .acao:focus-visible { outline: none; box-shadow: var(--foco-anel); }
</style>
