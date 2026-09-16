<script>
  import Dialogo from './Dialogo.svelte';
  import Icone from './Icone.svelte';

  let { quadra, onEntrar, onVoltar, submetendo = false } = $props();
  let apelido = $state('');
  let erro = $state('');

  $effect(() => {
    if (typeof localStorage !== 'undefined' && !apelido) {
      const salvo = localStorage.getItem('placar_ultimo_apelido');
      if (salvo) apelido = salvo;
    }
  });

  function handleSubmit(e) {
    e.preventDefault();
    const apelidoLimpo = apelido.trim();
    if (!apelidoLimpo) {
      erro = 'Informe seu apelido para entrar na quadra.';
      return;
    }
    if (typeof localStorage !== 'undefined') {
      try {
        localStorage.setItem('placar_ultimo_apelido', apelidoLimpo);
      } catch {}
    }
    erro = '';
    onEntrar(apelidoLimpo);
  }
</script>

<Dialogo
  rotuladoPor="titulo-entrar-quadra"
  variante="centro"
  largura="400px"
  onFechar={onVoltar}
>
  <div class="modal-entrar">
    <header class="modal-header">
      <div>
        <span class="quadra-tag">Entrar na quadra</span>
        <h3 id="titulo-entrar-quadra">{quadra?.nome || 'Quadra ' + (quadra?.id || '')}</h3>
      </div>
      <button type="button" class="btn-fechar" onclick={onVoltar} aria-label="Fechar modal">
        <Icone nome="fechar" tamanho="1.1em" />
      </button>
    </header>

    <div class="info-box">
      <Icone nome="informacao" tamanho="1.1em" class="info-icon" />
      <p>
        Sem cadastro e sem senha. Informe seu apelido para aparecer na quadra e acompanhar o placar ao vivo.
      </p>
    </div>

    <form onsubmit={handleSubmit} class="form-entrar">
      <div class="campo-grupo">
        <label for="apelido-input">Seu Apelido</label>
        <input
          id="apelido-input"
          type="text"
          placeholder="Ex: Eli, Carlos, Marina..."
          bind:value={apelido}
          maxlength="30"
          required
          disabled={submetendo}
        />
      </div>

      {#if erro}
        <p class="erro-msg">{erro}</p>
      {/if}

      <div class="modal-actions">
        <button type="button" class="btn-secondary" onclick={onVoltar} disabled={submetendo}>
          Voltar
        </button>
        <button type="submit" class="btn-confirm" disabled={submetendo}>
          {submetendo ? 'Entrando...' : 'Entrar no Jogo'}
        </button>
      </div>
    </form>
  </div>
</Dialogo>

<style>
  .modal-entrar {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 12px;
  }

  .quadra-tag {
    font-size: var(--texto-micro);
    color: #38bdf8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 700;
  }

  .modal-header h3 {
    margin: 4px 0 0 0;
    font-size: var(--texto-titulo);
    color: var(--text-primary);
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
  }

  .info-box {
    background: rgba(56, 189, 248, 0.08);
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: var(--radius-sm);
    padding: 10px 12px;
    display: flex;
    gap: 10px;
    align-items: flex-start;
  }

  .info-box :global(.info-icon) {
    color: #38bdf8;
    flex-shrink: 0;
    margin-top: 2px;
  }

  .info-box p {
    margin: 0;
    font-size: var(--texto-legenda);
    color: var(--text-secondary);
    line-height: 1.4;
  }

  .form-entrar {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .campo-grupo {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .campo-grupo label {
    font-size: var(--texto-apoio);
    color: var(--text-primary);
    font-weight: 600;
  }

  .campo-grupo input {
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 12px 14px;
    font-size: var(--texto-corpo);
    color: var(--text-primary);
    box-sizing: border-box;
    width: 100%;
  }

  .campo-grupo input:focus {
    outline: none;
    border-color: #0284c7;
  }

  .erro-msg {
    margin: 0;
    color: #f87171;
    font-size: var(--texto-legenda);
  }

  .modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 4px;
  }

  .btn-secondary {
    background: transparent;
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 10px 18px;
    color: var(--text-secondary);
    font-size: var(--texto-apoio);
    font-weight: 600;
    cursor: pointer;
  }

  .btn-confirm {
    background: #0284c7;
    border: none;
    border-radius: var(--radius-md);
    padding: 10px 22px;
    color: #ffffff;
    font-size: var(--texto-apoio);
    font-weight: 700;
    cursor: pointer;
    transition: background 0.15s ease;
  }

  .btn-confirm:hover {
    background: #0369a1;
  }

  .btn-confirm:disabled,
  .btn-secondary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
</style>
