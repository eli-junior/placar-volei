import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { definirBarrasEscondidas } from '../src/lib/barrasDoSistema.js';

const sala = readFileSync(new URL('../src/components/SalaQuadra.svelte', import.meta.url), 'utf8');
const manual = readFileSync(new URL('../src/components/PlacarManual.svelte', import.meta.url), 'utf8');
const plugin = readFileSync(new URL('../../android/app/src/main/java/br/com/placarvolei/BarrasDoSistemaPlugin.java', import.meta.url), 'utf8');
const atividade = readFileSync(new URL('../../android/app/src/main/java/br/com/placarvolei/MainActivity.java', import.meta.url), 'utf8');

test('fora do APK esconder as barras é no-op', async () => {
  assert.equal(await definirBarrasEscondidas(true), false);
  assert.equal(await definirBarrasEscondidas(false), false);
});

test('com a ponte própria do APK, esconder e mostrar chegam ao nativo em ordem', async () => {
  const chamadas = [];
  globalThis.window = { PlacarBarras: { esconder: () => chamadas.push('esconder'), mostrar: () => chamadas.push('mostrar') } };
  try {
    const a = definirBarrasEscondidas(true);
    const b = definirBarrasEscondidas(false);
    const c = definirBarrasEscondidas(true);
    assert.deepEqual(await Promise.all([a, b, c]), [true, true, true]);
    assert.deepEqual(chamadas, ['esconder', 'mostrar', 'esconder']);
  } finally {
    delete globalThis.window;
  }
});

test('a sala esconde as barras só no modo de exibição e as devolve ao sair', () => {
  assert.match(sala, /if \(podeControlar\) return;\s*definirBarrasEscondidas\(true\);\s*return \(\) => \{ definirBarrasEscondidas\(false\); \};/);
});

test('o plugin nativo está registrado e usa o modo imersivo por deslize', () => {
  assert.match(atividade, /registerPlugin\(BarrasDoSistemaPlugin\.class\)/);
  assert.match(plugin, /@CapacitorPlugin\(name = "BarrasDoSistema"\)/);
  assert.match(plugin, /BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE/);
  assert.match(atividade, /addJavascriptInterface\(new PonteBarras\(\), "PlacarBarras"\)/);
});

test('na exibição o rodapé flutua sobre o placar e a dica some sozinha', () => {
  assert.match(manual, /\.modo-imersivo \.rodape \{[^}]*position: absolute/);
  assert.match(manual, /animation: dica-some 5s forwards/);
});

test('o dígito só cresce com a caixa aparada ao glifo, para não cobrir o nome da equipe', () => {
  const resultado = readFileSync(new URL('../src/components/PlacarResultado.svelte', import.meta.url), 'utf8');
  assert.match(resultado, /@supports \(text-box: trim-both cap alphabetic\) \{\s*strong:not\(\.tres-digitos\) \{[^}]*text-box: trim-both cap alphabetic;[^}]*100cqh/);
});
