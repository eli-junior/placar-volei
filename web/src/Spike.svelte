<script>
  // SPIKE CV7.TS3 (descartável, só com VITE_SPIKE=1): o JS roda com a tela
  // apagada? Anota em `spike_js` cada tique nativo recebido, cada tique de
  // setInterval, o wake lock e as mudanças de visibilidade.
  import { onMount } from 'svelte';
  import { registerPlugin } from '@capacitor/core';
  import { Preferences } from '@capacitor/preferences';

  const Spike = registerPlugin('Spike');
  let estado = $state('parado');
  let nativos = $state(0);
  let timers = $state(0);
  let wake = $state('não pedido');
  let log = [];
  let sentinela = null;

  async function anotar(tipo, extra = {}) {
    log.push({ tipo, t: Date.now(), ...extra });
    await Preferences.set({ key: 'spike_js', value: JSON.stringify(log) });
  }

  async function pedirWake() {
    try {
      if (!navigator.wakeLock) { wake = 'API ausente'; await anotar('wake', { r: 'ausente' }); return; }
      sentinela = await navigator.wakeLock.request('screen');
      wake = 'ativo';
      await anotar('wake', { r: 'ativo' });
      sentinela.addEventListener('release', () => { wake = 'liberado'; anotar('wake', { r: 'liberado' }); });
    } catch (e) {
      wake = `erro: ${e.name}`;
      await anotar('wake', { r: `erro ${e.name}: ${e.message}` });
    }
  }

  let iniciado = false;
  async function iniciar() {
    if (iniciado) return;
    iniciado = true;
    log = [];
    estado = 'rodando';
    await Preferences.remove({ key: 'spike_js' });
    await anotar('inicio');
    await pedirWake();
    await Spike.addListener('tique', (e) => { nativos += 1; anotar('nativo', { n: e.n, tn: e.t }); });
    setInterval(() => { timers += 1; anotar('timer', { n: timers }); }, 5000);
    document.addEventListener('visibilitychange', () => anotar('vis', { v: document.visibilityState }));
    await Spike.servico();
    await anotar('servico');
    await Spike.iniciar();
  }

  onMount(() => {});
</script>

<main style="padding: 40px 16px; color: #fff; font-family: sans-serif;">
  <h1>Spike CV7.TS3</h1>
  <p>Estado: {estado}</p>
  <p>Tiques nativos recebidos: {nativos}</p>
  <p>Tiques do setInterval: {timers}</p>
  <p>Wake lock: {wake}</p>
  <button type="button" onclick={iniciar} style="min-height: 64px; padding: 0 24px; font-size: 1.2rem;">Iniciar teste</button>
</main>
