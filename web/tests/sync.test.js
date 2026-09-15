import { test } from 'node:test';
import assert from 'node:assert/strict';
import { aceitarSnapshot, mensagemDeErro } from '../src/sync.js';

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

test('erro normalizado do backend chega como frase legível', () => {
  const corpo = {
    detail: 'Apelido deve ter no máximo 30 caractere(s).',
    erros: [{ campo: 'apelido', rotulo: 'Apelido', mensagem: 'deve ter no máximo 30 caractere(s)' }],
  };
  assert.equal(mensagemDeErro(corpo), 'Apelido deve ter no máximo 30 caractere(s).');
});

test('422 cru do FastAPI nunca vira "[object Object]"', () => {
  const cru = {
    detail: [
      { type: 'missing', loc: ['body', 'apelido'], msg: 'Field required' },
      { type: 'string_too_long', loc: ['body', 'nome'], msg: 'String should have at most 50 characters' },
    ],
  };
  const texto = mensagemDeErro(cru);
  assert.ok(!texto.includes('[object Object]'));
  assert.ok(texto.includes('apelido Field required'));
  assert.ok(texto.includes('nome String should have at most 50 characters'));
});

test('corpo sem descrição cai na mensagem alternativa', () => {
  assert.equal(mensagemDeErro({}, 'Falhou.'), 'Falhou.');
  assert.equal(mensagemDeErro(null, 'Falhou.'), 'Falhou.');
  assert.equal(mensagemDeErro({ detail: {} }, 'Falhou.'), 'Falhou.');
});
