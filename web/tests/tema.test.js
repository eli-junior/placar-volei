import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { aplicarTema, guardarTema, lerTemaSol } from '../src/lib/tema.js';

test('tema lido, aplicado e guardado num lugar só', () => {
  const dados = {};
  const armazenamento = { getItem: k => dados[k] ?? null, setItem: (k, v) => { dados[k] = v; } };
  assert.equal(lerTemaSol(armazenamento), false);
  guardarTema(true, armazenamento);
  assert.equal(lerTemaSol(armazenamento), true);
  const attrs = {};
  const documento = { documentElement: { setAttribute: (k, v) => { attrs[k] = v; }, removeAttribute: k => { delete attrs[k]; } } };
  aplicarTema(true, documento);
  assert.equal(attrs['data-tema'], 'sol');
  aplicarTema(false, documento);
  assert.equal('data-tema' in attrs, false);
});

test('tema é aplicado antes do mount e não duplicado nos componentes', () => {
  const main = readFileSync(new URL('../src/main.js', import.meta.url), 'utf8');
  assert.ok(main.indexOf('aplicarTema(lerTemaSol())') < main.indexOf('mount(App'));
  for (const f of ['SalaQuadra.svelte', 'HomePlacar.svelte']) {
    const fonte = readFileSync(new URL(`../src/components/${f}`, import.meta.url), 'utf8');
    assert.doesNotMatch(fonte, /placar:tema/);
  }
});

test('QR do compartilhamento usa a assinatura certa do gerador', () => {
  const modal = readFileSync(new URL('../src/components/ModalCompartilhar.svelte', import.meta.url), 'utf8');
  assert.match(modal, /gerarQrCode\(urlCompleta, \{ nivel: 'M' \}\)/);
});
