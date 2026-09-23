<script>
  import { onMount } from 'svelte';
  import { ehDonoDoRelogio, mostrarChaveRelogio } from '../lib/relogio.js';

  // Chave "Controlar pelo Relógio" (CV3.DS1.US2). O estado vem da sala, não
  // de preferência local: ligada, o servidor recusa ponto e desfazer do site.
  let { quadra, eu, participantes = [], ocupado = false, onAlternar = (ativo) => {} } = $props();

  let temRelogio = $state(false);
  const ligada = $derived(Boolean(quadra?.controle_relogio));
  const dono = $derived(participantes.find(p => p.id === quadra?.controle_relogio)?.apelido || 'eli');
  const visivel = $derived(mostrarChaveRelogio({ temRelogio, ligada, ehAdmin: eu?.papel === 'ADMIN' }));

  onMount(async () => {
    if (!ehDonoDoRelogio(eu?.apelido)) return;
    try {
      const resposta = await fetch(`/api/quadras/${quadra.id}/watch`);
      if (resposta.ok) temRelogio = (await resposta.json()).devices.length > 0;
    } catch {
      // Sem a consulta a chave fica oculta; o vínculo continua no ícone do relógio.
    }
  });
</script>

{#if visivel}
  <div class="chave-relogio">
    <label class="chave-label">
      <input
        type="checkbox"
        role="switch"
        checked={ligada}
        disabled={ocupado}
        onchange={(e) => onAlternar(e.currentTarget.checked)}
      />
      <span>Controlar pelo Relógio</span>
    </label>
    <p class="chave-ajuda">
      {ligada
        ? `Ligado: só o relógio de ${dono} marca pontos. O site mostra o placar e continua configurando a partida.`
        : 'Desligado: os pontos são marcados pelo telefone.'}
    </p>
  </div>
{/if}

<style>
  .chave-relogio {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 12px;
    border: 1px solid var(--border-color);
    border-radius: 10px;
  }

  .chave-label {
    display: flex;
    align-items: center;
    gap: 10px;
    min-height: 44px;
    font-weight: 700;
    color: var(--text-primary);
    cursor: pointer;
  }

  .chave-label input {
    width: 22px;
    height: 22px;
  }

  .chave-ajuda {
    margin: 0;
    font-size: 0.85rem;
    color: var(--text-secondary);
  }
</style>
