import { test } from 'node:test';
import assert from 'node:assert/strict';
import { ordenarJogadores, chamarJogadores, ErroJogadores } from '../src/lib/jogadores.js';
import { noAplicativoAndroid, emCascaEmbarcada } from '../src/lib/casca.js';
import { guardarSegredoDono, lerSegredoDono } from '../src/lib/preferencias.js';

test('ordena ativos antes de inativos e sem considerar acento', () => {
  const lista = [
    { nome: 'Zeca', ativo: true }, { nome: 'Ana', ativo: false },
    { nome: 'Álvaro', ativo: true }, { nome: 'Bia', ativo: true },
  ];
  assert.deepEqual(ordenarJogadores(lista).map(j => j.nome), ['Álvaro', 'Bia', 'Zeca', 'Ana']);
});

test('404 vira segredo recusado e 409 traz o campo', async () => {
  const resp = (status, corpo) => async () => ({ ok: status < 400, status, json: async () => corpo });
  await assert.rejects(chamarJogadores('x', '', {}, resp(404, null)), e => e instanceof ErroJogadores && /Segredo recusado/.test(e.message));
  await assert.rejects(
    chamarJogadores('x', '', { metodo: 'POST', corpo: {} }, resp(409, { detail: 'Nome em uso.', erros: [{ campo: 'nome' }] })),
    e => e.status === 409 && e.campo === 'nome' && e.message === 'Nome em uso.',
  );
});

test('envia o segredo no cabeçalho', async () => {
  let visto;
  await chamarJogadores('abc', '', {}, async (_url, init) => { visto = init.headers; return { ok: true, json: async () => ({}) }; });
  assert.equal(visto['x-owner-secret'], 'abc');
});

test('APK: qualquer página nativa oculta jogadores; só localhost é a casca', () => {
  const nativo = (hostname) => ({ Capacitor: { isNativePlatform: () => true }, location: { hostname } });
  assert.equal(noAplicativoAndroid(nativo('placar.exemplo.com')), true);
  assert.equal(emCascaEmbarcada(nativo('placar.exemplo.com')), false);
  assert.equal(noAplicativoAndroid({ location: { hostname: 'x' } }), false);
});

test('segredo do dono é guardado e esquecido', () => {
  const mem = new Map();
  const arm = { getItem: k => mem.get(k) ?? null, setItem: (k, v) => mem.set(k, v), removeItem: k => mem.delete(k) };
  guardarSegredoDono('s3', arm);
  assert.equal(lerSegredoDono(arm), 's3');
  guardarSegredoDono('', arm);
  assert.equal(lerSegredoDono(arm), '');
});

import { dimensoesReduzidas, iniciais, enviarFoto } from '../src/lib/jogadores.js';

test('reduz pelo lado maior sem ampliar', () => {
  assert.deepEqual(dimensoesReduzidas(4000, 3000), { largura: 480, altura: 360 });
  assert.deepEqual(dimensoesReduzidas(3000, 4000), { largura: 360, altura: 480 });
  assert.deepEqual(dimensoesReduzidas(200, 100), { largura: 200, altura: 100 });
  assert.deepEqual(dimensoesReduzidas(10000, 1), { largura: 480, altura: 1 });
  assert.deepEqual(dimensoesReduzidas(0, 0), { largura: 1, altura: 1 });
});

test('iniciais do avatar', () => {
  assert.equal(iniciais('Ana Maria Souza'), 'AS');
  assert.equal(iniciais('ana'), 'A');
  assert.equal(iniciais('  '), '?');
  assert.equal(iniciais(undefined), '?');
});

test('envia a foto como JPEG cru com o segredo', async () => {
  let visto;
  const r = await enviarFoto('seg', 'j1', new Blob(['x']), async (url, init) => {
    visto = { url, init };
    return { ok: true, json: async () => ({ id: 'j1' }) };
  });
  assert.equal(r.id, 'j1');
  assert.equal(visto.url, '/api/jogadores/j1/foto');
  assert.equal(visto.init.method, 'PUT');
  assert.equal(visto.init.headers['content-type'], 'image/jpeg');
  assert.equal(visto.init.headers['x-owner-secret'], 'seg');
  await assert.rejects(enviarFoto('s', 'j', new Blob(['x']), async () => ({ ok: false, status: 413, json: async () => ({ detail: 'Foto grande.' }) })), e => e.status === 413 && e.message === 'Foto grande.');
});

import { moverPosicao, faltamParaSortear, chamarSessao } from '../src/lib/jogadores.js';

test('mover posição sobe, desce e respeita os limites', () => {
  assert.deepEqual(moverPosicao(['a', 'b', 'c'], 'b', -1), ['b', 'a', 'c']);
  assert.deepEqual(moverPosicao(['a', 'b', 'c'], 'b', 1), ['a', 'c', 'b']);
  assert.deepEqual(moverPosicao(['a', 'b', 'c'], 'a', -1), ['a', 'b', 'c']);
  assert.deepEqual(moverPosicao(['a', 'b', 'c'], 'c', 1), ['a', 'b', 'c']);
  assert.deepEqual(moverPosicao(['a', 'b'], 'x', 1), ['a', 'b']);
  const original = ['a', 'b'];
  moverPosicao(original, 'a', 1);
  assert.deepEqual(original, ['a', 'b']);
});

test('quantos faltam para sortear', () => {
  assert.equal(faltamParaSortear(0), 4);
  assert.equal(faltamParaSortear(3), 1);
  assert.equal(faltamParaSortear(4), 0);
  assert.equal(faltamParaSortear(9), 0);
});

test('chamarSessao usa /api/sessao com o segredo', async () => {
  let visto;
  await chamarSessao('seg', '/presencas/j1', { metodo: 'PUT' }, async (url, init) => { visto = { url, init }; return { ok: true, json: async () => ({}) }; });
  assert.equal(visto.url, '/api/sessao/presencas/j1');
  assert.equal(visto.init.method, 'PUT');
  assert.equal(visto.init.headers['x-owner-secret'], 'seg');
  await assert.rejects(chamarSessao('s', '', {}, async () => ({ ok: false, status: 409, json: async () => ({ detail: 'Sessão já existe uma sessão aberta.', erros: [{ campo: 'sessao' }] }) })), e => e.status === 409 && e.campo === 'sessao');
});

import { chamarRodada, descreverTime, posicaoDaCombinacao, primeiraPartida } from '../src/lib/jogadores.js';

test('primeira partida são os dois primeiros da fila', () => {
  const times = [{ fila: 3 }, { fila: 1 }, { fila: 2 }];
  assert.deepEqual(primeiraPartida(times).map((t) => t.fila), [1, 2]);
  assert.equal(primeiraPartida([{ fila: 1 }]), null);
  assert.equal(primeiraPartida(undefined), null);
});

test('descreve um time com as notas do sorteio', () => {
  const time = { jogadores: [{ nome: 'Ana Souza', nota: 90 }, { nome: 'Bia Lima', nota: 85 }] };
  assert.equal(descreverTime(time), 'Ana Souza (90) + Bia Lima (85)');
});

test('posição da combinação volta ao início ao esgotar', () => {
  assert.deepEqual(posicaoDaCombinacao({ tentativa: 0, distintas: 5 }), { atual: 1, total: 5 });
  assert.deepEqual(posicaoDaCombinacao({ tentativa: 4, distintas: 5 }), { atual: 5, total: 5 });
  assert.deepEqual(posicaoDaCombinacao({ tentativa: 5, distintas: 5 }), { atual: 1, total: 5 });
  assert.deepEqual(posicaoDaCombinacao({ tentativa: 3, distintas: 1 }), { atual: 1, total: 1 });
  assert.deepEqual(posicaoDaCombinacao({ tentativa: 2 }), { atual: 1, total: 1 });
});

test('chamarRodada usa /api/rodada com o segredo e o corpo', async () => {
  let visto;
  await chamarRodada('seg', '/sorteio', { metodo: 'POST', corpo: { alvo: 12 } }, async (url, init) => { visto = { url, init }; return { ok: true, json: async () => ({}) }; });
  assert.equal(visto.url, '/api/rodada/sorteio');
  assert.equal(visto.init.body, JSON.stringify({ alvo: 12 }));
  assert.equal(visto.init.headers['x-owner-secret'], 'seg');
});
