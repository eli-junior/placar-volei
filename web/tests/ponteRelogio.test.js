// CV7.TS3 — a ponte entre o plugin do Data Layer e a quadra local.
import { test, mock } from 'node:test';
import assert from 'node:assert/strict';
import { QuadraLocal } from '../src/lib/quadraLocal.js';
import { INTERVALO_SINAL_MS, criarPonteRelogio } from '../src/lib/ponteRelogio.js';

function memoria() {
  const mapa = new Map();
  return {
    mapa,
    falharGravacao: false,
    async ler(c) { return mapa.get(c) ?? null; },
    async gravar(c, v) { if (this.falharGravacao) throw new Error('disco'); mapa.set(c, v); },
    async apagar(c) { mapa.delete(c); },
  };
}

/** Plugin de mentira: guarda o que o JS mandou e deixa o teste "receber" lances. */
function pluginFalso() {
  const p = { ouvintes: [], respostas: [], estados: [], iniciou: 0, parou: 0, falharResposta: false };
  p.pings = [];
  p.addListener = async (evento, f) => {
      (evento === 'ping' ? p.pings : p.ouvintes).push(f);
    return { remove: async () => { p.ouvintes = p.ouvintes.filter((x) => x !== f); p.pings = p.pings.filter((x) => x !== f); } };
  };
  p.iniciar = async () => { p.iniciou++; };
  p.parar = async () => { p.parou++; };
  p.responder = async (r) => { if (p.falharResposta) throw new Error('fora de alcance'); p.respostas.push({ no: r.no, ...JSON.parse(r.json) }); };
  p.publicarEstado = async ({ json }) => { p.estados.push(JSON.parse(json)); };
  p.receber = (corpo) => Promise.all(p.ouvintes.map((f) => f({ no: 'no-1', corpo: typeof corpo === 'string' ? corpo : JSON.stringify(corpo) })));
  return p;
}

const uuid = (n) => `00000000-0000-4000-8000-${String(n).padStart(12, '0')}`;
async function montar() {
  const arm = memoria();
  let n = 0;
  const q = await QuadraLocal.criar(arm, { apelido: 'Eli', novoId: () => `id-${++n}` });
  const plugin = pluginFalso();
  const mudancas = [];
  const ponte = criarPonteRelogio({ plugin, quadra: q, aoMudar: (s) => mudancas.push(s) });
  await ponte.iniciar();
  return { arm, q, plugin, ponte, mudancas, partida: q.snapshot().partida_id };
}
const lance = (partida, n, equipe) => ({ id: uuid(n), partida_id: partida, controle_versao: 1, acao: 'ponto', equipe });

test('ao iniciar, liga o plugin e publica o estado atual para o relógio, já com a sala aberta', async () => {
  const { plugin, ponte } = await montar();
  assert.equal(plugin.iniciou, 1);
  assert.equal(plugin.ouvintes.length, 1);
  assert.equal(plugin.estados.length, 1);
  assert.equal(plugin.estados[0].estado_partida.pontos_a, 0);
  assert.equal(plugin.estados[0].sala_aberta, true);
  assert.equal(typeof plugin.estados[0].t, 'number');
  await ponte.parar();
});

test('o relógio que acabou de abrir pergunta (ping) e recebe o estado na hora', async () => {
  const { plugin, ponte } = await montar();
  const antes = plugin.estados.length;
  await Promise.all(plugin.pings.map((f) => f({})));
  await new Promise((r) => setTimeout(r, 5));
  assert.equal(plugin.estados.length, antes + 1);
  await ponte.parar();
});

test('sinal de vida: republica o estado a cada intervalo enquanto a sala está aberta', async () => {
  mock.timers.enable({ apis: ['setInterval'] });
  try {
    const { plugin, ponte } = await montar();
    const antes = plugin.estados.length;
    mock.timers.tick(INTERVALO_SINAL_MS * 3);
    await new Promise((r) => setImmediate(r));
    assert.equal(plugin.estados.length, antes + 3);
    await ponte.parar();
    const depois = plugin.estados.length;
    mock.timers.tick(INTERVALO_SINAL_MS * 3);
    await new Promise((r) => setImmediate(r));
    assert.equal(plugin.estados.length, depois);
  } finally {
    mock.timers.reset();
  }
});

test('lance do relógio: responde ao nó que enviou, publica o estado novo e avisa a tela', async () => {
  const { plugin, partida, mudancas, q } = await montar();
  await plugin.receber(lance(partida, 1, 'A'));
  assert.equal(plugin.respostas.length, 1);
  const r = plugin.respostas[0];
  assert.deepEqual([r.no, r.id, r.status, r.recibo.status, r.estado.comando_id], ['no-1', uuid(1), 201, 'APLICADO', uuid(1)]);
  assert.equal(q.snapshot().estado_partida.pontos_a, 1);
  assert.equal(mudancas.at(-1).estado_partida.pontos_a, 1);
  assert.equal(plugin.estados.at(-1).estado_partida.pontos_a, 1);
  assert.equal(plugin.estados.at(-1).comando_id, undefined);
});

test('reenvio pelo mesmo id devolve o mesmo recibo sem contar de novo', async () => {
  const { plugin, partida, q } = await montar();
  await plugin.receber(lance(partida, 1, 'B'));
  await plugin.receber(lance(partida, 1, 'B'));
  assert.deepEqual(plugin.respostas.map((r) => r.status), [201, 200]);
  assert.deepEqual(plugin.respostas[0].recibo, plugin.respostas[1].recibo);
  assert.equal(q.snapshot().estado_partida.pontos_b, 1);
});

test('corpo ilegível: 400, sem efeito; a ponte segue de pé', async () => {
  const { plugin, partida, q } = await montar();
  await plugin.receber('{ não é json');
  assert.deepEqual([plugin.respostas[0].status, plugin.respostas[0].id], [400, null]);
  await plugin.receber(lance(partida, 2, 'A'));
  assert.equal(plugin.respostas[1].status, 201);
  assert.equal(q.snapshot().estado_partida.pontos_a, 1);
});

test('falha ao gravar no aparelho: 503 para o relógio guardar na fila, e o placar não muda', async () => {
  const { arm, plugin, partida, q } = await montar();
  arm.falharGravacao = true;
  await plugin.receber(lance(partida, 3, 'A'));
  assert.deepEqual([plugin.respostas[0].status, plugin.respostas[0].id], [503, uuid(3)]);
  assert.equal(q.snapshot().estado_partida.pontos_a, 0);
  // Com o disco de volta, o reenvio do mesmo lance entra.
  arm.falharGravacao = false;
  await plugin.receber(lance(partida, 3, 'A'));
  assert.deepEqual([plugin.respostas[1].status, q.snapshot().estado_partida.pontos_a], [201, 1]);
});

test('relógio fora de alcance na resposta: o lance já valeu e o reenvio acha o recibo', async () => {
  const { plugin, partida, q } = await montar();
  plugin.falharResposta = true;
  await plugin.receber(lance(partida, 4, 'A'));
  assert.equal(plugin.respostas.length, 0);
  assert.equal(q.snapshot().estado_partida.pontos_a, 1);
  plugin.falharResposta = false;
  await plugin.receber(lance(partida, 4, 'A'));
  assert.deepEqual([plugin.respostas[0].status, q.snapshot().estado_partida.pontos_a], [200, 1]);
});

test('publicar sem relógio ao alcance não derruba nada', async () => {
  const { plugin, ponte } = await montar();
  plugin.publicarEstado = async () => { throw new Error('sem nós'); };
  await assert.doesNotReject(ponte.publicar());
});

test('parar avisa que a sala fechou e desliga os ouvintes e o plugin', async () => {
  const { plugin, ponte } = await montar();
  await ponte.parar();
  assert.equal(plugin.estados.at(-1).sala_aberta, false);
  assert.deepEqual([plugin.ouvintes.length, plugin.pings.length, plugin.parou], [0, 0, 1]);
});
