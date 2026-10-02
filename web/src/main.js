import { mount } from 'svelte';
import App from './App.svelte';
import AppCasca from './AppCasca.svelte';
import { emCascaEmbarcada } from './lib/casca.js';
import './app.css';
import { aplicarTema, lerTemaSol } from './lib/tema.js';

// Antes do mount: sem piscar o tema escuro para quem usa o Modo Sol.
aplicarTema(lerTemaSol());

// No APK a interface embarcada abre a escolha de quadra (CV7.TS1) e a quadra
// local (CV7.US1); no navegador e nas páginas do servidor, o app de sempre.
// SPIKE CV7.TS3 (descartável): build de teste com VITE_SPIKE=1.
const app = import.meta.env.VITE_SPIKE
  ? import('./Spike.svelte').then(({ default: Spike }) => mount(Spike, { target: document.getElementById('app') }))
  : emCascaEmbarcada()
  ? mount(AppCasca, {
      target: document.getElementById('app'),
      props: { servidorPadrao: import.meta.env.VITE_PLACAR_SERVIDOR ?? '' },
    })
  : mount(App, { target: document.getElementById('app') });

export default app;
