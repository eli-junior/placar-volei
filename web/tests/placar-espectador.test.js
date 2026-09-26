import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { compile } from 'svelte/compiler';

const resultado = readFileSync(
  new URL('../src/components/PlacarResultado.svelte', import.meta.url),
  'utf8',
);
const espectador = readFileSync(
  new URL('../src/components/PlacarManual.svelte', import.meta.url),
  'utf8',
);
const sala = readFileSync(
  new URL('../src/components/SalaQuadra.svelte', import.meta.url),
  'utf8',
);

test('painel esportivo do espectador compila sem avisos', () => {
  assert.equal(compile(resultado, { filename: 'PlacarResultado.svelte' }).warnings.length, 0);
  assert.equal(compile(espectador, { filename: 'PlacarManual.svelte' }).warnings.length, 0);
});

test('representação recebe placar pronto e não depende de sala ou transporte', () => {
  assert.match(resultado, /pontosA = 0/);
  assert.match(resultado, /pontosB = 0/);
  assert.match(resultado, /ladosInvertidos = false/);
  assert.doesNotMatch(resultado, /WebSocket|fetch\(|quadra|onMarcarPonto/);
});

test('pontos escalam pela largura e altura e preservam números tabulares', () => {
  assert.match(resultado, /container-type: size/);
  assert.match(resultado, /min\(50cqw, 74cqh\)/);
  assert.match(resultado, /font-variant-numeric: tabular-nums/);
  assert.match(resultado, /tresDigitosA/);
  assert.match(resultado, /strong\.tres-digitos \{ font-size: clamp\(5rem, min\(27cqw, 54cqh\), 18rem\); \}/);
});

test('espectador deixa os cartões dobráveis fora da nova composição', () => {
  assert.match(espectador, /PlacarResultado/);
  assert.doesNotMatch(espectador, /CartaoDobravel/);
  assert.match(espectador, /Linha do tempo/);
  assert.match(espectador, /Inverter lados/);
});

test('metadados operacionais não antecedem o placar do espectador', () => {
  assert.match(sala, /\{#if podeControlar\}\s*<section class="quadra-hero"/);
  assert.match(sala, /\{#if podeControlar \|\| avisoRelogio \|\| !wsConectado \|\| erro\}/);
  assert.match(espectador, /class="contexto"/);
});

test('painel do espectador ocupa a altura útil no modo imersivo', () => {
  assert.match(sala, /class="placar-espectador-wrapper"/);
  assert.match(sala, /\.em-modo-imersivo \.placar-espectador-wrapper\s*\{[^}]*flex: 1 1 auto;[^}]*height: 100%;/s);
  assert.match(espectador, /grid-template-areas:\s*'contexto'\s*'vitoria'\s*'resultado'\s*'rodape'/);
});

test('feedback de atualização respeita movimento reduzido', () => {
  assert.match(resultado, /movimentoReduzido \? 0 : 360/);
  assert.match(resultado, /prefers-reduced-motion: reduce/);
  assert.match(resultado, /aria-live="polite"/);
});
