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
