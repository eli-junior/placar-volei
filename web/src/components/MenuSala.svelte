<script>
  /**
   * Menu ⋯ da sala (CV4.DS3.US1/US2): local único das ações secundárias,
   * para operador e espectador. Cada ação fecha o menu antes de agir, para
   * que só exista um diálogo aberto por vez; o `Dialogo` devolve o foco ao ⋯.
   */
  import { tick } from 'svelte';
  import Dialogo from './Dialogo.svelte';
  import Icone from './Icone.svelte';

  let {
    /** [{ rotulo, icone, acao, pressionado?, fechaMenu? }] */
    acoes = [],
    movimentoReduzido = false,
    onFechar = () => {},
    children,
  } = $props();

  async function executar(item) {
    if (item.fechaMenu === false) {
      item.acao();
      return;
    }
    onFechar();
    // Espera o menu sair e o foco voltar ao ⋯; assim o próximo diálogo o
    // registra como acionador.
    await tick();
    setTimeout(item.acao, 0);
  }
</script>

<Dialogo rotulo="Mais ações" variante="folha" largura="520px" {movimentoReduzido} {onFechar}>
  <div class="menu-sala">
    <div class="menu-acoes">
      {#each acoes as item (item.rotulo)}
        <button type="button" onclick={() => executar(item)} aria-pressed={item.pressionado}>
          <Icone nome={item.icone} tamanho="1.1em" /><span>{item.rotulo}</span>
        </button>
      {/each}
      <button type="button" onclick={onFechar}>
        <Icone nome="fechar" tamanho="1.1em" /><span>Fechar</span>
      </button>
    </div>
    {@render children?.()}
  </div>
</Dialogo>

<style>
  .menu-sala { display: flex; flex-direction: column; gap: 14px; padding: 16px; max-height: 80dvh; overflow-y: auto; }
  .menu-acoes { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 8px; }
  .menu-acoes button {
    display: flex;
    align-items: center;
    gap: 10px;
    min-height: 52px;
    padding: 0 14px;
    border: 1px solid var(--border-color);
    border-radius: 12px;
    background: var(--bg-surface);
    color: var(--text-primary);
    font: inherit;
    font-weight: 650;
    text-align: left;
    cursor: pointer;
  }
</style>
