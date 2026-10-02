import { test } from 'node:test';
import assert from 'node:assert/strict';
import { emCascaEmbarcada, normalizarServidor, servidorDisponivel } from '../src/lib/casca.js';

const nativo = (hostname) => ({ Capacitor: { isNativePlatform: () => true }, location: { hostname } });

test('casca embarcada só no APK e só na interface local', () => {
  assert.equal(emCascaEmbarcada(nativo('localhost')), true);
  // Páginas do servidor abertas pelo WebView seguem o app de sempre.
  assert.equal(emCascaEmbarcada(nativo('placar.exemplo.com')), false);
  assert.equal(emCascaEmbarcada({ location: { hostname: 'localhost' } }), false);
  assert.equal(emCascaEmbarcada(undefined), false);
});

test('servidor aceita domínio puro ou URL e devolve a origem https', () => {
  assert.equal(normalizarServidor('placar.exemplo.com'), 'https://placar.exemplo.com');
  assert.equal(normalizarServidor(' https://placar.exemplo.com/quadra/123 '), 'https://placar.exemplo.com');
  assert.equal(normalizarServidor('http://192.168.0.10:8000'), 'http://192.168.0.10:8000');
  assert.equal(normalizarServidor('http://placar.exemplo.com'), null);
  assert.equal(normalizarServidor(''), null);
  assert.equal(normalizarServidor('não é url'), null);
});

test('servidor disponível quando a rede chega, indisponível se falha ou demora', async () => {
  const chamadas = [];
  const ok = async (url, opcoes) => { chamadas.push([url, opcoes.mode]); return {}; };
  assert.equal(await servidorDisponivel('https://a.com', { fetchFn: ok }), true);
  assert.deepEqual(chamadas, [['https://a.com/health', 'no-cors']]);

  const falha = async () => { throw new TypeError('Failed to fetch'); };
  assert.equal(await servidorDisponivel('https://a.com', { fetchFn: falha }), false);

  const demora = (_url, { signal }) => new Promise((_, rejeitar) => signal.addEventListener('abort', () => rejeitar(new Error('abortado'))));
  assert.equal(await servidorDisponivel('https://a.com', { fetchFn: demora, tempoMs: 20 }), false);
});
