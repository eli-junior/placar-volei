import { test } from 'node:test';
import assert from 'node:assert/strict';
import { comSinal, contarPartida, dataDaResenha, nomesDe, recorde } from '../src/lib/resenha.js';

const jogadores = {
  a: { id: 'a', nome: 'Ana' },
  b: { id: 'b', nome: 'Beto' },
  c: { id: 'c', nome: 'Caio' },
  d: { id: 'd', nome: 'Duda' },
};

test('nomes de um, dois e três jogadores', () => {
  assert.equal(nomesDe(['a'], jogadores), 'Ana');
  assert.equal(nomesDe(['a', 'b'], jogadores), 'Ana & Beto');
  assert.equal(nomesDe(['a', 'b', 'c'], jogadores), 'Ana, Beto e Caio');
  assert.equal(nomesDe([], jogadores), '');
  assert.equal(nomesDe(['x'], jogadores), '?');
});

test('data no fuso de São Paulo, sem o "-feira"', () => {
  // 01:30 UTC de quinta ainda é quarta à noite em São Paulo
  assert.equal(dataDaResenha('2026-10-15T01:30:00+00:00'), 'quarta, 14/10');
  assert.equal(dataDaResenha('2026-10-18T12:00:00+00:00'), 'domingo, 18/10');
  assert.equal(dataDaResenha(null), '');
  assert.equal(dataDaResenha('lixo'), '');
});

test('a partida é contada pelo lado de quem venceu', () => {
  const partida = { placar_a: 2, placar_b: 10, lado_a: ['a', 'b'], lado_b: ['c', 'd'] };
  assert.deepEqual(contarPartida(partida, jogadores), {
    vencedores: 'Caio & Duda',
    perdedores: 'Ana & Beto',
    placar: '10 x 2',
  });
});

test('recorde e saldo com sinal', () => {
  assert.equal(comSinal(12), '+12');
  assert.equal(comSinal(-3), '-3');
  assert.equal(comSinal(0), '0');
  assert.equal(recorde({ vitorias: 4, derrotas: 2, saldo: 12 }), '4V · 2D · +12');
  assert.equal(recorde({ vitorias: 0, derrotas: 0, saldo: 0 }), 'não entrou em quadra');
});
