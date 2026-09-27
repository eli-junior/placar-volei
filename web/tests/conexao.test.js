import { test } from 'node:test';
import assert from 'node:assert/strict';
import { criarConexao } from '../src/lib/conexao.js';

class SocketFalso {
  constructor(alvo) { this.alvo = alvo; this.readyState = 1; this.fechado = false; }
  close() { this.fechado = true; this.readyState = 3; }
  receber(obj) { this.onmessage?.({ data: JSON.stringify(obj) }); }
  cair(code = 1006) { this.readyState = 3; this.onclose?.({ code }); }
}

function montar(extra = {}) {
  const sockets = [];
  const mensagens = [];
  const timers = [];
  let agora = 0;
  let quedas = 0;
  const conexao = criarConexao({
    criarSocket: alvo => { const s = new SocketFalso(alvo); sockets.push(s); return s; },
    aoMensagem: m => mensagens.push(m),
    aoCair: () => { quedas += 1; },
    aoFechar: () => true,
    agendar: (fn, ms) => { const t = { fn, em: agora + ms, ativo: true }; timers.push(t); return t; },
    cancelar: t => { if (t) t.ativo = false; },
    agora: () => agora,
    aleatorio: () => 0,
    ...extra,
  });
  const avancar = ms => {
    agora += ms;
    for (const t of [...timers]) if (t.ativo && t.em <= agora) { t.ativo = false; t.fn(); }
  };
  return { conexao, sockets, mensagens, avancar, quedas: () => quedas };
}

test('PING não chega ao app e mantém a conexão viva', () => {
  const { conexao, sockets, mensagens, avancar } = montar();
  conexao.conectar('12345');
  for (let i = 0; i < 5; i++) { avancar(20000); sockets[0].receber({ tipo: 'PING' }); }
  assert.equal(mensagens.length, 0);
  assert.equal(sockets.length, 1);
  assert.equal(sockets[0].fechado, false);
});

test('45 s de silêncio derrubam o socket e reconectam', () => {
  const { conexao, sockets, avancar, quedas } = montar();
  conexao.conectar('12345');
  avancar(45001);
  assert.equal(sockets[0].fechado, true);
  assert.equal(quedas(), 1);
  avancar(1000);
  assert.equal(sockets.length, 2);
});

test('backoff cresce a cada queda e volta ao início com a confirmação', () => {
  const { conexao, sockets, avancar } = montar();
  conexao.conectar('12345');
  sockets[0].cair();
  assert.equal(conexao.tentativas, 1);
  avancar(1000);
  sockets[1].cair();
  assert.equal(conexao.tentativas, 2);
  avancar(1500);
  assert.equal(sockets.length, 3);
  conexao.confirmar();
  assert.equal(conexao.tentativas, 0);
});

test('mensagem de socket antigo é ignorada', () => {
  const { conexao, sockets, mensagens } = montar();
  conexao.conectar('12345');
  conexao.conectar('12345');
  sockets[0].receber({ tipo: 'PLACAR_ATUALIZADO' });
  sockets[0].cair();
  assert.equal(mensagens.length, 0);
  sockets[1].receber({ tipo: 'PLACAR_ATUALIZADO' });
  assert.equal(mensagens.length, 1);
});

test('fechamento definitivo (4401/4404) não reconecta', () => {
  const { conexao, sockets, avancar } = montar({ aoFechar: code => code !== 4404 });
  conexao.conectar('12345');
  sockets[0].cair(4404);
  avancar(60000);
  assert.equal(sockets.length, 1);
});

test('retomar reabre na hora um socket morto e ignora um vivo', () => {
  const { conexao, sockets, avancar } = montar();
  conexao.conectar('12345');
  conexao.retomar();
  assert.equal(sockets.length, 1);
  sockets[0].readyState = 3;
  conexao.retomar();
  assert.equal(sockets.length, 2);
  assert.equal(conexao.tentativas, 0);
  avancar(10);
});

test('desconectar para tudo, inclusive a reconexão agendada', () => {
  const { conexao, sockets, avancar } = montar();
  conexao.conectar('12345');
  sockets[0].cair();
  conexao.desconectar();
  avancar(60000);
  assert.equal(sockets.length, 1);
});
