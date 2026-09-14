<script>
  import { slide, fade } from 'svelte/transition';
  import CartaoDobravel from './CartaoDobravel.svelte';

  let {
    estadoPartida = null,
    quadra = null,
    prefersReducedMotion = false,
    modoImersivo = true,
    onAbrirLinhaDoTempo = () => {},
  } = $props();

  const pontosA = $derived(estadoPartida?.pontos_a ?? 0);
  const pontosB = $derived(estadoPartida?.pontos_b ?? 0);
  const equipeA = $derived(estadoPartida?.equipe_a || 'Equipe A');
  const equipeB = $derived(estadoPartida?.equipe_b || 'Equipe B');
  const alvo = $derived(estadoPartida?.alvo ?? 12);
  const vantagem = $derived(estadoPartida?.vantagem ?? true);
  const teto = $derived(estadoPartida?.teto ?? null);
  const encerrada = $derived(estadoPartida?.encerrada ?? false);
  const vencedor = $derived(estadoPartida?.vencedor ?? null);

  const vencedorNome = $derived(
    vencedor === 'A' ? equipeA : vencedor === 'B' ? equipeB : null
  );
</script>

<div class="placar-manual-container {modoImersivo ? 'modo-imersivo' : ''}">
  <!-- Placa do Topo: Identificação e Regras -->
  <div class="placa-topo">
    <div class="quadra-badge">
      <span class="icone-arena">🏟️</span>
      <span class="nome-quadra">
        {quadra?.arena_nome ? quadra.arena_nome + ' • ' : ''}{quadra?.nome || 'Quadra'}
      </span>
    </div>

    <div class="regras-badge">
      <span class="regra-set">SET ÚNICO</span>
      <span class="regra-alvo">ALVO: {alvo} PTS</span>
      {#if vantagem}<span class="regra-detalhe">VANTAGEM</span>{/if}
      {#if teto}<span class="regra-detalhe">TETO {teto}</span>{/if}
    </div>
  </div>

  <!-- Banner de Vitória quando houver vencedor -->
  {#if encerrada && vencedorNome}
    <div class="banner-vitoria" in:slide={{ duration: 250 }}>
      <span class="trofeu">🏆</span>
      <div class="vitoria-info">
        <span class="vitoria-label">FIM DE JOGO</span>
        <span class="vitoria-time">Vitória da {vencedorNome}!</span>
      </div>
    </div>
  {/if}

  <!-- Cavalete / Mesa do Placar Manual -->
  <div class="cavalete-mesa">
    <!-- Barra Superior de Fixação dos Anéis -->
    <div class="barra-suporte-aneis">
      <div class="parafuso parafuso-esq"></div>
      <div class="trilho-metalico"></div>
      <div class="parafuso parafuso-dir"></div>
    </div>

    <!-- Seção dos Cartões e Equipes -->
    <div class="painel-cartoes">
      <!-- Coluna Equipe A -->
      <div class="coluna-equipe {vencedor === 'A' ? 'time-vencedor' : ''}">
        <div class="etiqueta-equipe etiqueta-a">
          <span class="etiqueta-texto">{equipeA}</span>
        </div>

        <CartaoDobravel
          valor={pontosA}
          equipe={equipeA}
          tema="a"
          tamanho="grande"
          {prefersReducedMotion}
        />
      </div>

      <!-- Divisor Central do Placar ("×" ou divisor da bancada) -->
      <div class="divisor-central">
        <div class="vs-badge">
          <span class="vs-simbolo">×</span>
        </div>
      </div>

      <!-- Coluna Equipe B -->
      <div class="coluna-equipe {vencedor === 'B' ? 'time-vencedor' : ''}">
        <div class="etiqueta-equipe etiqueta-b">
          <span class="etiqueta-texto">{equipeB}</span>
        </div>

        <CartaoDobravel
          valor={pontosB}
          equipe={equipeB}
          tema="b"
          tamanho="grande"
          {prefersReducedMotion}
        />
      </div>
    </div>

    <!-- Base Dobrável com Efeito de Sombra e Perspectiva -->
    <div class="base-cavalete">
      <div class="base-vinco"></div>
    </div>
  </div>

  <!-- Rodapé do modo imersivo: Dica sutil e Linha do Tempo -->
  <div class="rodape-imersivo">
    {#if modoImersivo}
      <div class="dica-toque" in:fade={{ duration: 200 }}>
        <span class="dica-icone">👆</span>
        <span class="dica-texto">Toque na tela para opções</span>
      </div>
    {:else}
      <button
        type="button"
        class="btn-lt-espectador"
        onclick={onAbrirLinhaDoTempo}
        aria-label="Abrir linha do tempo da partida"
      >
        <span class="lt-icon">📜</span>
        <span class="lt-label">Linha do Tempo</span>
      </button>
    {/if}
  </div>
</div>

<style>
  .placar-manual-container {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
    padding: 10px 0;
  }

  .placar-manual-container.modo-imersivo {
    min-height: 80vh;
    justify-content: center;
    gap: 24px;
    padding: 20px 0;
  }

  /* Placa do Topo */
  .placa-topo {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
  }

  .quadra-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 999px;
    padding: 4px 14px;
  }

  .icone-arena {
    font-size: 0.9rem;
  }

  .nome-quadra {
    font-size: 0.82rem;
    font-weight: 700;
    color: var(--text-primary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .regras-badge {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--text-secondary);
    letter-spacing: 0.06em;
  }

  .regra-set {
    color: var(--accent-orange);
  }

  .regra-alvo {
    color: #ffffff;
  }

  .regra-detalhe {
    color: var(--text-muted);
  }

  /* Banner de Vitória */
  .banner-vitoria {
    width: 100%;
    max-width: 440px;
    background: linear-gradient(90deg, rgba(245, 158, 11, 0.25) 0%, rgba(234, 88, 12, 0.25) 100%);
    border: 2px solid var(--accent-orange);
    border-radius: var(--radius-md);
    padding: 12px 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 14px;
    box-shadow: 0 4px 20px rgba(249, 115, 22, 0.35);
  }

  .trofeu {
    font-size: 2.2rem;
  }

  .vitoria-info {
    display: flex;
    flex-direction: column;
  }

  .vitoria-label {
    font-size: 0.75rem;
    font-weight: 800;
    text-transform: uppercase;
    color: var(--accent-orange);
    letter-spacing: 0.08em;
  }

  .vitoria-time {
    font-size: 1.25rem;
    font-weight: 800;
    color: #ffffff;
  }

  /* Cavalete / Bancada do Placar */
  .cavalete-mesa {
    width: 100%;
    max-width: 440px;
    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    border: 2px solid rgba(255, 255, 255, 0.12);
    border-radius: 18px;
    box-shadow:
      0 16px 40px rgba(0, 0, 0, 0.6),
      inset 0 1px 1px rgba(255, 255, 255, 0.15);
    padding: 12px 14px 18px 14px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    position: relative;
  }

  /* Barra Metálica Superior */
  .barra-suporte-aneis {
    width: 100%;
    height: 14px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 10px;
    position: relative;
  }

  .trilho-metalico {
    position: absolute;
    left: 20px;
    right: 20px;
    height: 4px;
    background: linear-gradient(90deg, #475569 0%, #94a3b8 50%, #475569 100%);
    border-radius: 2px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
  }

  .parafuso {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #cbd5e1;
    border: 1px solid #475569;
    box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.6);
    z-index: 2;
  }

  /* Painel dos Cartões */
  .painel-cartoes {
    width: 100%;
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: center;
    gap: 10px;
  }

  .coluna-equipe {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    transition: transform 0.2s ease;
  }

  .time-vencedor {
    transform: scale(1.02);
  }

  /* Etiquetas das Equipes no estilo plaqueta de mesa */
  .etiqueta-equipe {
    width: 100%;
    max-width: 140px;
    padding: 6px 8px;
    border-radius: 6px;
    text-align: center;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.1);
  }

  .etiqueta-a {
    background: linear-gradient(135deg, #0891b2 0%, #0e7490 100%);
    border-color: rgba(6, 182, 212, 0.5);
  }

  .etiqueta-b {
    background: linear-gradient(135deg, #ea580c 0%, #c2410c 100%);
    border-color: rgba(249, 115, 22, 0.5);
  }

  .etiqueta-texto {
    font-size: 0.84rem;
    font-weight: 800;
    color: #ffffff;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    display: block;
  }

  /* Divisor Central */
  .divisor-central {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 2px;
  }

  .vs-badge {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.1);
    display: grid;
    place-items: center;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
  }

  .vs-simbolo {
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--text-muted);
    line-height: 1;
  }

  /* Base do Cavalete */
  .base-cavalete {
    width: 96%;
    height: 6px;
    background: #0b1120;
    border-radius: 3px;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.9);
    margin-top: 4px;
  }

  /* Rodapé do Modo Imersivo */
  .rodape-imersivo {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 36px;
  }

  .dica-toque {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 500;
    color: var(--text-muted);
    animation: pulsarSuave 2.5s infinite ease-in-out;
  }

  @keyframes pulsarSuave {
    0%, 100% {
      opacity: 0.5;
    }
    50% {
      opacity: 0.9;
    }
  }

  .btn-lt-espectador {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.15);
    color: var(--text-secondary);
    border-radius: 999px;
    padding: 6px 16px;
    font-size: 0.85rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    touch-action: manipulation;
    transition: background 0.15s ease, color 0.15s ease;
  }

  .btn-lt-espectador:hover {
    background: rgba(255, 255, 255, 0.12);
    color: #ffffff;
  }
</style>
