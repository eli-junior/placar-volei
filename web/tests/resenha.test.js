import { test } from 'node:test';
import assert from 'node:assert/strict';
import { comSinal, contarPartida, dataDaResenha, emPedacos, montarCartoes, nomeDoArquivo, nomesDe, recorde } from '../src/lib/resenha.js';

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

test('cartões: capa, prêmios sem o rei, galeria e tabela, numerados', () => {
  const premios = [{ id: 'rei' }, ...Array.from({ length: 7 }, (_, i) => ({ id: `p${i}` }))];
  const galeria = Array.from({ length: 10 }, (_, i) => ({ jogador: `j${i}` }));
  const tabela = Array.from({ length: 10 }, (_, i) => ({ jogador: `j${i}` }));
  const cartoes = montarCartoes({ premios, galeria, tabela });
  assert.deepEqual(cartoes.map((c) => `${c.tipo}${c.parte}/${c.partes}`), ['capa1/1', 'premios1/2', 'premios2/2', 'galeria1/2', 'galeria2/2', 'tabela1/1']);
  assert.equal(cartoes[1].itens.length, 5);
  assert.ok(cartoes.flatMap((c) => c.itens).every((p) => p.id !== 'rei'));
  assert.deepEqual(cartoes.map((c) => c.numero), [1, 2, 3, 4, 5, 6]);
  assert.ok(cartoes.every((c) => c.total === 6));
});

test('sem partidas, só a capa', () => {
  assert.deepEqual(montarCartoes({ premios: [], galeria: [], tabela: [] }).map((c) => c.tipo), ['capa']);
});

test('pedaços e nome do arquivo no fuso da quadra', () => {
  assert.deepEqual(emPedacos([1, 2, 3, 4, 5], 2), [[1, 2], [3, 4], [5]]);
  assert.deepEqual(emPedacos([], 2), []);
  assert.equal(nomeDoArquivo('2026-10-15T01:30:00+00:00', 3), 'resenha-2026-10-14-3.png');
  assert.equal(nomeDoArquivo(null, 1), 'resenha-joguinho-1.png');
});
