// CV8.DS3.US5 — painel da condução, chamar partida no placar e sincronia.
import AxeBuilder from '@axe-core/playwright';
import { test, expect } from './apoio.js';

const SEGREDO = 'segredo-e2e';
const CABECALHO = { 'x-owner-secret': SEGREDO };

async function sessaoLimpa(p) {
  await p.request.post('/api/rodada/descartar', { headers: CABECALHO });
  await p.request.post('/api/rodada/cancelar', { headers: CABECALHO });
  await p.request.delete('/api/sessao/quadra', { headers: CABECALHO });
  await p.request.post('/api/sessao/encerrar', { headers: CABECALHO });
}

async function chegam(p, lista) {
  expect((await p.request.post('/api/sessao', { headers: CABECALHO })).status()).toBe(201);
  const nomes = [];
  for (const [rotulo, genero, nota] of lista) {
    const nome = `${rotulo} ${Math.random().toString(36).slice(2, 7)}`;
    const j = await p.request.post('/api/jogadores', { headers: CABECALHO, data: { nome, genero, nota } });
    const { id } = await j.json();
    expect((await p.request.put(`/api/sessao/presencas/${id}`, { headers: CABECALHO })).status()).toBe(200);
    nomes.push(nome);
  }
  return nomes;
}

async function rodadaConfirmada(p, alvo = 12) {
  expect((await p.request.post('/api/rodada/sorteio', { headers: CABECALHO, data: { alvo } })).status()).toBe(201);
  expect((await p.request.post('/api/rodada/confirmar', { headers: CABECALHO })).status()).toBe(200);
}

async function abrirTela(p) {
  await p.goto('/');
  await p.getByRole('button', { name: 'Sessão', exact: true }).click();
  await p.getByLabel('Segredo do dono').fill(SEGREDO);
  await p.getByRole('button', { name: 'Entrar' }).click();
  await p.getByRole('heading', { name: 'Sessão', level: 1 }).waitFor();
}

const SEIS = [['Ana', 'M', 90], ['Bia', 'M', 80], ['Caio', 'H', 70], ['Davi', 'H', 60], ['Eva', 'M', 50], ['Fabio', 'H', 40]];

test('sem quadra vinculada a chamada fica bloqueada com o motivo', async ({ abrir }) => {
  const p = await abrir();
  await sessaoLimpa(p);
  await chegam(p, SEIS);
  await rodadaConfirmada(p);
  await abrirTela(p);
  await expect(p.getByRole('heading', { name: /Rodada 1/ })).toContainText('alvo 12');
  await expect(p.getByRole('button', { name: 'Chamar partida' })).toBeDisabled();
  await expect(p.getByText('Vincule uma quadra do placar para chamar a partida.')).toBeVisible();
  // painel inicial: fila, reis e eliminados com os textos vazios
  await expect(p.getByRole('heading', { name: 'Fila (1)' })).toBeVisible();
  await expect(p.getByText('Ninguém com 2 vitórias seguidas ainda.')).toBeVisible();
  await expect(p.getByText('Ninguém perdeu ainda.')).toBeVisible();
  await expect(p.getByRole('status').filter({ hasText: 'Time 1 × Time 2' })).toBeVisible();
});

test('criar quadra, vincular, chamar partida e ver as duplas no placar', async ({ abrir }) => {
  const p = await abrir();
  await sessaoLimpa(p);
  const nomes = await chegam(p, SEIS);
  await rodadaConfirmada(p, 12);
  await abrirTela(p);

  await p.getByRole('button', { name: 'Criar quadra e vincular' }).click();
  await expect(p.getByText('disponível', { exact: true })).toBeVisible();
  const link = p.getByRole('link', { name: 'Abrir o placar' });
  const href = await link.getAttribute('href');
  expect(href).toMatch(/^\/quadra\/\d{5}$/);

  // placar aberto na mesma sessão do navegador (admin): vê as duplas chegarem sem recarregar
  const placar = await p.context().newPage();
  await placar.goto(href);
  await placar.getByLabel(/Marcar ponto para/).first().waitFor();

  await expect(p.getByRole('button', { name: 'Chamar partida' })).toBeEnabled();
  await p.getByRole('button', { name: 'Chamar partida' }).click();
  await expect(p.getByRole('heading', { name: 'Partida em quadra' })).toBeVisible();
  await expect(p.getByText('chamada', { exact: true })).toBeVisible();
  await expect(p.getByRole('button', { name: 'Chamar partida' })).toBeDisabled();
  await expect(p.getByText(/Já há uma partida chamada/)).toBeVisible();

  // a primeira a chegar (Ana) joga a primeira partida: o nome dela está no placar
  const primeiro = nomes[0].split(' ')[0];
  await expect(placar.getByText(new RegExp(primeiro)).first()).toBeVisible();
  await expect(placar.getByText(/ \+ /).first()).toBeVisible();
  await sessaoLimpa(p);
});

test('quadra vinculada por código e indisponível quando some', async ({ abrir }) => {
  const p = await abrir();
  await sessaoLimpa(p);
  await chegam(p, SEIS);
  await rodadaConfirmada(p);
  const criada = await p.request.post('/api/quadras', { data: { apelido: 'Eli', nome: 'Existente' } });
  const { id } = await criada.json();
  await abrirTela(p);
  await p.getByLabel('Ou vincule uma quadra existente pelo código').fill('00000');
  await p.getByRole('button', { name: 'Vincular', exact: true }).click();
  await expect(p.getByRole('alert')).toContainText('não encontrada ou expirada');
  await p.getByLabel('Ou vincule uma quadra existente pelo código').fill(id);
  await p.getByRole('button', { name: 'Vincular', exact: true }).click();
  await expect(p.getByText(`Quadra ${id}`)).toBeVisible();
  await expect(p.getByRole('button', { name: 'Chamar partida' })).toBeEnabled();
  await p.getByRole('button', { name: 'Desvincular' }).click();
  await expect(p.getByText('Nenhuma quadra vinculada.')).toBeVisible();
});

test('dois aparelhos na sessão veem as mudanças sem atualizar', async ({ abrir }) => {
  const a = await abrir();
  await sessaoLimpa(a);
  await chegam(a, SEIS);
  const b = await abrir();
  await abrirTela(a);
  await abrirTela(b);
  await expect(a.getByText('Ao vivo')).toBeVisible();
  await expect(b.getByText('Ao vivo')).toBeVisible();

  // A sorteia: B passa a mostrar a proposta sozinho
  await a.getByRole('button', { name: 'Sortear duplas' }).click();
  await expect(a.getByRole('heading', { name: /Proposta 1/ })).toBeVisible();
  await expect(b.getByRole('heading', { name: /Proposta 1/ })).toBeVisible();

  // B confirma: A vira o painel da condução
  await b.getByRole('button', { name: 'Confirmar e iniciar' }).click();
  await expect(a.getByRole('heading', { name: 'Quadra do placar' })).toBeVisible();
  await expect(b.getByRole('heading', { name: 'Quadra do placar' })).toBeVisible();

  // A cancela: B volta ao sorteio
  await a.getByRole('button', { name: 'Cancelar rodada' }).click();
  await a.getByRole('button', { name: 'Sim, cancelar rodada' }).click();
  await expect(b.getByRole('heading', { name: 'Sortear a rodada' })).toBeVisible();
  await sessaoLimpa(a);
});

test('painel da condução sem violações axe', async ({ abrir }) => {
  const p = await abrir({ viewport: { width: 390, height: 844 } });
  await sessaoLimpa(p);
  await chegam(p, SEIS);
  await rodadaConfirmada(p);
  await abrirTela(p);
  await p.getByRole('heading', { name: 'Quadra do placar' }).waitFor();
  await p.evaluate(() => Promise.all(document.getAnimations().filter((a) => a.effect?.getTiming().iterations !== Infinity).map((a) => a.finished.catch(() => {}))));
  const { violations } = await new AxeBuilder({ page: p }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze();
  expect(violations.map((v) => `${v.id}: ${v.nodes.map((n) => n.target.join(' ') + ' ' + (n.any[0]?.message ?? '')).join(' | ')}`)).toEqual([]);
  await sessaoLimpa(p);
});
