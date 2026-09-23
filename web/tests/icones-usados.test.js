import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { ICONES } from '../src/lib/icones.js';

/**
 * Nome de ícone inexistente não quebra o build: `formasDoIcone` devolve lista
 * vazia e o botão aparece como um círculo em branco. Foi assim que a
 * engrenagem das configurações ficou invisível desde a CV2.
 */
test('todo ícone usado nos componentes existe no conjunto', () => {
  const pasta = new URL('../src/components/', import.meta.url);
  const usados = new Set();
  for (const arquivo of readdirSync(pasta).filter(n => n.endsWith('.svelte'))) {
    const fonte = readFileSync(new URL(arquivo, pasta), 'utf8');
    for (const [, bloco] of fonte.matchAll(/<Icone\b([^>]*)>/g)) {
      // `nome="sol"` ou literais em expressão: `nome={temaSol ? 'lua' : 'sol'}`.
      for (const [, literal, fixo] of bloco.matchAll(/'([a-z]+)'|nome="([a-z]+)"/g)) usados.add(literal ?? fixo);
    }
  }
  const faltando = [...usados].filter(nome => !ICONES[nome]);
  assert.ok(usados.has('engrenagem'));
  assert.deepEqual(faltando, []);
});
