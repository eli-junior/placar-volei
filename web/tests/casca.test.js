import { test } from 'node:test';
import assert from 'node:assert/strict';
import { emCascaEmbarcada, normalizarServidor, lerServidor, salvarServidor } from '../src/lib/casca.js';

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

test('servidor lembrado sobrevive a armazenamento indisponível', () => {
  const mapa = new Map();
  const armazenamento = { getItem: (k) => mapa.get(k) ?? null, setItem: (k, v) => mapa.set(k, v) };
  assert.equal(lerServidor(armazenamento, 'padrao.com'), 'padrao.com');
  salvarServidor('https://a.com', armazenamento);
  assert.equal(lerServidor(armazenamento), 'https://a.com');
  const quebrado = { getItem() { throw new Error(); }, setItem() { throw new Error(); } };
  assert.equal(lerServidor(quebrado, 'x'), 'x');
  assert.doesNotThrow(() => salvarServidor('y', quebrado));
});
