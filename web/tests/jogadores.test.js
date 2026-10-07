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
