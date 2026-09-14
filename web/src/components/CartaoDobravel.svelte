<script>
  let {
    valor = 0,
    equipe = '',
    tema = 'a', // 'a' (ciano) ou 'b' (laranja)
    tamanho = 'normal', // 'normal' | 'grande'
    prefersReducedMotion = false,
  } = $props();

  let valorExibido = $state(0);
  let valorAnterior = $state(0);
  let inicializado = $state(false);
  let direcaoAnimacao = $state(null); // 'descer' | 'subir' | null
  let timeoutAnimacao = null;

  $effect(() => {
    if (!inicializado) {
      valorExibido = valor;
      valorAnterior = valor;
      inicializado = true;
      return;
    }

    if (valor !== valorExibido) {
      const novoValor = valor;
      const antigoValor = valorExibido;
      const diff = novoValor - antigoValor;

      valorAnterior = antigoValor;
      valorExibido = novoValor;

      if (prefersReducedMotion) {
        direcaoAnimacao = null;
        return;
      }

      if (timeoutAnimacao) {
        clearTimeout(timeoutAnimacao);
      }

      if (diff > 0) {
        direcaoAnimacao = 'descer';
      } else {
        direcaoAnimacao = 'subir';
      }

      timeoutAnimacao = setTimeout(() => {
        direcaoAnimacao = null;
      }, 360);
    }
  });
</script>

<div class="cartao-wrapper tamanho-{tamanho} tema-{tema}">
  <!-- Anéis metálicos superiores do placar dobrável -->
  <div class="aneis-container" aria-hidden="true">
    <div class="anel anel-esq">
      <div class="anel-arco"></div>
      <div class="anel-sombra"></div>
    </div>
    <div class="anel anel-dir">
      <div class="anel-arco"></div>
      <div class="anel-sombra"></div>
    </div>
  </div>

  <!-- Cartão Base / Estático -->
  <div class="cartao-placa cartao-base" aria-live="polite">
    <div class="ilhoses-container" aria-hidden="true">
      <div class="ilhos ilhos-esq"></div>
      <div class="ilhos ilhos-dir"></div>
    </div>

    <div class="vinco-central" aria-hidden="true"></div>

    <div class="numero-container">
      <span class="numero-texto">{direcaoAnimacao === 'descer' ? valorAnterior : valorExibido}</span>
    </div>
  </div>

  <!-- Cartão em Movimento 3D (Flip mecânico) -->
  {#if direcaoAnimacao === 'descer'}
    <div class="cartao-placa cartao-animado anim-descer" aria-hidden="true">
      <div class="ilhoses-container">
        <div class="ilhos ilhos-esq"></div>
        <div class="ilhos ilhos-dir"></div>
      </div>
      <div class="vinco-central"></div>
      <div class="numero-container">
        <span class="numero-texto">{valorExibido}</span>
      </div>
    </div>
  {:else if direcaoAnimacao === 'subir'}
    <div class="cartao-placa cartao-animado anim-subir" aria-hidden="true">
      <div class="ilhoses-container">
        <div class="ilhos ilhos-esq"></div>
        <div class="ilhos ilhos-dir"></div>
      </div>
      <div class="vinco-central"></div>
      <div class="numero-container">
        <span class="numero-texto">{valorAnterior}</span>
      </div>
    </div>
  {/if}
</div>

<style>
  .cartao-wrapper {
    position: relative;
    perspective: 1200px;
    user-select: none;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding-top: 14px; /* Espaço para o arco dos anéis */
  }

  /* Tamanho Normal (usado no controlador) */
  .tamanho-normal {
    width: 110px;
    height: 130px;
  }

  .tamanho-normal .cartao-placa {
    height: 116px;
    width: 100%;
  }

  .tamanho-normal .numero-texto {
    font-size: 5rem;
  }

  /* Tamanho Grande (usado no modo imersivo do espectador) */
  .tamanho-grande {
    width: 148px;
    height: 180px;
  }

  .tamanho-grande .cartao-placa {
    height: 166px;
    width: 100%;
  }

  .tamanho-grande .numero-texto {
    font-size: 7.2rem;
  }

  @media (min-width: 480px) {
    .tamanho-grande {
      width: 175px;
      height: 215px;
    }

    .tamanho-grande .cartao-placa {
      height: 201px;
    }

    .tamanho-grande .numero-texto {
      font-size: 8.6rem;
    }
  }

  /* Anéis Metálicos Superiores (Espiral / Argolas do placar manual) */
  .aneis-container {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 32px;
    display: flex;
    justify-content: space-between;
    padding: 0 20px;
    pointer-events: none;
    z-index: 10;
  }

  .anel {
    width: 14px;
    height: 28px;
    position: relative;
  }

  .anel-arco {
    width: 100%;
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(135deg, #e2e8f0 0%, #94a3b8 40%, #ffffff 65%, #475569 100%);
    box-shadow:
      0 2px 5px rgba(0, 0, 0, 0.6),
      inset 0 1px 2px rgba(255, 255, 255, 0.9),
      inset 0 -1px 2px rgba(0, 0, 0, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.4);
  }

  /* Cartão de Pontuação (Placa de PVC/Papelão do placar clássico) */
  .cartao-placa {
    position: absolute;
    top: 14px;
    left: 0;
    border-radius: 12px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow:
      0 8px 24px rgba(0, 0, 0, 0.6),
      inset 0 1px 1px rgba(255, 255, 255, 0.15),
      inset 0 -2px 4px rgba(0, 0, 0, 0.5);
    backface-visibility: hidden;
  }

  .cartao-base {
    z-index: 1;
  }

  .cartao-animado {
    z-index: 2;
    transform-origin: 50% 12px; /* Centro da linha dos anéis */
    will-change: transform, opacity, filter;
  }

  /* Temas de Cores Esportivas */
  .tema-a .cartao-placa {
    background: linear-gradient(180deg, #092635 0%, #03141f 50%, #020b12 100%);
    border: 2px solid rgba(6, 182, 212, 0.35);
  }

  .tema-a .numero-texto {
    color: #e0f2fe;
    text-shadow:
      0 2px 14px rgba(6, 182, 212, 0.6),
      0 0 2px rgba(255, 255, 255, 0.9);
  }

  .tema-b .cartao-placa {
    background: linear-gradient(180deg, #381508 0%, #1c0802 50%, #0d0300 100%);
    border: 2px solid rgba(249, 115, 22, 0.35);
  }

  .tema-b .numero-texto {
    color: #ffedd5;
    text-shadow:
      0 2px 14px rgba(249, 115, 22, 0.6),
      0 0 2px rgba(255, 255, 255, 0.9);
  }

  /* Furos/Ilhoses dos anéis no cartão */
  .ilhoses-container {
    position: absolute;
    top: 5px;
    left: 0;
    right: 0;
    display: flex;
    justify-content: space-between;
    padding: 0 20px;
    z-index: 3;
    pointer-events: none;
  }

  .ilhos {
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: #020617;
    border: 2px solid #64748b;
    box-shadow:
      inset 0 2px 4px rgba(0, 0, 0, 0.9),
      0 1px 1px rgba(255, 255, 255, 0.2);
  }

  /* Vinco central horizontal típico de cartões dobráveis */
  .vinco-central {
    position: absolute;
    top: 50%;
    left: 0;
    right: 0;
    height: 2px;
    background: rgba(0, 0, 0, 0.65);
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    z-index: 4;
    pointer-events: none;
  }

  /* Exibição do Numeral */
  .numero-container {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    z-index: 2;
    padding-top: 6px;
  }

  .numero-texto {
    font-family: var(--font-display);
    font-weight: 800;
    line-height: 0.9;
    letter-spacing: -0.02em;
    font-variant-numeric: tabular-nums;
  }

  /* Animações Mecânicas de Virada de Cartão (Flip 3D) */
  .anim-descer {
    animation: flipCardDown 0.35s cubic-bezier(0.25, 1, 0.5, 1) forwards;
  }

  .anim-subir {
    animation: flipCardUp 0.30s cubic-bezier(0.4, 0, 0.8, 0.4) forwards;
  }

  @keyframes flipCardDown {
    0% {
      transform: rotateX(-95deg);
      filter: brightness(0.65);
      box-shadow: 0 0 0 rgba(0, 0, 0, 0);
    }
    65% {
      transform: rotateX(8deg);
      filter: brightness(1.1);
      box-shadow: 0 16px 28px rgba(0, 0, 0, 0.6);
    }
    100% {
      transform: rotateX(0deg);
      filter: brightness(1);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);
    }
  }

  @keyframes flipCardUp {
    0% {
      transform: rotateX(0deg);
      filter: brightness(1);
      opacity: 1;
    }
    100% {
      transform: rotateX(-95deg);
      filter: brightness(0.6);
      opacity: 0;
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .cartao-animado {
      animation: none !important;
      transform: none !important;
      display: none !important;
    }
  }
</style>
