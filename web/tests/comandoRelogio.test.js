// CV7.TS3 — lances do relógio na quadra local: mesmo contrato do servidor
// (`POST /api/watch/comandos`), aplicados uma vez só e com recibo.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { CHAVE_QUADRA_LOCAL, ID_RELOGIO_LOCAL, QuadraLocal } from '../src/lib/quadraLocal.js';
import { MSG_ALVO_MUDOU } from '../src/lib/partida.js';

function memoria() {
  const mapa = new Map();
  return {
    mapa,
    async ler(c) { return mapa.get(c) ?? null; },
    async gravar(c, v) { mapa.set(c, v); },
    async apagar(c) { mapa.delete(c); },
  };
}

let seqId = 0;
const uuid = () => `00000000-0000-4000-8000-${String(++seqId).padStart(12, '0')}`;
const opcoes = () => { let n = 0; return { apelido: 'Eli', agora: () => '2026-10-02T12:00:00+00:00', novoId: () => `id-${++n}` }; };

async function quadra(campos = {}) {
  const arm = memoria();
  const q = await QuadraLocal.criar(arm, opcoes(), campos);
  return { arm, q, partida: q.snapshot().partida_id };
}

const ponto = (partida, equipe, extra = {}) => ({ id: uuid(), partida_id: partida, controle_versao: 1, acao: 'ponto', equipe, ...extra });
const desfazer = (partida, alvo) => ({ id: uuid(), partida_id: partida, controle_versao: 1, acao: 'desfazer', ...alvo });

test('ponto do relógio: aplica, responde 201 com recibo e o estado já confirmando o lance', async () => {
  const { q, partida } = await quadra();
  const cmd = ponto(partida, 'A');
  const r = await q.aplicarComandoRelogio(cmd);
  assert.equal(r.status, 201);
  assert.deepEqual(r.recibo, { id: cmd.id, status: 'APLICADO', detalhe: null, evento_seq: 2 });
  assert.equal(r.estado.comando_id, cmd.id);
  assert.equal(r.estado.estado_partida.pontos_a, 1);
  assert.equal(r.estado.seq, 2);
  // O relógio tem sempre o controle, e o estado não leva a linha do tempo.
  assert.equal(r.estado.quadra.controle_id, ID_RELOGIO_LOCAL);
  assert.equal('linha_do_tempo' in r.estado, false);
  // O celular vê o lance, atribuído ao relógio.
  const item = q.snapshot().linha_do_tempo.at(-1);
  assert.deepEqual([item.descricao, item.autor_apelido], ['Ponto para Equipe A', 'Relógio']);
});

test('reenvio do mesmo lance não conta duas vezes; outro conteúdo com o mesmo id é recusado', async () => {
  const { q, partida } = await quadra();
  const cmd = ponto(partida, 'A');
  const primeiro = await q.aplicarComandoRelogio(cmd);
  const reenvio = await q.aplicarComandoRelogio({ ...cmd });
  assert.equal(reenvio.status, 200);
  assert.deepEqual(reenvio.recibo, primeiro.recibo);
  assert.equal(reenvio.estado.comando_id, undefined);
  assert.equal(q.snapshot().estado_partida.pontos_a, 1);

  const outro = await q.aplicarComandoRelogio({ ...cmd, equipe: 'B' });
  assert.deepEqual([outro.status, outro.detail], [409, 'Este lance já foi usado com outro conteúdo.']);
  assert.equal(q.snapshot().estado_partida.pontos_b, 0);
});

test('o recibo sobrevive a fechar e reabrir o app: o reenvio continua não contando', async () => {
  const { arm, q, partida } = await quadra();
  const cmd = ponto(partida, 'B');
  await q.aplicarComandoRelogio(cmd);
  const { quadra: reaberta } = await QuadraLocal.abrir(arm, opcoes());
  const reenvio = await reaberta.aplicarComandoRelogio({ ...cmd });
  assert.equal(reenvio.status, 200);
  assert.equal(reaberta.snapshot().estado_partida.pontos_b, 1);
});

test('lance de partida antiga é recusado, guardado e não reaplicado', async () => {
  const { q, partida } = await quadra({ alvo: 1, vantagem: false });
  await q.aplicarComandoRelogio(ponto(partida, 'A'));
  await q.reiniciar({});
  const velho = ponto(partida, 'B');
  const r = await q.aplicarComandoRelogio(velho);
  assert.equal(r.status, 200);
  assert.deepEqual([r.recibo.status, r.recibo.detalhe], ['RECUSADO', 'Uma nova partida começou. Este lance não vale para ela.']);
  assert.equal(q.snapshot().estado_partida.pontos_b, 0);
  assert.deepEqual((await q.aplicarComandoRelogio({ ...velho })).recibo, r.recibo);
});

test('desfazer: pelo seq do ponto visto no topo, ou pelo id de um lance anterior da fila', async () => {
  const { q, partida } = await quadra();
  const a = ponto(partida, 'A');
  const b = ponto(partida, 'B');
  await q.aplicarComandoRelogio(a);
  await q.aplicarComandoRelogio(b);

  // O topo agora é o ponto de B (seq 3): quem viu o de A no topo não desfaz nada.
  const velho = await q.aplicarComandoRelogio(desfazer(partida, { alvo_seq: 2 }));
  assert.deepEqual([velho.recibo.status, velho.recibo.detalhe], ['RECUSADO', MSG_ALVO_MUDOU]);
  assert.equal(q.snapshot().estado_partida.pontos_b, 1);

  // Pelo id do lance que ainda estava na fila do relógio.
  const ok = await q.aplicarComandoRelogio(desfazer(partida, { alvo_comando: b.id }));
  assert.equal(ok.status, 201);
  assert.equal(ok.estado.estado_partida.pontos_b, 0);
  assert.equal(ok.estado.estado_partida.pontos_a, 1);

  // Id desconhecido, ou de um lance recusado, não tem ponto para desfazer.
  const orfao = await q.aplicarComandoRelogio(desfazer(partida, { alvo_comando: uuid() }));
  assert.equal(orfao.recibo.status, 'RECUSADO');
});

test('partida encerrada: ponto recusado; nova partida só depois do fim', async () => {
  const { q, partida } = await quadra({ alvo: 2, vantagem: false });
  const cedo = await q.aplicarComandoRelogio({ id: uuid(), partida_id: partida, controle_versao: 1, acao: 'nova_partida' });
  assert.deepEqual([cedo.recibo.status, cedo.recibo.detalhe], ['RECUSADO', 'A partida atual ainda não foi encerrada.']);

  await q.aplicarComandoRelogio(ponto(partida, 'A'));
  const fim = await q.aplicarComandoRelogio(ponto(partida, 'A'));
  assert.equal(fim.estado.estado_partida.encerrada, true);
  const depois = await q.aplicarComandoRelogio(ponto(partida, 'B'));
  assert.deepEqual([depois.recibo.status, depois.recibo.detalhe], ['RECUSADO', 'A partida já está encerrada.']);

  const nova = await q.aplicarComandoRelogio({ id: uuid(), partida_id: partida, controle_versao: 1, acao: 'nova_partida' });
  assert.equal(nova.status, 201);
  assert.notEqual(nova.estado.partida_id, partida);
  assert.deepEqual([nova.estado.estado_partida.pontos_a, nova.estado.seq], [0, 1]);
});

test('corpo que não é um lance válido: 422, sem recibo e sem efeito', async () => {
  const { q, partida } = await quadra();
  const antes = q.snapshot().seq;
  const ruins = [
    null,
    { ...ponto(partida, 'A'), id: 'x' },
    { ...ponto(partida, 'A'), equipe: 'C' },
    { ...ponto(partida, 'A'), equipe: null },
    { ...ponto(partida, 'A'), alvo_seq: 2 },
    desfazer(partida, {}),
    { ...desfazer(partida, { alvo_seq: 2 }), equipe: 'A' },
    { ...ponto(partida, 'A'), acao: 'voar' },
    { ...ponto(partida, 'A'), partida_id: '' },
    { ...ponto(partida, 'A'), controle_versao: -1 },
  ];
  for (const c of ruins) assert.equal((await q.aplicarComandoRelogio(c)).status, 422, JSON.stringify(c));
  assert.equal(q.snapshot().seq, antes);
  assert.equal((q.registro.recibos ?? []).length, 0);
});

test('celular e relógio marcando juntos entram na ordem e nenhum se perde', async () => {
  const { q, partida } = await quadra({ alvo: 50 });
  const lances = [];
  for (let i = 0; i < 6; i++) {
    lances.push(q.marcarPonto('A'));
    lances.push(q.aplicarComandoRelogio(ponto(partida, 'B')));
  }
  await Promise.all(lances);
  const e = q.snapshot().estado_partida;
  assert.deepEqual([e.pontos_a, e.pontos_b], [6, 6]);
  assert.deepEqual(e.equipes_ativas, ['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B']);
});

test('o estado do relógio continua pequeno em partida longa (limite de ~100 KB do Data Layer)', async () => {
  const { q, partida } = await quadra({ alvo: 100, vantagem: false });
  for (let i = 0; i < 150; i++) await q.aplicarComandoRelogio(ponto(partida, i % 2 ? 'A' : 'B'));
  const bytes = Buffer.byteLength(JSON.stringify(q.snapshotParaRelogio()));
  assert.ok(bytes < 20_000, `estado com ${bytes} bytes`);
  assert.ok(Buffer.byteLength(JSON.stringify(q.snapshot())) > bytes, 'a linha do tempo fica de fora');
});

test('guarda só os últimos recibos', async () => {
  const { arm, q, partida } = await quadra({ alvo: 100 });
  const registro = JSON.parse(arm.mapa.get(CHAVE_QUADRA_LOCAL));
  registro.recibos = Array.from({ length: 499 }, (_, i) => ({ id: `r${i}`, partida_id: 'p', acao: 'ponto', equipe: 'A', alvo: null, status: 'RECUSADO', detalhe: 'x', evento_seq: null }));
  arm.mapa.set(CHAVE_QUADRA_LOCAL, JSON.stringify(registro));
  const { quadra: q2 } = await QuadraLocal.abrir(arm, opcoes());
  const p2 = q2.snapshot().partida_id;
  await q2.aplicarComandoRelogio(ponto(p2, 'A'));
  await q2.aplicarComandoRelogio(ponto(p2, 'B'));
  assert.equal(q2.registro.recibos.length, 500);
  assert.equal(q2.registro.recibos[0].id, 'r1');
  void q; void partida;
});
