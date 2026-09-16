<script>
  /**
   * Ícone vetorial do conjunto Lucide (CV2.DS4.US3).
   *
   * Emoji de texto é desenhado pela fonte do sistema: o mesmo caractere sai
   * colorido no Android, chapado no Windows e com outro traço no iOS, e às
   * vezes vira retângulo vazio. Este componente desenha o mesmo traço em toda
   * plataforma e herda a cor do texto (`currentColor`), então participa do
   * sistema de tokens sem precisar de cor própria.
   *
   * Acessibilidade: o ícone é decorativo por padrão (`aria-hidden`). Quando ele
   * é a única informação do elemento — um botão só de ícone, por exemplo —
   * passe `rotulo` e ele vira `role="img"` com nome acessível.
   */
  let {
    nome,
    tamanho = '1.15em',
    traco = 2,
    rotulo = null,
    class: classe = '',
  } = $props();

  import { formasDoIcone } from '../lib/icones.js';

  const formas = $derived(formasDoIcone(nome));
</script>

<svg
  class="icone {classe}"
  xmlns="http://www.w3.org/2000/svg"
  viewBox="0 0 24 24"
  width={tamanho}
  height={tamanho}
  fill="none"
  stroke="currentColor"
  stroke-width={traco}
  stroke-linecap="round"
  stroke-linejoin="round"
  role={rotulo ? 'img' : undefined}
  aria-label={rotulo || undefined}
  aria-hidden={rotulo ? undefined : 'true'}
  focusable="false"
>
  {#each formas as forma, i (i)}
    {#if forma.tag === 'path'}
      <path d={forma.d} />
    {:else if forma.tag === 'circle'}
      <circle cx={forma.cx} cy={forma.cy} r={forma.r} />
    {:else if forma.tag === 'rect'}
      <rect
        x={forma.x}
        y={forma.y}
        width={forma.width}
        height={forma.height}
        rx={forma.rx}
      />
    {:else if forma.tag === 'line'}
      <line x1={forma.x1} y1={forma.y1} x2={forma.x2} y2={forma.y2} />
    {/if}
  {/each}
</svg>

<style>
  .icone {
    display: inline-block;
    vertical-align: -0.125em;
    flex-shrink: 0;
  }
</style>
