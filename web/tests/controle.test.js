import { test } from 'node:test';
import assert from 'node:assert/strict';
import { podePassarControle } from '../src/lib/controle.js';

const ctx = { euId: 'eli', controleId: 'eli', ehAdmin: true };

test('admin pode passar o controle para controlador, inclusive o relógio', () => {
  assert.equal(podePassarControle({ id: 'relogio', papel: 'CONTROLADOR' }, ctx), true);
  assert.equal(podePassarControle({ id: 'ana', papel: 'ADMIN' }, ctx), true);
});

test('não oferece passar para espectador, para si, para quem já controla ou sem ser admin', () => {
  assert.equal(podePassarControle({ id: 'rafa', papel: 'ESPECTADOR' }, ctx), false);
  assert.equal(podePassarControle({ id: 'eli', papel: 'ADMIN' }, ctx), false);
  assert.equal(podePassarControle({ id: 'relogio', papel: 'CONTROLADOR' }, { ...ctx, controleId: 'relogio' }), false);
  assert.equal(podePassarControle({ id: 'relogio', papel: 'CONTROLADOR' }, { ...ctx, ehAdmin: false }), false);
});
