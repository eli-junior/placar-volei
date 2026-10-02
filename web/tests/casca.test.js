import { test } from 'node:test';
import assert from 'node:assert/strict';
import { emCascaEmbarcada, modosDisponiveis, normalizarServidor, servidorDisponivel } from '../src/lib/casca.js';

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

test('servidor só está disponível com 200 e status ok no /health', async () => {
  const urls = [];
  const resposta = (status, corpo) => async (url) => { urls.push(url); return { status, corpo }; };
  assert.equal(await servidorDisponivel('https://a.com', { requisitar: resposta(200, { status: 'ok', version: '1' }) }), true);
  assert.deepEqual(urls, ['https://a.com/health']);

  // Túnel no ar com o backend fora (502) e respostas sem o corpo esperado não valem.
  assert.equal(await servidorDisponivel('https://a.com', { requisitar: resposta(502, null) }), false);
  assert.equal(await servidorDisponivel('https://a.com', { requisitar: resposta(200, '<html>') }), false);
  assert.equal(await servidorDisponivel('https://a.com', { requisitar: resposta(200, { status: 'erro' }) }), false);

  const falha = async () => { throw new TypeError('Failed to fetch'); };
  assert.equal(await servidorDisponivel('https://a.com', { requisitar: falha }), false);

  const nuncaResponde = () => new Promise(() => {});
  assert.equal(await servidorDisponivel('https://a.com', { requisitar: nuncaResponde, tempoMs: 20 }), false);
});

const semLocal = { existe: false, emAndamento: false };
const emAndamento = { existe: true, emAndamento: true };
const encerrada = { existe: true, emAndamento: false };

test('modos: servidor no ar libera só a online e diz por que a local não', () => {
  const m = modosDisponiveis({ servidor: 'disponivel', configurado: true, local: semLocal });
  assert.deepEqual([m.online, m.local, m.acaoLocal], [true, false, 'criar']);
  assert.match(m.aviso, /só é usada quando não há conexão/);
  assert.equal(modosDisponiveis({ servidor: 'disponivel', configurado: true, local: encerrada }).local, false);
});

test('modos: sem servidor libera só a local (criar ou continuar)', () => {
  assert.deepEqual(modosDisponiveis({ servidor: 'indisponivel', configurado: true, local: semLocal }), { online: false, local: true, acaoLocal: 'criar', aviso: null });
  assert.equal(modosDisponiveis({ servidor: 'indisponivel', configurado: true, local: encerrada }).acaoLocal, 'continuar');
  // APK sem servidor configurado: a local é o único modo.
  assert.deepEqual(modosDisponiveis({ servidor: 'indisponivel', configurado: false, local: semLocal }).local, true);
});

test('modos: partida local em andamento nunca fica presa, nem testando nem com o servidor no ar', () => {
  assert.equal(modosDisponiveis({ servidor: 'disponivel', configurado: true, local: emAndamento }).local, true);
  const testando = modosDisponiveis({ servidor: 'testando', configurado: true, local: emAndamento });
  assert.deepEqual([testando.online, testando.local, testando.acaoLocal], [false, true, 'continuar']);
});

test('modos: testando a conexão não libera nada novo', () => {
  const m = modosDisponiveis({ servidor: 'testando', configurado: true, local: semLocal });
  assert.deepEqual([m.online, m.local], [false, false]);
  assert.equal(modosDisponiveis({ servidor: 'testando', configurado: true, local: encerrada }).local, false);
});
