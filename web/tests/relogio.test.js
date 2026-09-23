import { test } from 'node:test';
import assert from 'node:assert/strict';
import { ehDonoDoRelogio, mostrarChaveRelogio } from '../src/lib/relogio.js';
import { ICONES } from '../src/lib/icones.js';

test('só eli, em qualquer caixa, abre o vínculo do relógio', () => {
  for (const apelido of ['eli', 'Eli', 'ELI', ' eLi ']) assert.equal(ehDonoDoRelogio(apelido), true);
  for (const apelido of ['Rafa', 'eli2', 'elisa', 'eli.relogio', '', null, undefined]) {
    assert.equal(ehDonoDoRelogio(apelido), false);
  }
});

test('chave aparece para quem tem relógio ou para o admin desligar', () => {
  assert.equal(mostrarChaveRelogio({ temRelogio: true, ligada: false, ehAdmin: false }), true);
  assert.equal(mostrarChaveRelogio({ temRelogio: false, ligada: true, ehAdmin: true }), true);
  assert.equal(mostrarChaveRelogio({ temRelogio: false, ligada: true, ehAdmin: false }), false);
  assert.equal(mostrarChaveRelogio({ temRelogio: false, ligada: false, ehAdmin: true }), false);
});

test('ícone do relógio existe no conjunto embutido', () => {
  assert.ok(Array.isArray(ICONES.relogio) && ICONES.relogio.length > 0);
});
