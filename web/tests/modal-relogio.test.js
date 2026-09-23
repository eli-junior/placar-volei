import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { compile } from 'svelte/compiler';

/**
 * Em template Svelte, `{8}` dentro de um atributo é expressão: o
 * `pattern="[0-9]{8}"` saía como `[0-9]8` e o navegador recusava qualquer
 * código de oito dígitos do relógio antes de chamar a API.
 */
test('campo do código do relógio exige exatamente oito dígitos', () => {
  const fonte = readFileSync(new URL('../src/components/ModalRelogio.svelte', import.meta.url), 'utf8');
  const { js } = compile(fonte, { filename: 'ModalRelogio.svelte' });
  assert.match(js.code, /pattern['"`],\s*['"`]\[0-9\]\{8\}['"`]/);
  assert.doesNotMatch(js.code, /\[0-9\]8/);
  assert.match('15056015', /^(?:[0-9]{8})$/);
});
