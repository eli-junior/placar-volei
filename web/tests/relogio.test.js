import { test } from 'node:test';
import assert from 'node:assert/strict';
import { ehDonoDoRelogio } from '../src/lib/relogio.js';
import { ICONES } from '../src/lib/icones.js';

test('só eli, em qualquer caixa, abre o vínculo do relógio', () => {
  for (const apelido of ['eli', 'Eli', 'ELI', ' eLi ']) assert.equal(ehDonoDoRelogio(apelido), true);
  for (const apelido of ['Rafa', 'eli2', 'elisa', 'eli.relogio', '', null, undefined]) {
    assert.equal(ehDonoDoRelogio(apelido), false);
  }
});

test('ícone do relógio existe no conjunto embutido', () => {
  assert.ok(Array.isArray(ICONES.relogio) && ICONES.relogio.length > 0);
});
