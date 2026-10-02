// CV7.US1 — a quadra local do aparelho: log guardado, comandos, recuperação.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { CHAVE_ILEGIVEL, CHAVE_QUADRA_LOCAL, ErroGravacao, QuadraLocal } from '../src/lib/quadraLocal.js';
import { ErroRegra } from '../src/lib/partida.js';

/** Armazenamento em memória, com falha de gravação sob demanda. */
function memoria(inicial = {}) {
  const mapa = new Map(Object.entries(inicial));
  return {
    mapa,
    falharGravacao: false,
    falharLeitura: false,
    async ler(chave) {
      if (this.falharLeitura) throw new Error('leitura');
      return mapa.get(chave) ?? null;
    },
    async gravar(chave, valor) {
      if (this.falharGravacao) throw new Error('gravação');
      mapa.set(chave, valor);
    },
    async apagar(chave) { mapa.delete(chave); },
  };
}

function opcoes() {
  let n = 0;
  return { apelido: 'Eli', agora: () => '2026-10-02T12:00:00+00:00', novoId: () => `id-${++n}` };
}

test('cria a quadra com os padrões do servidor e guarda no aparelho', async () => {
  const arm = memoria();
  const q = await QuadraLocal.criar(arm, opcoes());
  const s = q.snapshot();
  assert.equal(s.quadra.id, 'LOCAL');
  assert.deepEqual([s.estado_partida.alvo, s.estado_partida.vantagem, s.estado_partida.pontos_a], [10, true, 0]);
  assert.equal(s.quadra.controle_id, q.eu.id);
  assert.equal(q.eu.papel, 'ADMIN');
  assert.ok(arm.mapa.has(CHAVE_QUADRA_LOCAL));
});

test('o placar sobrevive a fechar e reabrir o app', async () => {
  const arm = memoria();
  const q = await QuadraLocal.criar(arm, opcoes(), { alvo: 3 });
  await q.marcarPonto('A');
  await q.marcarPonto('B');
  await q.desfazer();
  await q.marcarPonto('A');

  const { quadra: reaberta, ilegivel } = await QuadraLocal.abrir(arm, opcoes());
  assert.equal(ilegivel, false);
  assert.deepEqual(reaberta.snapshot().estado_partida, q.snapshot().estado_partida);
  assert.deepEqual(reaberta.snapshot().linha_do_tempo, q.snapshot().linha_do_tempo);
  assert.equal(reaberta.snapshot().estado_partida.pontos_a, 2);
});

test('partida até o fim, nova partida e tema do placar', async () => {
  const arm = memoria();
  const q = await QuadraLocal.criar(arm, opcoes(), { alvo: 2, vantagem: false });
  assert.equal(q.emAndamento, true);
  await q.marcarPonto('A');
  const fim = await q.marcarPonto('A');
  assert.equal(fim.estado_partida.encerrada, true);
  assert.equal(q.emAndamento, false);
  await assert.rejects(q.marcarPonto('B'), (e) => e instanceof ErroRegra && e.status === 400);

  const nova = await q.reiniciar({ equipe_a: 'Azuis', tema_placar: 'classico' });
  assert.deepEqual([nova.estado_partida.pontos_a, nova.estado_partida.equipe_a, nova.estado_partida.alvo, nova.quadra.tema_placar], [0, 'Azuis', 2, 'classico']);
  assert.notEqual(nova.partida_id, fim.partida_id);
  assert.equal(q.emAndamento, true);

  // O histórico de partidas anteriores continua no log, mas a tela mostra a atual.
  const { quadra } = await QuadraLocal.abrir(arm, opcoes());
  assert.equal(quadra.snapshot().partida_id, nova.partida_id);
  assert.equal(quadra.snapshot().quadra.tema_placar, 'classico');
});

test('zerar reinicia no meio da partida mantendo regras e nomes', async () => {
  const q = await QuadraLocal.criar(memoria(), opcoes(), { alvo: 15, equipe_a: 'Azuis' });
  const meio = await q.marcarPonto('A');
  await assert.rejects(q.reiniciar(), (e) => e instanceof ErroRegra && e.status === 400);
  const zerada = await q.reiniciar({ zerar: true });
  assert.deepEqual([zerada.estado_partida.pontos_a, zerada.estado_partida.alvo, zerada.estado_partida.equipe_a], [0, 15, 'Azuis']);
  assert.notEqual(zerada.partida_id, meio.partida_id);
});

test('configurar só o tema não cria evento; tema inválido é recusado', async () => {
  const q = await QuadraLocal.criar(memoria(), opcoes());
  const antes = q.snapshot().seq;
  const s = await q.configurar({ tema_placar: 'classico' });
  assert.deepEqual([s.seq, s.quadra.tema_placar], [antes, 'classico']);
  await assert.rejects(q.configurar({ tema_placar: 'neon' }), (e) => e instanceof ErroRegra && e.status === 422);
  const regras = await q.configurar({ alvo: 15, equipe_a: 'Rubros' });
  assert.deepEqual([regras.estado_partida.alvo, regras.estado_partida.equipe_a, regras.seq], [15, 'Rubros', antes + 1]);
});

test('falha ao gravar: o ponto não vale e o placar fica como estava', async () => {
  const arm = memoria();
  const q = await QuadraLocal.criar(arm, opcoes());
  await q.marcarPonto('A');
  arm.falharGravacao = true;
  await assert.rejects(q.marcarPonto('B'), ErroGravacao);
  assert.equal(q.snapshot().estado_partida.pontos_b, 0);
  // E o próximo toque, com o armazenamento de volta, entra normalmente.
  arm.falharGravacao = false;
  assert.equal((await q.marcarPonto('B')).estado_partida.pontos_b, 1);
});

test('toques rápidos entram na ordem e nenhum se perde', async () => {
  const q = await QuadraLocal.criar(memoria(), opcoes(), { alvo: 50 });
  const toques = ['A', 'B', 'A', 'A', 'B', 'A', 'B', 'B'];
  await Promise.all(toques.map((e) => q.marcarPonto(e)));
  const s = q.snapshot();
  assert.deepEqual([s.estado_partida.pontos_a, s.estado_partida.pontos_b], [4, 4]);
  assert.deepEqual(s.estado_partida.equipes_ativas, toques);
  // Nem um falho no meio da fila derruba os seguintes.
  const resultados = await Promise.allSettled([q.desfazer(), q.configurar({ tema_placar: 'neon' }), q.marcarPonto('A')]);
  assert.deepEqual(resultados.map((r) => r.status), ['fulfilled', 'rejected', 'fulfilled']);
});

test('dados ilegíveis não derrubam o app: ficam guardados e a pessoa decide', async () => {
  const lixo = '{"versao":1,"quadra":{"id":"LOCAL"},"eventos":[]}';
  for (const bruto of ['não é json', lixo, JSON.stringify({ versao: 99 })]) {
    const arm = memoria({ [CHAVE_QUADRA_LOCAL]: bruto });
    const { quadra, ilegivel } = await QuadraLocal.abrir(arm, opcoes());
    assert.deepEqual([quadra, ilegivel], [null, true]);
    assert.equal(arm.mapa.get(CHAVE_ILEGIVEL), bruto);
    // Os dados originais seguem lá até alguém descartar.
    assert.equal(arm.mapa.get(CHAVE_QUADRA_LOCAL), bruto);
    await QuadraLocal.descartarIlegivel(arm);
    assert.deepEqual([...arm.mapa.keys()], []);
  }
});

test('log com buraco na numeração é tratado como ilegível', async () => {
  const arm = memoria();
  const q = await QuadraLocal.criar(arm, opcoes(), { alvo: 9 });
  await q.marcarPonto('A');
  await q.marcarPonto('B');
  const registro = JSON.parse(arm.mapa.get(CHAVE_QUADRA_LOCAL));
  registro.eventos.splice(1, 1);
  arm.mapa.set(CHAVE_QUADRA_LOCAL, JSON.stringify(registro));
  assert.equal((await QuadraLocal.abrir(arm, opcoes())).ilegivel, true);
});

test('erro de leitura do aparelho sobe, em vez de parecer dado ilegível', async () => {
  const arm = memoria();
  arm.falharLeitura = true;
  await assert.rejects(QuadraLocal.abrir(arm, opcoes()), /leitura/);
});

test('sem quadra guardada, abrir devolve nada e apagar limpa o aparelho', async () => {
  const arm = memoria();
  assert.deepEqual(await QuadraLocal.abrir(arm, opcoes()), { quadra: null, ilegivel: false });
  const q = await QuadraLocal.criar(arm, opcoes());
  await q.apagar();
  assert.deepEqual(await QuadraLocal.abrir(arm, opcoes()), { quadra: null, ilegivel: false });
});
