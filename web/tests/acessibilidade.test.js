import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const ler = arquivo => readFileSync(new URL(`../src/${arquivo}`, import.meta.url), 'utf8');

test('linha do tempo usa o diálogo nativo (foco preso e retorno de foco)', () => {
  const linha = ler('components/LinhaDoTempo.svelte');
  assert.match(linha, /<Dialogo[\s\S]*rotuladoPor="titulo-linha-tempo"/);
  assert.doesNotMatch(linha, /role="dialog"/);
  assert.doesNotMatch(linha, /svelte:window onkeydown/);
});

test('movimento reduzido para toda animação infinita', () => {
  assert.match(ler('app.css'), /prefers-reduced-motion: reduce\)\s*\{[\s\S]*animation-iteration-count: 1 !important/);
});

test('só o botão que enviou fica ocupado', () => {
  const placar = ler('components/Placar.svelte');
  assert.doesNotMatch(placar, /aria-busy=\{enviando\}/);
  assert.match(placar, /aria-busy=\{enviando && origemEnvio === 'A'\}/);
  assert.doesNotMatch(placar, /Trocar Duplas/);
});

test('erro do apelido é anunciado e ligado ao campo', () => {
  const modal = ler('components/ModalEntrar.svelte');
  assert.match(modal, /id="apelido-erro" role="alert"/);
  assert.match(modal, /aria-describedby=\{erro \? 'apelido-erro' : undefined\}/);
});

test('região viva da sala nasce vazia e fica montada', () => {
  const sala = ler('components/SalaQuadra.svelte');
  assert.match(sala, /<div class="controle-painel"[^>]*aria-live="polite">/);
  assert.doesNotMatch(sala, /class="faixa-posse"[^>]*aria-live/);
});
