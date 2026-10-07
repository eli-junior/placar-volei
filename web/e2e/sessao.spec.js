// CV8.DS1.US2 — sessão do dia, presença e ordem de chegada no navegador real.
import AxeBuilder from '@axe-core/playwright';
import { test, expect } from './apoio.js';

const SEGREDO = 'segredo-e2e';

// Contraste medido no meio de um fade dá falso positivo: espera as animações.
async function violacoes(pagina) {
  await pagina.evaluate(() => Promise.all(document.getAnimations().filter((a) => a.effect?.getTiming().iterations !== Infinity).map((a) => a.finished.catch(() => {}))));
  const { violations } = await new AxeBuilder({ page: pagina }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze();
  return violations.map((v) => `${v.id}: ${v.nodes.map((n) => n.target.join(' ') + ' ' + (n.any[0]?.message ?? '')).join(' | ')}`);
}
const CABECALHO = { 'x-owner-secret': SEGREDO };

// A base do e2e é compartilhada: cada teste começa sem sessão aberta.
async function sessaoLimpa(p) {
  await p.request.post('/api/sessao/encerrar', { headers: CABECALHO });
}

async function criarJogador(p, rotulo, genero = 'M') {
  const nome = `${rotulo} ${Math.random().toString(36).slice(2, 7)}`;
  const r = await p.request.post('/api/jogadores', { headers: CABECALHO, data: { nome, genero } });
  expect(r.status()).toBe(201);
  return nome;
}

async function abrirTela(p) {
  await p.goto('/');
  await p.getByRole('button', { name: 'Sessão' }).click();
  await p.getByLabel('Segredo do dono').fill(SEGREDO);
  await p.getByRole('button', { name: 'Entrar' }).click();
  await p.getByRole('heading', { name: 'Sessão', level: 1 }).waitFor();
}

const presentes = (p) => p.locator('ol li .nome');

test('abrir, marcar na ordem de chegada, reordenar, desmarcar e encerrar', async ({ abrir }) => {
  const p = await abrir();
  await sessaoLimpa(p);
  const [a, b, c, d] = [await criarJogador(p, 'Ana'), await criarJogador(p, 'Bia'), await criarJogador(p, 'Caio', 'H'), await criarJogador(p, 'Davi', 'H')];
  await abrirTela(p);

  await expect(p.getByRole('heading', { name: 'Nenhuma sessão aberta' })).toBeVisible();
  await p.getByRole('button', { name: 'Abrir sessão' }).click();
  await expect(p.getByRole('status')).toContainText('Faltam 4');

  for (const n of [a, b, c]) await p.getByRole('button', { name: `Marcar ${n} como presente` }).click();
  await expect(presentes(p)).toHaveText([a, b, c]);
  await expect(p.getByRole('status')).toContainText('Faltam 1');

  await p.getByRole('button', { name: `Descer ${a}` }).click();
  await expect(presentes(p)).toHaveText([b, a, c]);
  await p.getByRole('button', { name: `Subir ${c}` }).click();
  await expect(presentes(p)).toHaveText([b, c, a]);
  await expect(p.getByRole('button', { name: `Subir ${b}` })).toBeDisabled();
  await expect(p.getByRole('button', { name: `Descer ${a}` })).toBeDisabled();

  // desmarcar e marcar de novo manda para o fim
  await p.getByRole('button', { name: `Desmarcar ${b}` }).click();
  await p.getByRole('button', { name: `Marcar ${b} como presente` }).click();
  await expect(presentes(p)).toHaveText([c, a, b]);
  await p.getByRole('button', { name: `Marcar ${d} como presente` }).click();
  await expect(p.getByRole('status')).toContainText('Já dá para sortear');

  // a ordem persiste ao recarregar
  await p.reload();
  await expect(presentes(p)).toHaveText([c, a, b, d]);

  await p.getByRole('button', { name: 'Encerrar sessão' }).click();
  await p.getByRole('button', { name: 'Sim, encerrar' }).click();
  await expect(p.getByRole('heading', { name: 'Nenhuma sessão aberta' })).toBeVisible();
});

test('cadastro rápido cria o jogador e marca no fim; erros aparecem', async ({ abrir }) => {
  const p = await abrir();
  await sessaoLimpa(p);
  const a = await criarJogador(p, 'Eva');
  await abrirTela(p);
  await p.getByRole('button', { name: 'Abrir sessão' }).click();
  await p.getByRole('button', { name: `Marcar ${a} como presente` }).click();

  const novo = `Fabi ${Math.random().toString(36).slice(2, 7)}`;
  await p.getByLabel('Nome', { exact: true }).fill('Fabi');
  await p.getByLabel('Mulher').check();
  await p.getByRole('button', { name: 'Cadastrar e marcar presente' }).click();
  await expect(p.getByRole('alert')).toContainText('nome e sobrenome');

  await p.getByLabel('Nome', { exact: true }).fill(novo);
  await p.getByRole('button', { name: 'Cadastrar e marcar presente' }).click();
  await expect(presentes(p)).toHaveText([a, novo]);
  await expect(p.locator('ol li').filter({ hasText: novo })).toContainText('nota 60');
});

test('só uma sessão aberta: outra aba vê o estado ao atualizar', async ({ abrir }) => {
  const p = await abrir();
  await sessaoLimpa(p);
  await abrirTela(p);
  const r = await p.request.post('/api/sessao', { headers: CABECALHO });
  expect(r.status()).toBe(201);
  await p.getByRole('button', { name: 'Abrir sessão' }).click();
  await expect(p.getByRole('alert')).toContainText('já existe uma sessão aberta');
  await expect(p.getByRole('heading', { name: /Presentes/ })).toBeVisible();
});

test('tela da sessão sem violações axe', async ({ abrir }) => {
  const p = await abrir({ viewport: { width: 390, height: 844 } });
  await sessaoLimpa(p);
  const a = await criarJogador(p, 'Gabi');
  await abrirTela(p);
  await p.getByRole('button', { name: 'Abrir sessão' }).click();
  await p.getByRole('button', { name: `Marcar ${a} como presente` }).click();
  await p.locator('ol li').first().waitFor();
  expect(await violacoes(p)).toEqual([]);
});

test('home mostra Sessão no navegador e não mostra no APK', async ({ abrir }) => {
  // O axe da Home fica em acessibilidade.spec.js: com quadras ao vivo na lista
  // ele acusa `.contagem` (contraste 4,03:1), defeito anterior a esta história.
  const p = await abrir({ viewport: { width: 360, height: 740 } });
  await p.goto('/');
  await expect(p.getByRole('button', { name: 'Sessão' })).toBeVisible();
  await expect(p.getByRole('button', { name: 'Jogadores' })).toBeVisible();

  const apk = await abrir({}, { fn: () => { window.Capacitor = { isNativePlatform: () => true }; } });
  await apk.goto('/');
  await apk.getByRole('tab', { name: 'Criar placar' }).waitFor();
  await expect(apk.getByRole('button', { name: 'Sessão' })).toHaveCount(0);
  await apk.goto('/sessao');
  await expect(apk.getByRole('heading', { name: 'Sessão', level: 1 })).toHaveCount(0);
});
