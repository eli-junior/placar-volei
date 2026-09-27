import { mount } from 'svelte';
import App from './App.svelte';
import './app.css';
import { aplicarTema, lerTemaSol } from './lib/tema.js';

// Antes do mount: sem piscar o tema escuro para quem usa o Modo Sol.
aplicarTema(lerTemaSol());

const app = mount(App, {
  target: document.getElementById('app'),
});

export default app;
