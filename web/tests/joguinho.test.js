import { test } from 'node:test';
import assert from 'node:assert/strict';
import { joguinhoVelho, oQueSePerde } from '../src/lib/joguinho.js';

const local = (a, m, d, h = 12) => new Date(a, m - 1, d, h, 0, 0);

test('joguinho de hoje não é velho, mesmo aberto de manhã e visto à noite', () => {
  assert.equal(joguinhoVelho(local(2026, 10, 8, 7).toISOString(), local(2026, 10, 8, 23)), null);
});

test('ontem e há N dias, pelo calendário do aparelho', () => {
  const ontem = joguinhoVelho(local(2026, 10, 7, 21).toISOString(), local(2026, 10, 8, 8));
  assert.deepEqual(ontem, { dias: 1, data: '07/10', quando: 'ontem' });
  const antigo = joguinhoVelho(local(2026, 10, 3, 9).toISOString(), local(2026, 10, 8, 8));
  assert.deepEqual(antigo, { dias: 5, data: '03/10', quando: 'há 5 dias' });
});

test('virada de mês e de ano', () => {
  assert.equal(joguinhoVelho(local(2026, 9, 30, 22).toISOString(), local(2026, 10, 1, 1))?.data, '30/09');
  assert.equal(joguinhoVelho(local(2025, 12, 31, 23).toISOString(), local(2026, 1, 1, 0))?.quando, 'ontem');
});

test('data ausente ou inválida não gera aviso', () => {
  assert.equal(joguinhoVelho(null), null);
  assert.equal(joguinhoVelho('lixo'), null);
});

test('o que se perde: proposta, rodada vazia e rodada com tudo', () => {
  assert.deepEqual(oQueSePerde({ estado: 'proposta', numero: 2 }, null), ['a proposta 2 (os times sorteados)']);
  assert.deepEqual(oQueSePerde({ estado: 'em_andamento', numero: 1 }, { partidas_encerradas: 0, fila: [], reis: [] }), ['a rodada 1']);
  const cheia = oQueSePerde(
    { estado: 'em_andamento', numero: 3 },
    { partidas_encerradas: 1, partida: { time_a: 2, time_b: 3 }, fila: [{}, {}], reis: [{}] },
  );
  assert.deepEqual(cheia, [
    '1 partida registrada (deixam de contar)',
    'a partida chamada, Time 2 × Time 3 (é anulada)',
    'a fila (2 times)',
    '1 rei da quadra',
  ]);
});
