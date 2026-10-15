// CV8.DS9.US25 — Resenha do Joguinho: a tela do print para o grupo.
// Os números vêm do servidor (testados em tests/test_estatisticas.py); aqui a
// resposta é fixa para conferir a tela, a acessibilidade e a largura do celular.
import AxeBuilder from '@axe-core/playwright';
import { test, expect } from './apoio.js';

const SEGREDO = 'segredo-e2e';

const jogador = (id, nome, completo, genero = 'H') => ({ id, nome, nome_completo: completo, genero, tem_foto: false });

const RESENHA = {
  sessao: { id: 's1', aberta_em: '2026-10-15T20:00:00+00:00', encerrada_em: '2026-10-15T23:00:00+00:00' },
  resumo: { partidas: 4, pontos: 68, jogadores: 4, rodadas: 1 },
  premios: [
    { id: 'rei', emoji: '👑', titulo: 'Rainha do dia', texto: '3 vitórias em 3 jogos', tom: 'positivo', jogadores: ['a'] },
    { id: 'pneu', emoji: '🍩', titulo: 'Pneu do dia', texto: 'tomou 10 x 2 e saiu de rosquinha', tom: 'negativo', jogadores: ['c', 'd'],
      partida: { rodada: 1, placar_a: 10, placar_b: 2, lado_a: ['a', 'b'], lado_b: ['c', 'd'] } },
    { id: 'pe_frio', emoji: '🥶', titulo: 'Pé-frio', texto: '3 derrotas em 3 jogos', tom: 'negativo', jogadores: ['c'] },
  ],
  campeoes: [{ rodada: 1, jogadores: ['a', 'b'] }],
  galeria: [
    { jogador: 'a', emoji: '👑', titulo: 'Rainha do dia', tom: 'positivo', selos: ['🏆'], vitorias: 3, derrotas: 0, saldo: 12 },
    { jogador: 'c', emoji: '🍩', titulo: 'Tomou pneu', tom: 'negativo', selos: ['🥶'], vitorias: 0, derrotas: 3, saldo: -12 },
  ],
  tabela: [
    { jogador: 'a', jogos: 3, vitorias: 3, derrotas: 0, aproveitamento: 100, pro: 30, contra: 18, saldo: 12, delta_nota: 4 },
    { jogador: 'c', jogos: 3, vitorias: 0, derrotas: 3, aproveitamento: 0, pro: 18, contra: 30, saldo: -12, delta_nota: -4 },
  ],
  jogadores: {
    a: jogador('a', 'Ana', 'Ana Lima', 'M'),
    b: jogador('b', 'Beto', 'Beto Reis'),
    c: jogador('c', 'Caio', 'Caio Melo'),
    d: jogador('d', 'Duda', 'Duda Alves', 'M'),
  },
};

test('o Joguinho abre a Resenha com prêmios, galeria e tabela, sem rolagem lateral', async ({ abrir }) => {
  const p = await abrir();
  await p.setViewportSize({ width: 390, height: 844 });
  await p.route('**/api/sessao/estatisticas', (rota) => rota.fulfill({ json: RESENHA }));
  await p.goto('/joguinho');
  await p.getByLabel('Segredo do dono').fill(SEGREDO);
  await p.getByRole('button', { name: 'Entrar' }).click();
  await p.getByRole('button', { name: 'Resenha' }).click();

  await expect(p).toHaveURL(/\/joguinho\/resenha$/);
  // capa, 1 cartão de prêmios (o rei fica na capa), 1 de galeria e 1 de tabela
  const cartoes = p.locator('.cartao');
  await expect(cartoes).toHaveCount(4);
  await expect(cartoes.nth(0).getByRole('heading', { name: 'Rainha do dia' })).toBeVisible();
  await expect(cartoes.nth(0)).toContainText('quinta, 15/10');
  await expect(cartoes.nth(1).getByRole('heading', { name: /Pneu do dia/ })).toBeVisible();
  await expect(p.getByText('Ana & Beto venceram Caio & Duda')).toBeVisible();
  await expect(p.locator('.retrato')).toHaveCount(2);
  await expect(p.locator('.retrato').nth(1)).toContainText('Tomou pneu');
  await expect(p.getByRole('row', { name: /Caio/ })).toContainText('-12');
  await expect(cartoes.nth(3)).toContainText('4/4');

  // cartão 4:5 na largura útil da tela
  const caixa = await cartoes.nth(0).boundingBox();
  expect(caixa.width).toBeGreaterThan(340);
  expect(Math.abs(caixa.height / caixa.width - 1.25)).toBeLessThan(0.01);

  const baixados = [];
  p.on('download', (d) => baixados.push(d));
  await p.getByRole('button', { name: 'Baixar 4 imagens' }).click();
  await expect(p.getByRole('status')).toContainText('4 imagens baixadas');
  await expect.poll(() => baixados.length).toBe(4);
  expect(baixados.map((d) => d.suggestedFilename()).sort()).toEqual([1, 2, 3, 4].map((n) => `resenha-2026-10-15-${n}.png`));
  const png = await (await baixados[0].createReadStream()).toArray();
  const bytes = Buffer.concat(png);
  // largura e altura no cabeçalho IHDR do PNG
  expect([bytes.readUInt32BE(16), bytes.readUInt32BE(20)]).toEqual([1080, 1350]);

  const largura = await p.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  expect(largura).toBeLessThanOrEqual(0);

  await p.evaluate(() => Promise.all(document.getAnimations().filter((a) => a.effect?.getTiming().iterations !== Infinity).map((a) => a.finished.catch(() => {}))));
  const { violations } = await new AxeBuilder({ page: p }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze();
  expect(violations.map((v) => `${v.id}: ${v.nodes.map((n) => n.target.join(' ') + ' ' + (n.any[0]?.message ?? '')).join(' | ')}`)).toEqual([]);

  await p.getByRole('button', { name: 'Joguinho' }).click();
  await expect(p.getByRole('heading', { name: 'Joguinho', level: 1 })).toBeVisible();
});

test('sem joguinho nenhum, a Resenha avisa', async ({ abrir }) => {
  const p = await abrir();
  await p.route('**/api/sessao/estatisticas', (rota) => rota.fulfill({ json: { sessao: null } }));
  await p.addInitScript((s) => localStorage.setItem('placar:segredo_dono', s), SEGREDO);
  await p.goto('/joguinho/resenha');
  await expect(p.getByText('Sem jogo, sem resenha')).toBeVisible();
});
