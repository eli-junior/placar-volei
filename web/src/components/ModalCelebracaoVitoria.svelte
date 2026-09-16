<script>
  import Dialogo from './Dialogo.svelte';
  import Icone from './Icone.svelte';

  let {
    estadoPartida,
    podeControlar = false,
    onNovaPartida = () => {},
    onCompartilhar = () => {},
    onFechar = () => {},
    movimentoReduzido = false,
  } = $props();

  const vencedor = $derived(estadoPartida?.vencedor);
  const equipeA = $derived(estadoPartida?.equipe_a || 'Time A');
  const equipeB = $derived(estadoPartida?.equipe_b || 'Time B');
  const vencedorNome = $derived(vencedor === 'A' ? equipeA : equipeB);
  const pontosA = $derived(estadoPartida?.pontos_a ?? 0);
  const pontosB = $derived(estadoPartida?.pontos_b ?? 0);

  const corVencedor = $derived(vencedor === 'A' ? 'var(--time-a)' : 'var(--time-b)');
</script>

<Dialogo
  rotuladoPor="titulo-celebracao"
  variante="centro"
  largura="420px"
  {movimentoReduzido}
  {onFechar}
>
  <div class="celebracao-container" style="--cor-campeao: {corVencedor}">
    <div class="trofeu-circulo">
      <Icone nome="trofeu" tamanho="3rem" class="icone-trofeu" />
    </div>

    <header class="celebracao-cabecalho">
      <span class="subtitulo-vitoria">FIM DE JOGO</span>
      <h2 id="titulo-celebracao" class="nome-campeao">{vencedorNome} Venceu!</h2>
    </header>

    <div class="placar-final-card">
      <div class="placar-score">
        <span class="pts-a" class:vencedor-pts={vencedor === 'A'}>{pontosA}</span>
        <span class="separador">×</span>
        <span class="pts-b" class:vencedor-pts={vencedor === 'B'}>{pontosB}</span>
      </div>
      <div class="nomes-linha">
        <span class="nome-a">{equipeA}</span>
        <span class="nome-b">{equipeB}</span>
      </div>
    </div>

    <div class="acoes-celebracao">
      {#if podeControlar}
        <button
          type="button"
          class="btn-proxima-rodada"
          onclick={onNovaPartida}
        >
          <Icone nome="bola" tamanho="1.1em" />
          <span>Iniciar Próxima Partida</span>
        </button>
      {/if}

      <button
        type="button"
        class="btn-compartilhar-resultado"
        onclick={onCompartilhar}
      >
        <Icone nome="compartilhar" tamanho="1.1em" />
        <span>Compartilhar Resultado</span>
      </button>

      <button
        type="button"
        class="btn-ver-placar"
        onclick={onFechar}
      >
        <span>Ver Placar e Linha do Tempo</span>
      </button>
    </div>
  </div>
</Dialogo>

<style>
  .celebracao-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 20px;
    padding: 8px 4px;
  }

  .trofeu-circulo {
    width: 80px;
    height: 80px;
    border-radius: var(--radius-circular);
    background: radial-gradient(circle, rgba(234, 179, 8, 0.25) 0%, rgba(234, 179, 8, 0.05) 70%);
    border: 2px solid #eab308;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #eab308;
    box-shadow: 0 0 24px rgba(234, 179, 8, 0.35);
    animation: pulso-trofeu 2s ease-in-out infinite alternate;
  }

  @keyframes pulso-trofeu {
    from { transform: scale(1); }
    to { transform: scale(1.06); }
  }

  @media (prefers-reduced-motion: reduce) {
    .trofeu-circulo { animation: none; }
  }

  .celebracao-cabecalho {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .subtitulo-vitoria {
    font-size: var(--texto-micro);
    font-weight: 800;
    letter-spacing: 0.15em;
    color: var(--text-muted);
  }

  .nome-campeao {
    margin: 0;
    font-size: var(--texto-titulo-forte);
    font-weight: 800;
    color: var(--cor-campeao);
  }

  .placar-final-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 14px 20px;
    width: 100%;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .placar-score {
    font-family: var(--fonte-numeros);
    font-size: var(--texto-display);
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;
    line-height: 1;
  }

  .pts-a { color: var(--time-a); }
  .pts-b { color: var(--time-b); }
  .separador { color: var(--text-muted); font-size: 0.7em; }

  .nomes-linha {
    display: flex;
    justify-content: space-between;
    font-size: var(--texto-apoio);
    color: var(--text-secondary);
    font-weight: 600;
  }

  .nome-a { text-align: left; color: var(--time-a); }
  .nome-b { text-align: right; color: var(--time-b); }

  .acoes-celebracao {
    display: flex;
    flex-direction: column;
    gap: 10px;
    width: 100%;
  }

  .btn-proxima-rodada {
    background: #0284c7;
    color: #ffffff;
    border: none;
    border-radius: var(--radius-md);
    padding: 14px 20px;
    font-size: var(--texto-corpo);
    font-weight: 700;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    transition: background 0.15s ease;
  }

  .btn-proxima-rodada:hover {
    background: #0369a1;
  }

  .btn-compartilhar-resultado {
    background: transparent;
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    padding: 12px 18px;
    font-size: var(--texto-apoio);
    font-weight: 600;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    transition: all 0.15s ease;
  }

  .btn-compartilhar-resultado:hover {
    background: rgba(255, 255, 255, 0.08);
  }

  .btn-ver-placar {
    background: transparent;
    border: none;
    color: var(--text-muted);
    font-size: var(--texto-legenda);
    cursor: pointer;
    padding: 6px;
  }

  .btn-ver-placar:hover {
    color: var(--text-primary);
  }
</style>
