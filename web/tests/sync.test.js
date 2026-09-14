import { test } from 'node:test';
import assert from 'node:assert/strict';
import { aceitarSnapshot } from '../src/sync.js';

test('resposta HTTP atrasada não reverte placar recebido por WebSocket', () => {
  const atual = { partida_id: 'partida', seq: 8 };
  assert.equal(aceitarSnapshot(atual, { partida_id: 'partida', seq: 7 }, 'partida'), false);
  assert.equal(aceitarSnapshot(atual, { partida_id: 'partida', seq: 9 }, 'partida'), true);
});

test('resposta da sala anterior não contamina a sala atual', () => {
  assert.equal(aceitarSnapshot(null, { partida_id: 'antiga', seq: 100 }, 'nova'), false);
  assert.equal(aceitarSnapshot(null, { partida_id: 'nova', seq: 1 }, 'nova'), true);
});

test('aceita transição para nova partida na mesma sala', () => {
  const atual = { quadra: { id: '12345' }, partida_id: 'partida-1', seq: 25 };
  const novaPartida = { quadra: { id: '12345' }, partida_id: 'partida-2', seq: 1 };
  assert.equal(aceitarSnapshot(atual, novaPartida, 'partida-1'), true);
});
