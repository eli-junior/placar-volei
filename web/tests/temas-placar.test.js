import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { compile } from 'svelte/compiler';

const ler = nome => readFileSync(new URL(`../src/components/${nome}`, import.meta.url), 'utf8');
const classico = ler('PlacarClassico.svelte');
const modal = ler('ModalConfigurarPartida.svelte');
const operacao = ler('Placar.svelte');
const espectador = ler('PlacarManual.svelte');
const sala = ler('SalaQuadra.svelte');

test('componentes dos temas compilam sem avisos', () => {
  for (const [nome, fonte] of [
    ['PlacarClassico.svelte', classico],
    ['ModalConfigurarPartida.svelte', modal],
    ['Placar.svelte', operacao],
  ]) {
    assert.equal(compile(fonte, { filename: nome }).warnings.length, 0, nome);
  }
});

test('representação clássica é pura: sem sala, transporte ou comandos', () => {
  assert.match(classico, /CartaoDobravel/);
  assert.doesNotMatch(classico, /WebSocket|fetch\(|quadra|onMarcarPonto/);
});

test('tema vem da sala para todos os papéis, com esportivo como padrão', () => {
  const usos = sala.match(/temaPlacar=\{quadra\?\.tema_placar \|\| 'esportivo'\}/g) ?? [];
  assert.equal(usos.length, 3);
  assert.match(espectador, /temaPlacar === 'classico'/);
  assert.match(operacao, /temaPlacar === 'esportivo'/);
});

test('seletor administrativo envia tema_placar e não mexe em claro/escuro', () => {
  assert.match(modal, /Visual do placar/);
  assert.match(modal, /tema_placar: temaVisual/);
  assert.doesNotMatch(modal, /data-tema|localStorage/);
});

test('tema da sala não usa armazenamento local', () => {
  assert.doesNotMatch(sala, /localStorage\.setItem\([^)]*tema_placar/);
});

test('cabeçalho em uma linha com alvos de 44px e status em bolinha', () => {
  assert.match(sala, /\.btn-topo,\s*\.chip-codigo \{\s*min-height: 44px;/);
  assert.match(sala, /role="img"\s*aria-label=\{conexaoVisivel\.rotulo\}/);
  assert.doesNotMatch(sala, /Ao vivo/);
});
