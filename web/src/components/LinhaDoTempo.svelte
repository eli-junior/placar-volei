<script>
  import { slide } from 'svelte/transition';
  import Dialogo from './Dialogo.svelte';

  let {
    itens = [],
    prefersReducedMotion = false,
    equipeA = 'Equipe A',
    equipeB = 'Equipe B',
    pontosA = 0,
    pontosB = 0,
    onFechar = () => {},
  } = $props();

  let listaEl = $state(null);

  // Formata timestamp ISO para hora legível HH:MM:SS
  function formatarHora(isoString) {
    if (!isoString) return '';
    try {
      const data = new Date(isoString);
      return data.toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      });
    } catch {
      return '';
    }
  }

  // Rola automaticamente para o fim da lista quando novos itens chegam
  $effect(() => {
    if (listaEl && itens.length > 0) {
      const timer = setTimeout(() => {
        if (listaEl) {
          listaEl.scrollTo({ top: listaEl.scrollHeight, behavior: prefersReducedMotion ? 'instant' : 'smooth' });
        }
      }, 50);
      // Lista nova ou diálogo fechado antes dos 50 ms: o timer não sobrevive.
      return () => clearTimeout(timer);
    }
  });

</script>

<!-- Diálogo nativo (CV5.DS4.US2): foco preso dentro, fundo inerte, Esc
     e retorno do foco a quem abriu vêm do `Dialogo`. -->
<Dialogo
  rotuladoPor="titulo-linha-tempo"
  variante="folha"
  largura="580px"
  movimentoReduzido={prefersReducedMotion}
  {onFechar}
>
  <div class="modal-sheet">
    <!-- Header com Placar Resumido e Fechar -->
    <header class="sheet-header">
      <div class="header-info">
        <div class="header-top-row">
          <span class="icone-cabecalho">📜</span>
          <h3 id="titulo-linha-tempo" class="header-titulo">Linha do Tempo</h3>
        </div>
        <p class="header-sub">
          Placar Atual: <strong class="placar-txt">{equipeA} {pontosA} × {pontosB} {equipeB}</strong>
        </p>
      </div>

      <button
        type="button"
        class="btn-fechar"
        onclick={onFechar}
        aria-label="Fechar Linha do Tempo"
      >
        ✕
      </button>
    </header>

    <!-- Lista Cronológica dos Lances -->
    <div class="sheet-body" bind:this={listaEl}>
      {#if itens.length === 0}
        <div class="empty-state">
          <span class="empty-icon">🏐</span>
          <p class="empty-text">Nenhum lance registrado nesta partida ainda.</p>
        </div>
      {:else}
        <ul class="lista-lances">
          {#each itens as item, index (item.id || item.seq)}
            <li
              class="card-lance {item.anulado ? 'lance-anulado' : ''} {item.tipo === 'PONTO_DESFEITO' ? 'lance-desfeito' : ''}"
              in:slide={{ duration: prefersReducedMotion ? 0 : 200 }}
            >
              <!-- Marcador de Sequência e Ícone -->
              <div class="lance-lado">
                <span class="lance-seq">#{item.seq}</span>
                {#if item.tipo === 'PARTIDA_INICIADA'}
                  <span class="lance-badge badge-inicio">🏁 Início</span>
                {:else if item.tipo === 'PONTO_MARCADO'}
                  <span
                    class="lance-badge {item.equipe === 'A' ? 'badge-equipe-a' : 'badge-equipe-b'}"
                  >
                    +1 {item.equipe === 'A' ? equipeA : equipeB}
                  </span>
                {:else if item.tipo === 'PONTO_DESFEITO'}
                  <span class="lance-badge badge-desfeito">↺ Anulação</span>
                {:else if item.tipo === 'CONTROLE_ASSUMIDO'}
                  <span class="lance-badge badge-geral">Controle</span>
                {:else if item.tipo === 'PAPEL_ALTERADO'}
                  <span class="lance-badge badge-geral">Admin</span>
                {:else if item.tipo === 'PARTIDA_ENCERRADA'}
                  <span class="lance-badge badge-fim">🏆 Vitória</span>
                {:else}
                  <span class="lance-badge badge-geral">⚙️ Regra</span>
                {/if}
              </div>

              <!-- Detalhes do Lance e Autor -->
              <div class="lance-detalhes">
                <div class="lance-desc-row">
                  <span class="lance-desc {item.anulado ? 'desc-cortada' : ''}">
                    {item.descricao}
                  </span>
                  {#if item.anulado}
                    <span class="tag-anulado">Anulado</span>
                  {/if}
                </div>

                <div class="lance-meta">
                  {#if item.autor_apelido && item.autor_apelido !== 'Sistema'}
                    <span class="lance-autor">por <strong>{item.autor_apelido}</strong></span>
                  {/if}
                  <span class="lance-hora">{formatarHora(item.criado_em)}</span>
                </div>
              </div>

              <!-- Placar Resultante no Momento do Lance -->
              <div class="lance-placar">
                <span class="placar-resultado {item.anulado ? 'resultado-anulado' : ''}">
                  {item.pontos_a} × {item.pontos_b}
                </span>
              </div>
            </li>
          {/each}
        </ul>
      {/if}
    </div>

    <!-- Rodapé Informativo -->
    <footer class="sheet-footer">
      <span class="auditoria-tag">🔒 Registro imutável append-only</span>
      <button type="button" class="btn-fechar-rodape" onclick={onFechar}>
        Fechar
      </button>
    </footer>
  </div>
</Dialogo>

<style>
  /* Caixa, fundo e cantos vêm da folha do `Dialogo`; aqui só o miolo que rola. */
  .modal-sheet {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-height: 0;
    overflow: hidden;
  }

  @media (max-height: 520px) {
    .sheet-header {
      padding: 10px 16px;
    }
    .sheet-footer {
      padding: 8px 16px;
    }
    .sheet-body {
      padding: 10px 14px;
      gap: 6px;
    }
  }

  /* Header */
  .sheet-header {
    padding: 16px 20px;
    background: rgba(var(--veu), 0.02);
    border-bottom: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
  }

  .header-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .header-top-row {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .icone-cabecalho {
    font-size: 1.25rem;
  }

  .header-titulo {
    font-size: 1.2rem;
    font-weight: 800;
    color: var(--texto-contraste);
    margin: 0;
  }

  .header-sub {
    font-size: 0.82rem;
    color: var(--text-muted);
    margin: 0;
  }

  .placar-txt {
    color: var(--text-primary);
  }

  .btn-fechar {
    background: rgba(var(--veu), 0.06);
    border: 1px solid rgba(var(--veu), 0.1);
    color: var(--text-secondary);
    border-radius: 999px;
    width: 34px;
    height: 34px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.95rem;
    cursor: pointer;
    transition: background 0.15s ease, color 0.15s ease;
  }

  .btn-fechar:hover {
    background: rgba(var(--veu), 0.14);
    color: var(--texto-contraste);
  }

  /* Body / Timeline */
  .sheet-body {
    padding: 14px 16px;
    overflow-y: auto;
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 8px;
    scroll-behavior: smooth;
  }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 48px 24px;
    gap: 12px;
    text-align: center;
  }

  .empty-icon {
    font-size: 2.5rem;
  }

  .empty-text {
    font-size: 0.92rem;
    color: var(--text-muted);
  }

  .lista-lances {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .card-lance {
    background: rgba(var(--veu), 0.03);
    border: 1px solid rgba(var(--veu), 0.06);
    border-radius: var(--radius-md);
    padding: 10px 14px;
    display: grid;
    grid-template-columns: auto 1fr auto;
    align-items: center;
    gap: 12px;
    transition: background 0.15s ease;
  }

  .card-lance:hover {
    background: rgba(var(--veu), 0.05);
  }

  .card-lance.lance-anulado {
    opacity: 0.55;
    background: rgba(239, 68, 68, 0.04);
    border-color: rgba(239, 68, 68, 0.15);
  }

  .card-lance.lance-desfeito {
    background: rgba(245, 158, 11, 0.05);
    border-color: rgba(245, 158, 11, 0.2);
  }

  /* Lado Esquerdo: Seq & Badge */
  .lance-lado {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .lance-seq {
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--text-muted);
    min-width: 24px;
  }

  .lance-badge {
    font-size: 0.72rem;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 999px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    white-space: nowrap;
  }

  .badge-inicio {
    background: rgba(148, 163, 184, 0.15);
    color: var(--texto-medio);
  }

  .badge-equipe-a {
    background: rgba(6, 182, 212, 0.18);
    color: var(--badge-time-a-texto);
    border: 1px solid rgba(6, 182, 212, 0.3);
  }

  .badge-equipe-b {
    background: rgba(249, 115, 22, 0.18);
    color: var(--badge-time-b-texto);
    border: 1px solid rgba(249, 115, 22, 0.3);
  }

  .badge-desfeito {
    background: rgba(245, 158, 11, 0.18);
    color: var(--badge-marca-texto);
    border: 1px solid rgba(245, 158, 11, 0.3);
  }

  .badge-fim {
    background: rgba(234, 179, 8, 0.2);
    color: var(--badge-fim-texto);
    border: 1px solid rgba(234, 179, 8, 0.35);
  }

  .badge-geral {
    background: rgba(168, 85, 247, 0.18);
    color: var(--badge-geral-texto);
  }

  /* Centro: Detalhes */
  .lance-detalhes {
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 0;
  }

  .lance-desc-row {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
  }

  .lance-desc {
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--texto-contraste);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .lance-desc.desc-cortada {
    text-decoration: line-through;
    color: var(--text-muted);
  }

  .tag-anulado {
    font-size: 0.65rem;
    font-weight: 700;
    color: var(--estado-erro);
    background: rgba(239, 68, 68, 0.15);
    padding: 1px 6px;
    border-radius: 4px;
    text-transform: uppercase;
  }

  .lance-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.74rem;
    color: var(--text-muted);
  }

  .lance-autor strong {
    color: var(--text-secondary);
  }

  .lance-hora {
    font-variant-numeric: tabular-nums;
  }

  /* Lado Direito: Placar Resultante */
  .lance-placar {
    display: flex;
    align-items: center;
    justify-content: flex-end;
  }

  .placar-resultado {
    font-family: var(--font-display);
    font-size: 1.15rem;
    font-weight: 800;
    color: var(--texto-contraste);
    background: rgba(var(--veu), 0.05);
    padding: 4px 10px;
    border-radius: var(--radius-sm);
    font-variant-numeric: tabular-nums;
  }

  .placar-resultado.resultado-anulado {
    color: var(--text-muted);
    text-decoration: line-through;
  }

  /* Rodapé */
  .sheet-footer {
    padding: 12px 20px;
    background: rgba(var(--veu), 0.02);
    border-top: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .auditoria-tag {
    font-size: 0.74rem;
    color: var(--text-muted);
    font-weight: 500;
  }

  .btn-fechar-rodape {
    padding: 6px 16px;
    font-size: 0.85rem;
    font-weight: 600;
    background: rgba(var(--veu), 0.06);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-sm);
    color: var(--text-secondary);
    cursor: pointer;
    transition: background 0.15s ease, color 0.15s ease;
  }

  .btn-fechar-rodape:hover {
    background: rgba(var(--veu), 0.12);
    color: var(--texto-contraste);
  }
</style>
