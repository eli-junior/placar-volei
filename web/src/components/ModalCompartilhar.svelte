<script>
  import Dialogo from './Dialogo.svelte';
  import Icone from './Icone.svelte';
  import { gerarQrCode, caminhoSvg, ladoComMargem } from '../lib/qrcode.js';

  let {
    quadra,
    onFechar = () => {},
    movimentoReduzido = false,
  } = $props();

  let copiadoPin = $state(false);
  let copiadoLink = $state(false);

  const urlCompleta = $derived(
    typeof window !== 'undefined'
      ? `${window.location.origin}/quadra/${quadra?.id}`
      : `https://placar.volei/quadra/${quadra?.id}`
  );

  const dadosQr = $derived.by(() => {
    try {
      const matriz = gerarQrCode(urlCompleta, 'M');
      const tamanho = ladoComMargem(matriz.length);
      const d = caminhoSvg(matriz);
      return { matriz, tamanho, d };
    } catch (e) {
      console.warn('Erro ao gerar QR Code:', e);
      return null;
    }
  });

  const suportaShare = $derived(
    typeof navigator !== 'undefined' && typeof navigator.share === 'function'
  );

  async function handleCompartilharNativo() {
    if (!suportaShare) return;
    try {
      await navigator.share({
        title: `Placar Vôlei — ${quadra?.nome || 'Sala ' + quadra?.id}`,
        text: `Acompanhe a partida de vôlei ao vivo no celular! Código da sala: ${quadra?.id}`,
        url: urlCompleta,
      });
    } catch (e) {
      // Usuário cancelou o compartilhamento
    }
  }

  function handleCopiarPin() {
    if (typeof navigator !== 'undefined' && navigator.clipboard && quadra?.id) {
      navigator.clipboard.writeText(quadra.id);
      copiadoPin = true;
      setTimeout(() => { copiadoPin = false; }, 2000);
    }
  }

  function handleCopiarLink() {
    if (typeof navigator !== 'undefined' && navigator.clipboard) {
      navigator.clipboard.writeText(urlCompleta);
      copiadoLink = true;
      setTimeout(() => { copiadoLink = false; }, 2000);
    }
  }
</script>

<Dialogo
  rotuladoPor="titulo-compartilhar"
  variante="centro"
  largura="380px"
  {movimentoReduzido}
  {onFechar}
>
  <div class="modal-compartilhar">
    <header class="modal-header">
      <div class="header-titulo-grupo">
        <Icone nome="compartilhar" tamanho="1.25em" class="icone-destaque" />
        <h3 id="titulo-compartilhar">Compartilhar Sala</h3>
      </div>
      <button
        type="button"
        class="btn-fechar"
        onclick={onFechar}
        aria-label="Fechar modal de compartilhamento"
      >
        <Icone nome="fechar" tamanho="1.1em" />
      </button>
    </header>

    <div class="modal-corpo">
      <p class="instrucao">
        Aponte a câmera do celular para entrar ou envie o código para a galera acompanhar.
      </p>

      <!-- Bloco de QR Code -->
      {#if dadosQr}
        <div class="qr-container">
          <svg
            viewBox="0 0 {dadosQr.tamanho} {dadosQr.tamanho}"
            class="qr-svg"
            role="img"
            aria-label="QR Code para acesso direto à quadra"
          >
            <rect width="100%" height="100%" fill="#ffffff" rx="8" />
            <path d={dadosQr.d} fill="#0f172a" />
          </svg>
        </div>
      {/if}

      <!-- Cartão com o PIN de 5 dígitos -->
      <div class="pin-card">
        <div class="pin-info">
          <span class="pin-label">CÓDIGO DA SALA</span>
          <span class="pin-numero">{quadra?.id}</span>
        </div>
        <button
          type="button"
          class="btn-copiar-pin"
          onclick={handleCopiarPin}
          aria-label="Copiar código numérico da sala"
        >
          <Icone nome={copiadoPin ? 'confirmado' : 'copiar'} tamanho="1.1em" />
          <span>{copiadoPin ? 'Copiado!' : 'Copiar'}</span>
        </button>
      </div>

      <!-- Ações de Compartilhamento -->
      <div class="acoes-compartilhar">
        {#if suportaShare}
          <button
            type="button"
            class="btn-acao-share"
            onclick={handleCompartilharNativo}
          >
            <Icone nome="compartilhar" tamanho="1.1em" />
            <span>Compartilhar via WhatsApp / App</span>
          </button>
        {/if}

        <button
          type="button"
          class="btn-acao-link"
          onclick={handleCopiarLink}
        >
          <Icone nome={copiadoLink ? 'confirmado' : 'elo'} tamanho="1.1em" />
          <span>{copiadoLink ? 'Link Copiado!' : 'Copiar Link Completo'}</span>
        </button>
      </div>
    </div>
  </div>
</Dialogo>

<style>
  .modal-compartilhar {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 12px;
  }

  .header-titulo-grupo {
    display: flex;
    align-items: center;
    gap: 10px;
    color: var(--text-primary);
  }

  .header-titulo-grupo h3 {
    margin: 0;
    font-size: var(--texto-titulo);
    font-weight: 700;
  }

  .btn-fechar {
    background: transparent;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    padding: 6px;
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: color 0.15s ease, background 0.15s ease;
  }

  .btn-fechar:hover {
    color: var(--text-primary);
    background: rgba(var(--veu), 0.08);
  }

  .modal-corpo {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
    text-align: center;
  }

  .instrucao {
    margin: 0;
    font-size: var(--texto-apoio);
    color: var(--text-secondary);
    line-height: 1.4;
  }

  .qr-container {
    background: #ffffff;
    padding: 12px;
    border-radius: var(--radius-md);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .qr-svg {
    width: 180px;
    height: 180px;
    display: block;
  }

  .pin-card {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 10px 14px;
    box-sizing: border-box;
  }

  .pin-info {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 2px;
  }

  .pin-label {
    font-size: var(--texto-micro);
    color: var(--text-muted);
    font-weight: 700;
    letter-spacing: 0.05em;
  }

  .pin-numero {
    font-family: var(--fonte-numeros);
    font-size: var(--texto-titulo-forte);
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: 0.1em;
  }

  .btn-copiar-pin {
    background: rgba(var(--veu), 0.08);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-sm);
    color: var(--text-primary);
    padding: 8px 12px;
    font-size: var(--texto-legenda);
    font-weight: 600;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 6px;
    transition: all 0.15s ease;
  }

  .btn-copiar-pin:hover {
    background: rgba(var(--veu), 0.15);
  }

  .acoes-compartilhar {
    display: flex;
    flex-direction: column;
    gap: 10px;
    width: 100%;
  }

  .btn-acao-share {
    background: var(--acento-info-forte);
    color: #ffffff;
    border: none;
    border-radius: var(--radius-md);
    padding: 12px 16px;
    font-size: var(--texto-corpo);
    font-weight: 700;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    transition: background 0.15s ease;
    width: 100%;
  }

  .btn-acao-share:hover {
    background: var(--acento-info-ativo);
  }

  .btn-acao-link {
    background: transparent;
    color: var(--text-secondary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 10px 16px;
    font-size: var(--texto-apoio);
    font-weight: 600;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    transition: all 0.15s ease;
    width: 100%;
  }

  .btn-acao-link:hover {
    color: var(--text-primary);
    border-color: rgba(var(--veu), 0.25);
    background: rgba(var(--veu), 0.04);
  }
</style>
