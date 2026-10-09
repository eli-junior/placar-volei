<script>
  // Fila e reis da rodada para quem acompanha a quadra (CV8.DS5.US13).
  // Só leitura: os dados vêm do servidor pela sala da quadra vinculada.
  let { exibicao = null, compacto = false } = $props();

  const mataMata = $derived(exibicao?.fase === 'mata_mata');
  const semRei = $derived(exibicao?.fase === 'sem_rei');
</script>

{#if exibicao && compacto}
  <p class="faixa" aria-label="Fila e reis">
    {#if exibicao.campeao}
      <strong>Campeões:</strong> {exibicao.campeao.nome}
    {:else}
      <strong>Fila:</strong> {exibicao.fila.length ? exibicao.fila.map((t) => t.nome).join(' · ') : 'ninguém'}
      · <strong>Reis:</strong> {exibicao.reis.length ? exibicao.reis.map((t) => t.nome).join(' · ') : 'nenhum'}
    {/if}
  </p>
{:else if exibicao}
  <section class="fila-e-reis" aria-labelledby="titulo-fila-reis">
    {#if exibicao.campeao}
      <h2 id="titulo-fila-reis">Campeões da rodada {exibicao.rodada}</h2>
      <p role="status"><strong>{exibicao.campeao.nome}</strong></p>
    {:else}
      <h2 id="titulo-fila-reis">Rodada {exibicao.rodada}</h2>
      <div aria-live="polite">
        {#if exibicao.em_quadra.length}
          <h3>{mataMata ? 'Mata-mata em quadra' : 'Em quadra'}</h3>
          <ul>
            {#each exibicao.em_quadra as t (t.time)}
              <li><span class="nome">{t.nome}</span>{#if t.vitorias} <span class="selo">{t.vitorias} vit.</span>{/if}</li>
            {/each}
          </ul>
        {/if}
        {#if semRei}<p class="vazio" role="status">Terminou sem rei.</p>{/if}
        <h3>Fila ({exibicao.fila.length})</h3>
        {#if exibicao.fila.length}
          <ol>
            {#each exibicao.fila as t (t.time)}
              <li><span class="nome">{t.nome}</span>{#if t.incompleto} <span class="selo">chegando</span>{/if}</li>
            {/each}
          </ol>
        {:else}
          <p class="vazio">Ninguém esperando.</p>
        {/if}
        <h3>Reis ({exibicao.reis.length})</h3>
        {#if exibicao.reis.length}
          <ol>
            {#each exibicao.reis as t (t.time)}
              <li><span class="nome">{t.nome}</span></li>
            {/each}
          </ol>
        {:else}
          <p class="vazio">Nenhum rei ainda.</p>
        {/if}
      </div>
    {/if}
  </section>
{/if}

<style>
  .faixa { flex: 0 0 auto; margin: 0; padding: .35rem .6rem; font-size: var(--texto-apoio); color: var(--texto-medio); text-align: center; overflow-wrap: anywhere; }
  .fila-e-reis { margin: .75rem 1rem; padding: .9rem 1rem; border: 1px solid var(--borda-sutil); border-radius: var(--raio-padrao); background: var(--fundo-superficie); color: var(--texto-forte); }
  h2 { margin: 0 0 .4rem; font-size: var(--texto-destaque); }
  h3 { margin: .6rem 0 .25rem; font-size: var(--texto-corpo); color: var(--texto-medio); }
  ul, ol { margin: 0; padding-left: 1.3rem; }
  li { padding: .1rem 0; }
  .nome { font-weight: 700; }
  .selo { margin-left: .35rem; padding: .05rem .45rem; border-radius: var(--raio-circular); background: var(--fundo-cartao-ativo); color: var(--texto-medio); font-size: var(--texto-micro); font-weight: 700; }
  .vazio { margin: 0; color: var(--texto-suave); font-size: var(--texto-apoio); }
</style>
