// CV7.TS2 — paridade das regras em JS com o backend Python.
// As fixtures vêm de `uv run python -m tests.paridade_fixtures`; o pytest
// falha se elas ficarem para trás da regra em Python.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import {
  ErroRegra,
  MSG_ALVO_MUDOU,
  desfazerPonto,
  configurarPartida,
  iniciarPartida,
  marcarPonto,
  projetarEstado,
  projetarLinhaDoTempo,
  projetarPartida,
  reiniciarPartida,
} from '../src/lib/partida.js';

const fixtures = JSON.parse(readFileSync(new URL('./fixtures/paridade.json', import.meta.url), 'utf8'));

for (const caso of fixtures.projecoes) {
  test(`projeção: ${caso.nome}`, () => {
    assert.deepEqual(projetarEstado(caso.eventos), caso.estado);
    assert.deepEqual(projetarLinhaDoTempo(caso.eventos, caso.apelidos), caso.linha_do_tempo);
  });
}

/** Mesmo recorte que o gerador: sem ids, horários e id de partida. */
function normalizar(partida, ordinais) {
  const ordinal = (id) => (id === null ? null : (ordinais.get(id) ?? ordinais.set(id, `P${ordinais.size + 1}`).get(id)));
  return {
    partida_id: ordinal(partida.partida_id),
    seq: partida.seq,
    estado_partida: { ...partida.estado_partida, partida_id: ordinal(partida.estado_partida.partida_id) },
    linha_do_tempo: partida.linha_do_tempo.map(({ id, criado_em, autor_id, ...resto }) => resto),
  };
}

/** Uma quadra local mínima: o log da partida atual e o relógio de mentira. */
function novaQuadra(cenario) {
  let n = 0;
  const ctx = { quadraId: 'q', autorId: 'eu', agora: () => '2026-10-01T12:00:00+00:00', novoId: () => `id-${++n}` };
  const apelidos = { eu: cenario.apelido };
  const quadra = { eventos: iniciarPartida(ctx, 'partida-1', cenario.criar), partidas: 1 };
  const snapshot = () => projetarPartida(quadra.eventos, apelidos);
  const aplicar = (passo) => {
    const { acao } = passo;
    let novos;
    if (acao === 'pontos') novos = marcarPonto(quadra.eventos, passo.equipe, ctx);
    else if (acao === 'desfazer') novos = desfazerPonto(quadra.eventos, null, ctx);
    else if (acao === 'configurar') novos = configurarPartida(quadra.eventos, passo.campos, ctx);
    else {
      novos = reiniciarPartida(quadra.eventos, passo.campos, ctx, `partida-${quadra.partidas + 1}`);
      quadra.partidas += 1;
      quadra.eventos = novos;
      return;
    }
    quadra.eventos = [...quadra.eventos, ...novos];
  };
  return { snapshot, aplicar };
}

for (const cenario of fixtures.cenarios) {
  test(`cenário: ${cenario.nome}`, () => {
    const ordinais = new Map();
    const { snapshot, aplicar } = novaQuadra(cenario);
    assert.deepEqual(normalizar(snapshot(), ordinais), cenario.inicial, 'estado inicial');

    cenario.passos.forEach((passo, i) => {
      const esperado = cenario.resultados[i];
      const rotulo = `passo ${i + 1} (${JSON.stringify(passo)})`;
      let erro = null;
      try {
        aplicar(passo);
      } catch (e) {
        if (!(e instanceof ErroRegra)) throw e;
        erro = e;
      }
      if (esperado.status >= 400) {
        assert.ok(erro, `${rotulo}: o servidor recusou com ${esperado.status} e o JS aceitou`);
        assert.equal(erro.status, esperado.status, `${rotulo}: status`);
        if (esperado.detalhe !== null) assert.equal(erro.message, esperado.detalhe, `${rotulo}: detalhe`);
      } else {
        assert.equal(erro, null, `${rotulo}: o servidor aceitou e o JS recusou (${erro?.message})`);
        assert.deepEqual(normalizar(snapshot(), ordinais), esperado.snapshot, rotulo);
      }
    });
  });
}

test('desfazer com alvo que não é o topo não anula outro ponto', () => {
  let n = 0;
  const ctx = { quadraId: 'q', autorId: 'eu', agora: () => 't', novoId: () => `id-${++n}` };
  let eventos = iniciarPartida(ctx, 'p', { alvo: 5 });
  eventos = [...eventos, ...marcarPonto(eventos, 'A', ctx)];
  eventos = [...eventos, ...marcarPonto(eventos, 'B', ctx)];
  assert.throws(
    () => desfazerPonto(eventos, 2, ctx),
    (e) => e instanceof ErroRegra && e.status === 409 && e.message === MSG_ALVO_MUDOU,
  );
  const [desfeito] = desfazerPonto(eventos, 3, ctx);
  assert.equal(desfeito.payload.ref_seq, 3);
});

test('quadra com teto menor que o alvo é recusada na criação', () => {
  const ctx = { quadraId: 'q', autorId: null, agora: () => 't', novoId: () => 'i' };
  assert.throws(() => iniciarPartida(ctx, 'p', { alvo: 10, teto: 5 }), (e) => e instanceof ErroRegra && e.status === 422);
});
