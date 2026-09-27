import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { compile } from 'svelte/compiler';
import {
  suportaTelaCheia,
  estaEmTelaCheia,
  solicitarTelaCheia,
  sairDaTelaCheia,
  observarTelaCheia,
  podeOcultarControles,
} from '../src/lib/telaCheia.js';

function documentoFalso({ habilitada = true, aceita = true, entraDeFato = true, prefixo = '' } = {}) {
  const ouvintes = {};
  const d = {
    fullscreenElement: null,
    addEventListener(nome, fn) { (ouvintes[nome] ??= new Set()).add(fn); },
    removeEventListener(nome, fn) { ouvintes[nome]?.delete(fn); },
    emitir(nome) { for (const fn of ouvintes[nome] ?? []) fn(); },
    ouvintes,
  };
  const pedir = async () => {
    if (!aceita) throw new TypeError('Permissions check failed');
    if (entraDeFato) d.fullscreenElement = d.documentElement;
    d.emitir('fullscreenchange');
  };
  d.documentElement = prefixo === 'webkit' ? { webkitRequestFullscreen: pedir } : { requestFullscreen: pedir };
  if (prefixo === 'webkit') d.webkitFullscreenEnabled = habilitada;
  else d.fullscreenEnabled = habilitada;
  d.exitFullscreen = async () => { d.fullscreenElement = null; d.emitir('fullscreenchange'); };
  return d;
}

test('sem suporte, informa indisponibilidade sem tentar', async () => {
  const d = documentoFalso({ habilitada: false });
  assert.equal(suportaTelaCheia(d), false);
  assert.deepEqual(await solicitarTelaCheia(d), { ok: false, motivo: 'indisponivel' });
  assert.equal(estaEmTelaCheia(d), false);
});

test('recusa do navegador não vira estado de tela cheia', async () => {
  const d = documentoFalso({ aceita: false });
  assert.deepEqual(await solicitarTelaCheia(d), { ok: false, motivo: 'recusada' });
  assert.equal(estaEmTelaCheia(d), false);
});

test('promise resolvida sem entrar de fato também conta como recusa', async () => {
  const d = documentoFalso({ entraDeFato: false });
  assert.deepEqual(await solicitarTelaCheia(d), { ok: false, motivo: 'recusada' });
});

test('entrada confirmada pelo estado real, inclusive com prefixo webkit', async () => {
  const d = documentoFalso();
  assert.deepEqual(await solicitarTelaCheia(d), { ok: true });
  assert.equal(estaEmTelaCheia(d), true);

  const w = documentoFalso({ prefixo: 'webkit' });
  w.webkitFullscreenElement = null;
  w.documentElement.webkitRequestFullscreen = async () => { w.webkitFullscreenElement = w.documentElement; };
  assert.deepEqual(await solicitarTelaCheia(w), { ok: true });
});

test('observador acompanha saída externa e limpa os listeners', async () => {
  const d = documentoFalso();
  const estados = [];
  const parar = observarTelaCheia((ativo) => estados.push(ativo), d);
  await solicitarTelaCheia(d);
  // Saída pelo sistema (Esc, Voltar do Android, troca de app).
  d.fullscreenElement = null;
  d.emitir('fullscreenchange');
  assert.deepEqual(estados, [true, false]);
  parar();
  assert.equal(d.ouvintes.fullscreenchange.size, 0);
  await sairDaTelaCheia(d); // fora da tela cheia: não faz nada
});

test('controles só se escondem sem modal, foco de teclado ou erro', () => {
  assert.equal(podeOcultarControles(), true);
  assert.equal(podeOcultarControles({ modalAberto: true }), false);
  assert.equal(podeOcultarControles({ focoDeTeclado: true }), false);
  assert.equal(podeOcultarControles({ erroPendente: true }), false);
});

const sala = readFileSync(new URL('../src/components/SalaQuadra.svelte', import.meta.url), 'utf8');

test('sala compila sem avisos e pede tela cheia direto no gesto', () => {
  assert.equal(compile(sala, { filename: 'SalaQuadra.svelte' }).warnings.length, 0);
  assert.match(sala, /onclick=\{alternarTelaCheia\}/);
  assert.match(sala, /observarTelaCheia\(/);
  assert.match(sala, /aria-pressed=\{telaCheia\}/);
});

test('toque que revela os controles não aciona o que estava oculto', () => {
  assert.match(sala, /onclickcapture=\{engolirCliqueDeRevelacao\}/);
});

test('revelar controles não muda o layout do palco do espectador', () => {
  const manual = readFileSync(new URL('../src/components/PlacarManual.svelte', import.meta.url), 'utf8');
  assert.match(sala, /class:em-modo-imersivo=\{!podeControlar\}/);
  assert.match(sala, /modoImersivo=\{true\}\s*controlesOcultos=\{modoImersivo\}/);
  assert.match(sala, /\.em-modo-imersivo > \.barra-sala \{\s*position: absolute;/);
  assert.match(manual, /\{#if controlesOcultos\}/);
});
