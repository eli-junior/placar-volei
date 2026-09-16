<script>
  /**
   * Diálogo padrão do produto (CV2.DS4.US2).
   *
   * Antes desta história cada modal era uma `div` com `position: fixed`,
   * `role="dialog"` escrito à mão e um `onkeydown` próprio para o Esc. Três
   * cópias do mesmo comportamento, nenhuma com retenção de foco: com o teclado
   * era possível tabular para trás do modal e operar a tela de baixo sem ver o
   * que estava acontecendo.
   *
   * A tag nativa `<dialog>` com `showModal()` entrega de graça o que estava
   * faltando: foco preso dentro do diálogo, elemento no top layer (acima de
   * qualquer `z-index`), inerte para o resto da página e fechamento por `Esc`
   * pelo próprio navegador — inclusive para leitores de tela.
   *
   * O que este componente acrescenta ao nativo:
   *
   * - `Esc` vira `onFechar` em vez de fechar direto, para que o pai continue
   *   dono do estado (`{#if aberto}`) e nenhuma tela fique com um diálogo
   *   invisível montado;
   * - clique no backdrop fecha (o navegador entrega esse clique com
   *   `event.target === <dialog>`, o que dispensa a div extra de fundo);
   * - backdrop com desfoque e as transições de entrada do produto;
   * - `aria-labelledby` obrigatório por contrato: quem usa aponta o id do
   *   título, e o diálogo passa a ser anunciado pelo nome.
   */
  import { fly, scale } from 'svelte/transition';

  let {
    /** id do elemento que dá nome ao diálogo (`aria-labelledby`). */
    rotuladoPor = null,
    /** Alternativa ao id quando não existe título visível. */
    rotulo = null,
    /** `centro` para caixa centralizada; `folha` para folha inferior no celular. */
    variante = 'centro',
    /** Largura máxima da caixa. */
    largura = '440px',
    /** Respeita `prefers-reduced-motion` quando o pai já sabe a preferência. */
    movimentoReduzido = false,
    /** Fechar ao clicar fora da caixa. */
    fecharNoFundo = true,
    onFechar = () => {},
    children,
  } = $props();

  let elemento = $state(null);

  $effect(() => {
    const dialogo = elemento;
    if (dialogo && !dialogo.open) {
      dialogo.showModal();
    }
    return () => {
      if (dialogo?.open) dialogo.close();
    };
  });

  // `cancel` é o evento do Esc. Impedimos o fechamento nativo para que o
  // estado continue no pai: quem abriu é quem fecha.
  function aoCancelar(evento) {
    evento.preventDefault();
    onFechar();
  }

  function aoClicar(evento) {
    if (!fecharNoFundo) return;
    if (evento.target === elemento) onFechar();
  }

  const duracao = $derived(movimentoReduzido ? 0 : 200);
</script>

<dialog
  bind:this={elemento}
  class="dialogo dialogo-{variante}"
  style="--dialogo-largura: {largura}"
  aria-labelledby={rotuladoPor || undefined}
  aria-label={rotuladoPor ? undefined : rotulo || undefined}
  oncancel={aoCancelar}
  onclick={aoClicar}
>
  {#if variante === 'folha'}
    <div class="dialogo-caixa" in:fly={{ y: 80, duration: duracao }}>
      {@render children?.()}
    </div>
  {:else}
    <div
      class="dialogo-caixa"
      in:scale={{ start: 0.96, duration: duracao, opacity: 0 }}
    >
      {@render children?.()}
    </div>
  {/if}
</dialog>

<style>
  .dialogo {
    border: none;
    padding: 0;
    background: transparent;
    color: inherit;
    max-width: 100vw;
    max-height: 100dvh;
    width: 100%;
    overflow: visible;
  }

  .dialogo::backdrop {
    background: rgba(2, 6, 23, 0.82);
    backdrop-filter: blur(4px);
    animation: dialogo-fundo 150ms ease;
  }

  @keyframes dialogo-fundo {
    from {
      opacity: 0;
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .dialogo::backdrop {
      animation: none;
    }
  }

  /* Caixa centralizada — entrar, criar sala, compartilhar. */
  .dialogo-centro {
    margin: auto;
    padding: 20px;
  }

  .dialogo-centro .dialogo-caixa {
    width: 100%;
    max-width: var(--dialogo-largura);
    margin: 0 auto;
    background: var(--fundo-superficie);
    border: 1px solid var(--borda-sutil);
    border-radius: var(--raio-amplo);
    box-shadow: var(--sombra-elevada);
    max-height: calc(100dvh - 40px);
    overflow-y: auto;
  }

  /* Folha inferior — linha do tempo e listas longas no celular. */
  .dialogo-folha {
    margin: auto auto 0;
    padding: max(12px, env(safe-area-inset-top)) max(12px, env(safe-area-inset-right)) 0
      max(12px, env(safe-area-inset-left));
  }

  .dialogo-folha .dialogo-caixa {
    width: 100%;
    max-width: var(--dialogo-largura);
    margin: 0 auto;
    background: var(--fundo-base);
    border: 1px solid var(--borda-sutil);
    border-radius: var(--raio-amplo) var(--raio-amplo) 0 0;
    box-shadow: var(--sombra-elevada);
    max-height: min(88dvh, calc(var(--tela-h, 100dvh) - 16px));
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  @media (min-width: 640px) {
    .dialogo-folha {
      margin: auto;
      padding: 24px;
    }

    .dialogo-folha .dialogo-caixa {
      border-radius: var(--raio-amplo);
      max-height: min(82dvh, calc(var(--tela-h, 100dvh) - 24px));
    }
  }

  @media (max-height: 520px) {
    .dialogo-folha .dialogo-caixa {
      max-height: calc(100dvh - 12px);
    }
  }
</style>
