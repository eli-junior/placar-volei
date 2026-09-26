import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { compile } from 'svelte/compiler';

const fonte = readFileSync(
  new URL('../src/components/HomePlacar.svelte', import.meta.url),
  'utf8',
);

test('Home esportiva compila sem avisos do Svelte', () => {
  const resultado = compile(fonte, { filename: 'HomePlacar.svelte' });
  assert.equal(resultado.warnings.length, 0);
});

test('Home começa pelo fluxo de acompanhar e mantém o erro junto ao formulário', () => {
  assert.match(fonte, /let abaAtiva = \$state\('acompanhar'\)/);
  assert.match(fonte, /id="painel-acompanhar"[\s\S]*?role="alert"[\s\S]*?id="codigo-quadra"/);
});

test('selecionar uma quadra preenche o código antes de tentar entrar', () => {
  const inicio = fonte.indexOf('function selecionarQuadraAtiva');
  const fim = fonte.indexOf('function mudarAbaPorTeclado');
  const funcao = fonte.slice(inicio, fim);
  assert.ok(funcao.indexOf("abaAtiva = 'acompanhar'") < funcao.indexOf('onEntrarQuadra'));
  assert.ok(funcao.indexOf('codigoQuadra = quadra.id') < funcao.indexOf('onEntrarQuadra'));
});

test('recusa ao entrar devolve o foco ao apelido que precisa ser corrigido', () => {
  assert.match(fonte, /if \(!erro \|\| abaAtiva !== 'acompanhar' \|\| !codigoQuadra\) return/);
  assert.match(fonte, /getElementById\('apelido-espectador'\)\?\.focus\(\)/);
});

test('modo claro escreve o valor sol esperado pelos tokens e o escuro remove o atributo', () => {
  assert.match(fonte, /setAttribute\('data-tema', 'sol'\)/);
  assert.match(fonte, /removeAttribute\('data-tema'\)/);
  assert.doesNotMatch(fonte, /toggleAttribute\('data-tema'/);
});
