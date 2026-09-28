import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { CHAVE_APELIDO, guardarApelido, lerApelido, nomeDoPapel, seloDoPapel } from '../src/lib/preferencias.js';

function memoria(inicial = {}) {
  const dados = { ...inicial };
  return {
    dados,
    getItem: k => (k in dados ? dados[k] : null),
    setItem: (k, v) => { dados[k] = String(v); },
    removeItem: k => { delete dados[k]; },
  };
}

test('apelido guardado na Home aparece na entrada por link', () => {
  const armazenamento = memoria();
  guardarApelido('Eli', armazenamento);
  assert.equal(lerApelido(armazenamento), 'Eli');
  assert.equal(armazenamento.dados[CHAVE_APELIDO], 'Eli');
});

test('apelido da chave antiga é migrado uma vez', () => {
  const armazenamento = memoria({ placar_ultimo_apelido: 'Bia' });
  assert.equal(lerApelido(armazenamento), 'Bia');
  assert.equal(armazenamento.dados[CHAVE_APELIDO], 'Bia');
  assert.equal('placar_ultimo_apelido' in armazenamento.dados, false);
});

test('armazenamento indisponível não quebra a tela', () => {
  const quebrado = { getItem() { throw new Error('bloqueado'); }, setItem() { throw new Error('bloqueado'); } };
  assert.equal(lerApelido(quebrado), '');
  guardarApelido('x', quebrado);
});

test('selo mostra o papel legível', () => {
  assert.equal(nomeDoPapel('CONTROLADOR'), 'Controlador');
  assert.equal(nomeDoPapel('ADMIN'), 'Admin');
  assert.equal(nomeDoPapel(undefined), '');
});

test('selo curto do topo: letra e dica por papel', () => {
  assert.deepEqual(seloDoPapel('ADMIN'), { letra: 'A', dica: 'Administrador da quadra' });
  assert.deepEqual(seloDoPapel('CONTROLADOR'), { letra: 'C', dica: 'Controlador do placar' });
  assert.equal(seloDoPapel('ESPECTADOR'), null);
});

test('conexão tem um só vocabulário e vitória um só texto', () => {
  const ler = f => readFileSync(new URL(`../src/components/${f}`, import.meta.url), 'utf8');
  const sala = ler('SalaQuadra.svelte');
  assert.doesNotMatch(sala, /Conectando\.\.\.|Sem conexão — reconectando/);
  for (const f of ['Placar.svelte', 'PlacarManual.svelte']) assert.doesNotMatch(ler(f), /Vitória d[ae] /);
  assert.doesNotMatch(ler('Placar.svelte'), /#a5f3fc/);
});

test('tamanho dos números: padrão M, guarda escolha válida e ignora lixo', async () => {
  const { lerTamanhoNumeros, guardarTamanhoNumeros, proximoTamanhoNumeros, CHAVE_TAMANHO_NUMEROS } = await import('../src/lib/preferencias.js');
  const m = memoria();
  assert.equal(lerTamanhoNumeros(m), 'M');
  guardarTamanhoNumeros('G', m);
  assert.equal(lerTamanhoNumeros(m), 'G');
  m.setItem(CHAVE_TAMANHO_NUMEROS, 'XL');
  assert.equal(lerTamanhoNumeros(m), 'M');
  assert.equal(lerTamanhoNumeros({ getItem() { throw new Error('bloqueado'); } }), 'M');
  assert.deepEqual(['P', 'M', 'G'].map(proximoTamanhoNumeros), ['M', 'G', 'P']);
});
