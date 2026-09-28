import { test } from 'node:test';
import assert from 'node:assert/strict';
import { podePassarControle } from '../src/lib/controle.js';

const ctx = { euId: 'eli', controleId: 'eli', ehAdmin: true };

test('admin pode passar o controle para controlador, inclusive o relógio', () => {
  assert.equal(podePassarControle({ id: 'relogio', papel: 'CONTROLADOR' }, ctx), true);
  assert.equal(podePassarControle({ id: 'ana', papel: 'ADMIN' }, ctx), true);
});

test('não oferece passar para espectador, para si, para quem já controla ou sem ser admin', () => {
  assert.equal(podePassarControle({ id: 'rafa', papel: 'ESPECTADOR' }, ctx), false);
  assert.equal(podePassarControle({ id: 'eli', papel: 'ADMIN' }, ctx), false);
  assert.equal(podePassarControle({ id: 'relogio', papel: 'CONTROLADOR' }, { ...ctx, controleId: 'relogio' }), false);
  assert.equal(podePassarControle({ id: 'relogio', papel: 'CONTROLADOR' }, { ...ctx, ehAdmin: false }), false);
});

import { ultimoPontoDesfazivel, descreverPosse } from '../src/lib/controle.js';

test('desfazer aponta o último ponto ativo da partida atual', () => {
  const itens = [
    { tipo: 'PARTIDA_INICIADA' },
    { tipo: 'PONTO_MARCADO', equipe: 'A' },
    { tipo: 'PONTO_MARCADO', equipe: 'B', anulado: true },
    { tipo: 'PONTO_DESFEITO' },
    { tipo: 'CONTROLE_ASSUMIDO' },
  ];
  assert.equal(ultimoPontoDesfazivel(itens), 'A');
  assert.equal(ultimoPontoDesfazivel([]), null);
});

test('pontos da partida anterior não são oferecidos para desfazer', () => {
  const itens = [
    { tipo: 'PARTIDA_INICIADA' },
    { tipo: 'PONTO_MARCADO', equipe: 'B' },
    { tipo: 'PARTIDA_ENCERRADA' },
    { tipo: 'PARTIDA_INICIADA' },
  ];
  assert.equal(ultimoPontoDesfazivel(itens), null);
});

test('posse é distinta do papel', () => {
  assert.deepEqual(descreverPosse({ temControle: true, ehAdmin: true, operador: 'Eli' }).podeAssumir, false);
  const relogio = descreverPosse({ temControle: false, ehAdmin: true, operador: 'Eli (Relógio)' });
  assert.equal(relogio.titulo, 'Controle com Eli (Relógio)');
  assert.equal(relogio.podeAssumir, true);
  assert.match(descreverPosse({ temControle: false, ehAdmin: false, operador: 'Ana' }).detalhe, /controlador/);
  assert.match(descreverPosse({ temControle: true, conectado: false }).detalhe, /Sem conexão/);
});

import { readFileSync } from 'node:fs';
import { compile } from 'svelte/compiler';

const ler = (nome) => readFileSync(new URL(`../src/components/${nome}`, import.meta.url), 'utf8');
const placar = ler('Placar.svelte');
const salaFonte = ler('SalaQuadra.svelte');

test('operação compila sem avisos', () => {
  assert.equal(compile(placar, { filename: 'Placar.svelte' }).warnings.length, 0);
  assert.equal(compile(salaFonte, { filename: 'SalaQuadra.svelte' }).warnings.length, 0);
});

test('+1 acompanham a inversão de lados e o desfazer fica no meio (CV6.DS1.US2)', () => {
  assert.match(placar, /\.lados-invertidos \.palco \{ grid-template-areas: 'resultado resultado' 'b a' 'desfazer desfazer'; \}/);
  assert.match(placar, /\.lados-invertidos \.palco \{ grid-template-areas: 'resultado resultado resultado' 'b desfazer a'; \}/);
});

test('desfazer fica fora de menu e sem confirmação', () => {
  assert.match(placar, /class="btn-desfazer"[\s\S]*?onclick=\{handleToqueDesfazer\}/);
  assert.doesNotMatch(placar, /confirm\(/);
});

test('ações secundárias aparecem uma vez só, no menu', () => {
  for (const rotulo of ['Compartilhar e QR', 'Linha do tempo', 'Relógio']) {
    assert.equal(salaFonte.split(`rotulo: '${rotulo}'`).length - 1, 1, rotulo);
  }
  assert.doesNotMatch(placar, /Duplas & Regras|Linha do Tempo/);
  assert.match(salaFonte, /<MenuSala acoes=\{acoesDoMenu\}/);
  // Duplas e regras e inverter lados moram no cabeçalho (CV6.DS1.US1).
  assert.doesNotMatch(salaFonte, /rotulo: 'Duplas e regras'/);
  assert.doesNotMatch(placar, /onAlternarLados/);
});

test('papel aparece em selo neutro com letra circulada, fora da faixa de posse', () => {
  assert.match(salaFonte, /class="btn-topo selo-papel" onclick=\{mostrarDicaSelo\} aria-label=\{selo\.dica\}/);
  assert.ok(salaFonte.indexOf('selo-papel-ancora') > salaFonte.indexOf('<div class="faixa-posse"'));
  assert.doesNotMatch(salaFonte, /badge-admin/);
});

test('operação reusa a representação clássica pura, sem grade própria', () => {
  assert.match(placar, /<PlacarClassico/);
  assert.doesNotMatch(placar, /CartaoDobravel|placar-grid/);
});

const menu = ler('MenuSala.svelte');
const dialogo = ler('Dialogo.svelte');
const presentes = ler('ListaPresentes.svelte');
const css = readFileSync(new URL('../src/app.css', import.meta.url), 'utf8');

test('menu da sala compila e é o único lugar de presentes, tema e compartilhar para o espectador', () => {
  assert.equal(compile(menu, { filename: 'MenuSala.svelte' }).warnings.length, 0);
  assert.doesNotMatch(salaFonte, /presentes-sobrepostos|btn-tema-header|btn-compartilhar-header|btn-girar/);
  assert.equal((salaFonte.match(/<ListaPresentes/g) ?? []).length, 1);
});

test('diálogo devolve o foco a quem o abriu e mostra o campo acima do teclado', () => {
  assert.equal(compile(dialogo, { filename: 'Dialogo.svelte' }).warnings.length, 0);
  assert.match(dialogo, /const acionador = typeof document === 'undefined' \? null : document\.activeElement;/);
  assert.match(dialogo, /acionador\.focus/);
  assert.match(dialogo, /onfocusin=\{aoFocar\}/);
  const index = readFileSync(new URL('../index.html', import.meta.url), 'utf8');
  assert.match(index, /interactive-widget=resizes-content/);
});

test('papéis não usam as cores das equipes', () => {
  assert.doesNotMatch(css, /--papel-admin-texto: #fb923c/);
  assert.doesNotMatch(css, /--papel-controlador-texto: #38bdf8/);
  assert.doesNotMatch(presentes, /accent-orange/);
});

test('resumo das regras mostra alvo, vantagem e teto', async () => {
  const { resumirRegras } = await import('../src/lib/controle.js');
  assert.equal(resumirRegras({ alvo: 12, vantagem: true, teto: null }), '12 pontos · Vantagem');
  assert.equal(resumirRegras({ alvo: 15, vantagem: false }), '15 pontos · Sem vantagem');
  assert.equal(resumirRegras({ alvo: 21, vantagem: true, teto: 25 }), '21 pontos · Vantagem · Teto 25');
  assert.equal(resumirRegras(null), '10 pontos · Vantagem');
});

test('resumo curto do topo mostra só o alvo', async () => {
  const { resumirRegrasCurto } = await import('../src/lib/controle.js');
  assert.equal(resumirRegrasCurto({ alvo: 12, vantagem: true, teto: 15 }), '12 pt');
  assert.equal(resumirRegrasCurto(null), '10 pt');
});
