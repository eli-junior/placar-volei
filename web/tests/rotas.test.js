import { test } from 'node:test';
import assert from 'node:assert/strict';
import { resolverRota } from '../src/lib/rotas.js';

test('rotas conhecidas do navegador', () => {
  assert.deepEqual(resolverRota('/'), { tela: 'inicio' });
  assert.deepEqual(resolverRota('/index.html'), { tela: 'inicio' });
  assert.deepEqual(resolverRota('/jogadores'), { tela: 'jogadores' });
  assert.deepEqual(resolverRota('/joguinho'), { tela: 'joguinho' });
  assert.deepEqual(resolverRota('/quadra/12345'), { tela: 'quadra', quadraId: '12345' });
});

test('/sessao é o endereço antigo do Joguinho e aponta o canônico', () => {
  assert.deepEqual(resolverRota('/sessao'), { tela: 'joguinho', canonico: '/joguinho' });
});

test('barra final é ignorada', () => {
  assert.equal(resolverRota('/jogadores/').tela, 'jogadores');
  assert.equal(resolverRota('/joguinho//').tela, 'joguinho');
  assert.deepEqual(resolverRota('/quadra/abc/'), { tela: 'quadra', quadraId: 'abc' });
});

test('o resto não existe', () => {
  for (const caminho of ['/rota-inexistente', '/quadra', '/quadra/', '/quadra/1/2', '/quadra/a b', '/joguinho/x', '/api/sessao', '/Joguinho']) {
    assert.equal(resolverRota(caminho).tela, 'nao_encontrada', caminho);
  }
});

test('no APK só o início e a sala existem', () => {
  assert.equal(resolverRota('/', { apk: true }).tela, 'inicio');
  assert.equal(resolverRota('/quadra/123', { apk: true }).tela, 'quadra');
  for (const caminho of ['/joguinho', '/sessao', '/jogadores', '/qualquer']) {
    assert.equal(resolverRota(caminho, { apk: true }).tela, 'nao_encontrada', caminho);
  }
});
